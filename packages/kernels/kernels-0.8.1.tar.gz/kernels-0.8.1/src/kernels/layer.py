from __future__ import annotations

import functools
import inspect
import logging
import os
import sys
import warnings
from abc import ABC, abstractmethod
from contextvars import ContextVar
from copy import deepcopy
from dataclasses import dataclass
from enum import Flag, auto
from functools import lru_cache
from pathlib import Path
from types import MethodType
from typing import (
    TYPE_CHECKING,
    Dict,
    Optional,
    Protocol,
    Tuple,
    Type,
    Union,
)

from ._interval_tree import IntervalTree
from ._versions import select_revision_or_version
from .utils import _get_caller_locked_kernel, _get_locked_kernel, get_kernel

if TYPE_CHECKING:
    import torch
    from torch import nn


_DISABLE_KERNEL_MAPPING: bool = bool(int(os.environ.get("DISABLE_KERNEL_MAPPING", "0")))


class Mode(Flag):
    """
    Kernelize mode

    The `Mode` flag is used by `kernelize` to select kernels for the given
    mode. Mappings can be registered for specific modes.

    * `INFERENCE`: The kernel is used for inference.
    * `TRAINING`: The kernel is used for training.
    * `TORCH_COMPILE`: The kernel is used with `torch.compile`.
    * `FALLBACK`: In a kernel mapping, this kernel is used when no other mode
       matches.

    Different modes can be combined. For instance, `INFERENCE | TORCH_COMPILE`
    should be used for layers that are used for inference *with* `torch.compile`.
    """

    _NONE = 0
    FALLBACK = auto()
    TRAINING = auto()
    INFERENCE = auto()
    TORCH_COMPILE = auto()

    def __or__(self, other: Mode) -> Mode:
        union = super().__or__(other)

        if Mode.INFERENCE in union and Mode.TRAINING in union:
            raise ValueError("Mode.INFERENCE and Mode.TRAINING are mutually exclusive.")

        if Mode.FALLBACK in union and union != Mode.FALLBACK:
            raise ValueError("Mode.FALLBACK cannot be combined with other modes.")

        return union


@dataclass(frozen=True)
class Device:
    type: str
    properties: Optional[CUDAProperties] = None

    def __post_init__(self):
        if self.properties is not None and isinstance(self.properties, CUDAProperties):
            if self.type != "cuda":
                raise ValueError("CUDAProperties is only supported for 'cuda' devices.")

    def create_repo(self) -> _DeviceRepos:
        """Create an appropriate repository set for this device type."""
        if self.type == "cuda":
            return _CUDARepos()
        elif self.type == "mps":
            return _MPSRepos()
        else:
            raise ValueError(f"Unknown device type: {self.type}")

    def __eq__(self, other):
        if not isinstance(other, Device):
            return NotImplemented
        return self.type == other.type and self.properties == other.properties

    def __hash__(self):
        return hash((self.type, self.properties))


@dataclass(frozen=True)
class CUDAProperties:
    min_capability: int
    max_capability: int

    def __eq__(self, other):
        if not isinstance(other, CUDAProperties):
            return NotImplemented
        return (
            self.min_capability == other.min_capability
            and self.max_capability == other.max_capability
        )

    def __hash__(self):
        return hash((self.min_capability, self.max_capability))


class LayerRepositoryProtocol(Protocol):
    @property
    def layer_name(self) -> str: ...

    @property
    def repo_id(self) -> str: ...

    @property
    def revision(self) -> str: ...


class LayerRepository:
    """
    Repository and name of a layer.
    """

    def __init__(
        self,
        repo_id: str,
        *,
        layer_name: str,
        revision: Optional[str] = None,
        version: Optional[str] = None,
    ):
        """
        Construct a layer repository.

        Args:
            repo_id (`str`): The Hub repository containing the layer.
            revision (`str`, *optional*, defaults to `"main"`): The specific
                revision (branch, tag, or commit) to download.
                Cannot be used together with `version`.
            version (`str`, *optional*): The kernel version to download. This
                can be a Python version specifier, such as `">=1.0.0,<2.0.0"`.
                Cannot be used together with `revision`.
        """

        if revision is not None and version is not None:
            raise ValueError(
                "Either a revision or a version must be specified, not both."
            )

        self.repo_id = repo_id
        self.layer_name = layer_name

        # We are going to resolve these lazily, since we do not want
        # to do a network request for every registered LayerRepository.
        self._revision = revision
        self._version = version

    @property
    @functools.lru_cache()
    def revision(self) -> str:
        return select_revision_or_version(
            repo_id=self.repo_id, revision=self._revision, version=self._version
        )

    def __eq__(self, other):
        return (
            isinstance(other, LayerRepository)
            and self.layer_name == other.layer_name
            and self.repo_id == other.repo_id
            and self._revision == other._revision
            and self._version == other._version
        )

    def __hash__(self):
        return hash((self.layer_name, self.repo_id, self._revision, self._version))


