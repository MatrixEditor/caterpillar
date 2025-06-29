from typing import Any, Callable, Protocol, Type, TypeVar

from caterpillar.abc import (
    _LengthT,
    _StructLike,
    _ContextLambda,
    _SwitchLike,
)
from caterpillar.byteorder import ByteOrder, Arch
from caterpillar.fields._base import Field

_TemplateModelT = TypeVar("_TemplateModelT")

class _ContainsTemplate(Protocol):
    __template__: TemplateInfo

class TemplateTypeVar:
    name: str
    field_kwds: dict[str, Any]
    def __init__(self, name: str, **field_kwds) -> None: ...
    def __getitem__(self, amount: _LengthT) -> TemplateTypeVar: ...
    def __rshift__(self, switch: dict | _SwitchLike) -> TemplateTypeVar: ...
    def __matmul__(self, offset: int | _ContextLambda) -> TemplateTypeVar: ...
    def __set_byteorder__(self, order: ByteOrder) -> TemplateTypeVar: ...
    def __rsub__(self, bits: int | _ContextLambda) -> TemplateTypeVar: ...
    def __floordiv__(self, condition: _ContextLambda | bool) -> TemplateTypeVar: ...
    def to_field(
        self,
        struct: _StructLike | _ContextLambda,
        arch: Arch | None = None,
        default=...,
    ) -> Field: ...

class TemplateInfo:
    required_tys: dict[str, _StructLike]
    positional_tys: dict[str, _StructLike]
    def is_defined(self, name: str) -> bool: ...
    def add_required(self, name: str) -> None: ...
    def add_positional(self, name: str, default: Any = None) -> None: ...

def istemplate(obj: Any) -> bool: ...
def template(
    *args: str | TemplateTypeVar, **kwargs
) -> Callable[[Type[_TemplateModelT]], Type[_TemplateModelT]]: ...
def get_mangled_name(model_ty: type, annotations: dict[str, Any]) -> str: ...
def derive(
    template_ty: Type[_ContainsTemplate],
    *tys_args,
    partial: bool = False,
    name: str | None = None,
    union: bool = False,
    **tys_kwargs,
) -> type: ...