class LockedLayerRepository:
    """
    Repository and name of a layer.

    In contrast to `LayerRepository`, this class uses repositories that
    are locked inside a project.
    """

    def __init__(
        self,
        repo_id: str,
        *,
        lockfile: Optional[Path] = None,
        layer_name: str,
    ):
        """
        Construct a layer repository.

        Args:
            repo_id (`str`): The Hub repository containing the layer.
        """
        self.repo_id = repo_id
        self.lockfile = lockfile
        self.layer_name = layer_name

    @property
    @functools.lru_cache()
    def revision(self) -> str:
        if self.lockfile is None:
            locked_sha = _get_caller_locked_kernel(self.repo_id)
        else:
            with open(self.lockfile, "r") as f:
                locked_sha = _get_locked_kernel(self.repo_id, f.read())

        if locked_sha is None:
            raise ValueError(f"Kernel `{self.repo_id}` is not locked")

        return locked_sha

    def __eq__(self, other):
        return (
            isinstance(other, LockedLayerRepository)
            and self.layer_name == other.layer_name
            and self.repo_id == other.repo_id
        )

    def __hash__(self):
        return hash((self.layer_name, self.repo_id))


_CACHED_LAYER: Dict[LayerRepositoryProtocol, Type["nn.Module"]] = {}


class _DeviceRepos(ABC):
    """
    Device-specific kernel layer repositories.
    """

    @property
    @abstractmethod
    def repos(
        self,
    ) -> Optional[Dict[Mode, LayerRepositoryProtocol]]: ...

    @abstractmethod
    def insert(self, device: Device, repos: Dict[Mode, LayerRepositoryProtocol]):
        """
        Insert a repository for a specific device and mode.
        """
        ...


class _MPSRepos(_DeviceRepos):
    _repos: Dict[Mode, LayerRepositoryProtocol]

    def __init__(self):
        super().__init__()
        self._repos = {}

    @property
    def repos(
        self,
    ) -> Optional[Dict[Mode, LayerRepositoryProtocol]]:
        return self._repos

    def insert(self, device: Device, repos: Dict[Mode, LayerRepositoryProtocol]):
        if device.type != "mps":
            raise ValueError(f"Device type must be 'mps', got {device.type}")

        self._repos = repos


class _CUDARepos(_DeviceRepos):
    _repos: IntervalTree[Dict[Mode, LayerRepositoryProtocol]]

    def __init__(self):
        super().__init__()
        self.repos_by_capability = IntervalTree()

    @property
    def repos(
        self,
    ) -> Optional[Dict[Mode, LayerRepositoryProtocol]]:
        capability = _find_capability()
        return self.repos_by_capability.find_smallest_interval(capability)

    def insert(self, device: Device, repos: Dict[Mode, LayerRepositoryProtocol]):
        assert device.properties is None or isinstance(
            device.properties, CUDAProperties
        )

        min_capability = (
            0 if device.properties is None else device.properties.min_capability
        )
        max_capability = (
            sys.maxsize
            if device.properties is None
            else device.properties.max_capability
        )

        self.repos_by_capability.insert(min_capability, max_capability, repos)


_KERNEL_MAPPING: ContextVar[Dict[str, Dict[str, _DeviceRepos]]] = ContextVar(
    "_KERNEL_MAPPING", default={}
)


def use_kernel_mapping(
    mapping: Dict[
        str,
        Dict[
            Union[Device, str],
            Union[LayerRepositoryProtocol, Dict[Mode, LayerRepositoryProtocol]],
        ],
    ],
    *,
    inherit_mapping: bool = True,
):
    """
    Context manager that sets a mapping for a duration of the context.

    When `inherit_mapping` is set to `True` the current mapping will be
    extended by `mapping` inside the context. If it is `False`, only
    `mapping` is used inside the context.
    """

    class ContextManager:
        def __enter__(self):
            # Mappings always stack on previous mappings.
            if inherit_mapping:
                self.token = _KERNEL_MAPPING.set(deepcopy(_KERNEL_MAPPING.get()))
            else:
                self.token = _KERNEL_MAPPING.set({})
            register_kernel_mapping(mapping)

        def __exit__(self, exc_type, exc_value, traceback):
            _KERNEL_MAPPING.reset(self.token)

    return ContextManager()


def register_kernel_mapping(
    mapping: Dict[
        str,
        Dict[
            Union[Device, str],
            Union[LayerRepositoryProtocol, Dict[Mode, LayerRepositoryProtocol]],
        ],
    ],
):
    """
    Allows one to register a mapping between a layer name and the corresponding
    kernel(s) to use, depending on the device. This should be used in conjunction
    with `kernelize`.

    Example usage:

    ```python
    from kernels import LayerRepository, register_kernel_mapping

    kernel_layer_mapping = {
      "LlamaRMSNorm": {
          "cuda": LayerRepository(
              repo_id="kernels-community/activation",
              layer_name="RmsNorm",
              revision="layers",
          ),
      },
    }
    register_kernel_mapping(kernel_layer_mapping)
    ```
    """
    # Merge with existing mappings.
    for new_kernel, new_device_repos in mapping.items():
        device_repo = _KERNEL_MAPPING.get().setdefault(new_kernel, {})
        for new_device, new_repo in new_device_repos.items():
            device = (
                Device(type=new_device) if isinstance(new_device, str) else new_device
            )

            if isinstance(new_repo, dict):
                kernel_options = new_repo
            else:
                kernel_options = {Mode.FALLBACK: new_repo}

            feature_repos = device_repo.setdefault(device.type, device.create_repo())
            feature_repos.insert(device, kernel_options)


def replace_kernel_forward_from_hub(
    cls,
    layer_name: str,
):
    """
    Decorator that prepares a layer class to use a kernel from the Hugging Face Hub.

    This decorator stores the layer name and original forward method, which will be used
    by the kernelize function to replace the forward implementation with the appropriate
    kernel from the hub.

    Args:
        cls: The layer class to decorate
        layer_name: The name of the layer to use for kernel lookup
    """
    cls.kernel_layer_name = layer_name


_MODE_FALLBACK_PRIORITY = {
    Mode.INFERENCE: [
        Mode.INFERENCE,
        Mode.INFERENCE | Mode.TORCH_COMPILE,
        Mode.TRAINING,
        Mode.TRAINING | Mode.TORCH_COMPILE,
        Mode.FALLBACK,
    ],
    Mode.TRAINING: [
        Mode.TRAINING,
        Mode.TRAINING | Mode.TORCH_COMPILE,
        Mode.FALLBACK,
    ],
    Mode.INFERENCE
    | Mode.TORCH_COMPILE: [
        Mode.INFERENCE | Mode.TORCH_COMPILE,
        Mode.TRAINING | Mode.TORCH_COMPILE,
        Mode.FALLBACK,
    ],
    Mode.TRAINING
    | Mode.TORCH_COMPILE: [
        Mode.TRAINING | Mode.TORCH_COMPILE,
        Mode.FALLBACK,
    ],
}


def _select_repository(
    repositories: Dict[Mode, LayerRepositoryProtocol],
    *,
    mode: Mode,
) -> Optional[Tuple[LayerRepositoryProtocol, Mode]]:
    # Get the fallback priority list for the requested mode
    if mode not in _MODE_FALLBACK_PRIORITY:
        raise ValueError(f"Unsupported mode: {mode}")

    fallback_modes = _MODE_FALLBACK_PRIORITY[mode]

    # Try each mode in priority order
    for fallback_mode in fallback_modes:
        if fallback_mode in repositories:
            return (repositories[fallback_mode], fallback_mode)

    return None


def kernelize(
    model: "nn.Module",
    *,
    mode: Mode = Mode.TRAINING | Mode.TORCH_COMPILE,
    device: Optional[Union[str, "torch.device"]] = None,
    use_fallback: bool = True,
):
    """
    Iterate over all modules in the model and replace the `forward` method of
    extensible layers for which kernels are registered using `register_kernel_mapping`
    or `use_kernel_mapping`.

    Args:
        model: The PyTorch model to kernelize
        mode: the mode that the kernel is going to be used in (e.g.
            `Mode.TRAINING | Mode.TORCH_COMPILE` kernelizes the model for training
            and `torch.compile`).
        device: The device type to load kernels for. The device type will be inferred
            from the parameters of the model when not provided.
        use_fallback: Whether to use the original forward method of modules when no
            compatible kernel could be found. If set to `False`, an exception will
            be raised in such cases.

    Returns:
        The kernelized model
    """
    import torch

    if mode == Mode.FALLBACK:
        raise ValueError("Mode.FALLBACK can only be used to register kernel mappings.")

    # Type check ignored because this causes a false negative on Python < 3.11.
    # Looks similar to: https://github.com/python/mypy/issues/9642
    # Remove once we start doing typing checks on >= 3.11.
    if Mode.INFERENCE not in mode and Mode.TRAINING not in mode:  # type: ignore[operator]
        raise ValueError("kernelize mode must contain Mode.INFERENCE or Mode.TRAINING.")

    if device is None:
        device_type = _find_device(model)
    elif isinstance(device, str):
        device_type = Device(type=torch.device(device).type)
    else:
        device_type = Device(device.type)

    assert isinstance(device_type, Device)

    for _, module in model.named_modules():
        module_class = type(module)
        if not hasattr(module_class, "kernel_layer_name"):
            continue
        layer_name = module_class.kernel_layer_name

        if _DISABLE_KERNEL_MAPPING:
            _replace_forward(module, module_class)
            continue

        kernel = _KERNEL_MAPPING.get().get(str(layer_name))

        if kernel is None:
            warnings.warn(
                "\n"
                f"No kernel mapping found for layer `{layer_name}`. "
                f"Check if the layer name matches one of the kernels in the mapping or add the kernel "
                f"you want to use to the mapping. Defaulting to original forward implementation."
            )
            if not use_fallback:
                raise ValueError(f"No layer mapping for `{layer_name}`")
            _replace_forward(module, module_class)
            continue

        # Get kernel options for the device
        property_repos = kernel.get(device_type.type)

        if property_repos is None:
            if not use_fallback:
                raise ValueError(
                    f"No layer mapping for `{layer_name}` with device type `{device_type}`"
                )
            _replace_forward(module, module_class)
            continue

        repos = property_repos.repos

        if repos is None:
            if not use_fallback:
                raise ValueError(
                    f"No layer mapping for `{layer_name}` device `{device_type}` with the right properties"
                )
            _replace_forward(module, module_class)
            continue

        repo_with_mode = _select_repository(
            repos,
            mode=mode,
        )

        if repo_with_mode is None:
            if not use_fallback:
                raise ValueError(
                    f"No repository for `{layer_name}` for configuration mode={mode}"
                )
            _replace_forward(module, module_class)
            continue

        repo, repo_mode = repo_with_mode

        logging.info(
            f"Using layer `{repo.layer_name}` from repo `{repo.repo_id}` (revision: {repo.revision}) for layer `{layer_name}`"
        )
        logging.debug(f"kernelize mode: {mode}, repo mode: {repo_mode}")

        layer = _get_layer_memoize(repo, module_class)

        # Ideally we would do validation on the mapping where we check that
        # e.g. if a repo class is registered for TRAINING | TORCH_COMPILE,
        # the actual layer is compatible with that. Unfortunately, this would
        # mean that we have to pre-download everything.
        _validate_layer_has_mode(
            layer_name=layer_name, module=layer, repo=repo, repo_mode=repo_mode
        )

        _conditionally_replace_forward(
            module=module,
            layer=layer,
            mode=mode,
            use_fallback=use_fallback,
        )

    return model


def use_kernel_forward_from_hub(layer_name: str):
    """
    Make a layer extensible using the name `layer_name`.
    """

    def decorator(cls):
        replace_kernel_forward_from_hub(cls, layer_name)
        return cls

    return decorator


def _get_kernel_layer(
    *, repo_id: str, layer_name: str, revision: str
) -> Type["nn.Module"]:
    """Get a layer from a kernel."""

    kernel = get_kernel(repo_id, revision=revision)

    if getattr(kernel, "layers", None) is None:
        raise ValueError(
            f"Kernel `{repo_id}` at revision `{revision}` does not define any layers."
        )

    layer = getattr(kernel.layers, layer_name, None)
    if layer is None:
        raise ValueError(f"Layer `{layer_name}` not found in kernel `{repo_id}`.")
    return layer


def _validate_layer(*, check_cls, cls):
    import torch.nn as nn

    # The layer must have at least have the following properties: (1) it
    # must be stateless; (2) the forward signature should correspond to
    # the signature it is replacing; (3) forward should not call other
    # methods.

    if not issubclass(cls, nn.Module):
        raise TypeError(f"Layer `{cls}` is not a Torch layer.")

    # We verify statelessness by checking that the does not have its own
    # constructor (since the constructor could add member variables)...
    if cls.__init__ is not nn.Module.__init__:
        raise TypeError("Layer must not override nn.Module constructor.")

    # ... or predefined member variables.
    torch_module_members = {name for name, _ in inspect.getmembers(nn.Module)}
    cls_members = {name for name, _ in inspect.getmembers(cls)}
    difference = cls_members - torch_module_members
    # verify if : difference ⊄ {"can_torch_compile", "has_backward"}
    if not difference <= {"can_torch_compile", "has_backward"}:
        raise TypeError("Layer must not contain additional members.")

    # Check whether the forward signatures are similar.
    params = inspect.signature(cls.forward).parameters
    ref_params = inspect.signature(check_cls.forward).parameters

    if len(params) != len(ref_params):
        raise TypeError(
            "Forward signature does not match: different number of arguments."
        )

    for param, ref_param in zip(params.values(), ref_params.values()):
        if param.kind != ref_param.kind:
            raise TypeError(
                f"Forward signature does not match: different kind of arguments ({param} ({param.kind}) and {ref_param} ({ref_param.kind})"
            )


def _find_device(model: "nn.Module") -> Device:
    try:
        param = next(model.parameters())
    except StopIteration:
        raise ValueError(
            "Cannot determine model device, provide as `device` argument to `kernelize`."
        )

    return Device(type=param.device.type)


@lru_cache
def _find_capability() -> int:
    import torch

    major, minor = torch.cuda.get_device_capability(device=None)
    return major * 10 + minor


def _conditionally_replace_forward(
    *,
    module: "nn.Module",
    layer: Type["nn.Module"],
    mode: Mode,
    use_fallback: bool,
):
    module_class = type(module)

    # Switch to fallback if the mode is not supported by the layer.
    # Note that this is useful even after _validate_layer_has_mode because
    # layers registered with the FALLBACK mode never get rejected by
    # _validate_layer_has_mode. For such layers, we want to fall back in
    # case the layer does not support the given mode.
    needs_fallback = Mode.TORCH_COMPILE in mode and not getattr(
        layer, "can_torch_compile", False
    )
    needs_fallback |= Mode.TRAINING in mode and not getattr(layer, "has_backward", True)

    if needs_fallback:
        if use_fallback:
            _replace_forward(module, module_class)
        else:
            raise ValueError(f"Available kernel does not support mode: {mode}")
    else:
        _replace_forward(module, layer)


def _replace_forward(module: "nn.Module", layer: Type["nn.Module"]):
    module.forward = MethodType(layer.forward, module)  # type: ignore[method-assign]


def _validate_layer_has_mode(
    *,
    layer_name: str,
    module: Type["nn.Module"],
    repo: LayerRepositoryProtocol,
    repo_mode: Mode,
):
    """
    Check that a repository supports the mode that it was registered for.
    """

    if Mode.TRAINING in repo_mode and not getattr(module, "has_backward", True):
        raise ValueError(
            f"Layer `{repo.layer_name}` ({repo.repo_id}, revision: {repo.revision}) does not support backward.\n"
            f"Was registered for `{layer_name}` with mode `{repo_mode}`"
        )

    if Mode.TORCH_COMPILE in repo_mode and not getattr(
        module, "can_torch_compile", False
    ):
        raise ValueError(
            f"Layer `{repo.layer_name}` ({repo.repo_id}, revision: {repo.revision}) does not support torch.compile.\n"
            f"Was registered for `{layer_name}` with mode `{repo_mode}`"
        )

    return True


def _get_layer_memoize(
    repo: LayerRepositoryProtocol, module_class: Type["nn.Module"]
) -> Type["nn.Module"]:
    layer = _CACHED_LAYER.get(repo, None)
    if layer is not None:
        return layer

    layer = _get_kernel_layer(
        repo_id=repo.repo_id,
        layer_name=repo.layer_name,
        revision=repo.revision,
    )
    _validate_layer(check_cls=module_class, cls=layer)
    _CACHED_LAYER[repo] = layer

    return layer
