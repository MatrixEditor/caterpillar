# pylint: disable=protected-access
# Copyright (C) MatrixEditor 2023-2025
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations

import sys
import inspect
import types
import dataclasses

from typing import Dict, Any
from typing import Union, Self
from typing import Optional
from typing import Callable, TypeVar

from caterpillar.byteorder import ByteOrder, Arch
from caterpillar.abc import _GreedyType, _PrefixedType
from caterpillar.abc import _ContextLambda, _Switch
from caterpillar.abc import _StructLike
from caterpillar.fields import Field, INVALID_DEFAULT
from caterpillar.model import Struct
from caterpillar.options import S_UNION


class TemplateTypeVar:
    """Template type variable.

    These specialised type variables are used within a template definition. They
    support most field operators. Therefore, they can be used in some situations
    where you need to adapt the field type at runtime.

    >>> T = TemplateTypeVar("T")

    Note that there is currently no support for inlined type variables, for example:

    >>> @template(T)
    ... class Foo:
    ...     bar: Enum(Baz, T) # !!! throws an error

    is not possible.
    """

    name: str
    """The bound name of this type variable"""

    field_kwds: Dict[str, Any]
    """Arguments that will be passed to the created field instance."""

    def __init__(self, name: str, **field_kwds) -> None:
        self.name = name
        self.field_kwds = field_kwds or {}

    def __repr__(self) -> str:
        # This method is important for documentation and type hints.
        # We try to illustrate the generic type as good as possible.
        count = self.field_kwds.get("amount")
        if not count:
            return f"~{self.name}"

        # display sequence access brackets
        return f"~{self.name}[{count}]"

    # Now we have to implement all special operators defined in FieldMixin
    def __getitem__(
        self, amount: Union[int, _GreedyType, _PrefixedType, _ContextLambda]
    ) -> TemplateTypeVar:
        return TemplateTypeVar(self.name, amount=amount, **self.field_kwds)

    def __rshift__(self, switch: Union[dict, _Switch]) -> Self:
        return TemplateTypeVar(self.name, options=switch, **self.field_kwds)

    def __matmul__(self, offset: Union[int, _ContextLambda]) -> Self:
        return TemplateTypeVar(self.name, offset=offset, **self.field_kwds)

    def __set_byteorder__(self, order: ByteOrder) -> Self:
        return TemplateTypeVar(self.name, order=order, **self.field_kwds)

    def __rsub__(self, bits: Union[int, _ContextLambda]) -> Self:
        return TemplateTypeVar(self.name, bits=bits, **self.field_kwds)

    # @scheduled_for_removal
    def __floordiv__(self, condition: Union[_ContextLambda, bool]) -> Self:
        return TemplateTypeVar(self.name, condition=condition, **self.field_kwds)

    def to_field(
        self,
        struct: Union[_StructLike, _ContextLambda],
        arch: Optional[Arch] = None,
        default=INVALID_DEFAULT,
    ) -> Field:
        # REVISIT: what about flags?
        return Field(struct, arch=arch, default=default, **self.field_kwds)


def get_caller_module(frame: int = 1) -> str:
    try:
        # Direct call to retrieve the module name
        return sys._getframemodulename(frame) or "__main__"
    except AttributeError:
        # Sometimes the call fails and we have to navigate manually
        try:
            return sys._getframe(frame).f_globals.get("__name__", "__main__")
        except (AttributeError, ValueError):
            # Use inspect module instead
            pass
    try:
        stack = inspect.stack()[frame]
        return stack.frame.f_globals.get("__name__", "__main__")
    except (AttributeError, ValueError) as e:
        raise ModuleNotFoundError("Could not load module from caller!") from e


TEMPLATE_ATTR = "__template__"


@dataclasses.dataclass
class TemplateInfo:
    required_tys: Dict[str, _StructLike]
    positional_tys: Dict[str, _StructLike]

    def is_defined(self, name: str) -> bool:
        return name in list(self.required_tys) + list(self.positional_tys)

    def add_required(self, name: str) -> None:
        if self.is_defined(name):
            raise ValueError(f"Typename {name!r} already defined!")
        self.required_tys[name] = None

    def add_positional(self, name: str, default=None) -> None:
        if self.is_defined(name):
            raise ValueError(f"Typename {name!r} already defined!")
        self.positional_tys[name] = default


def istemplate(obj: Any) -> bool:
    """Return true if the object is a template."""
    return hasattr(obj, TEMPLATE_ATTR)


def template(*args: Union[str, TemplateTypeVar], **kwargs) -> Callable[[type], type]:
    """
    Defines required template type variables if necessary and prepares
    template class definition.

    :return: a wrapper function that will be called with the class instance
    :rtype: Callable[[type], type]
    """
    if len(args) == 0 and len(kwargs) == 0:
        raise ValueError("Template class needs at least one template type var")

    info = TemplateInfo({}, {})
    module = sys.modules[get_caller_module(frame=2)]
    disposable = []
    for value in args:
        var: TemplateTypeVar = None
        match value:
            case str():
                info.add_required(value)
                var = TemplateTypeVar(value)
            case TemplateTypeVar():
                info.add_required(value.name)
                var = value
            case _:
                raise TypeError(f"Invalid typename type: {value!r}")

        # the type variable will be set globally (at least for
        # class creation)
        if not hasattr(module, var.name):
            setattr(module, var.name, var)
            disposable.append(var.name)

    for name, value in kwargs:
        # ellipsis indicates no default value
        if isinstance(value, _GreedyType):
            value = None

        info.add_positional(name, value)
        if not hasattr(module, name):
            setattr(module, name, TemplateTypeVar(name))
            disposable.append(name)

    # the class will get special attributes that identify it as
    # a template class
    def create_template_class(cls) -> type:
        for name in disposable:
            # Only temporary template vars will be removed
            delattr(module, name)
        setattr(cls, TEMPLATE_ATTR, info)
        return cls

    return create_template_class


def get_mangled_name(model_ty: type, annotations: Dict[str, Any]) -> str:
    ty_name = model_ty.__name__
    parts = []
    for name, value in annotations.items():
        parts.append(str(hash(f"{name}{value!r}")))

    hex_name = format(hash("".join(parts)), "X").replace("-", "_")
    return f"_{hex_name}{ty_name}"


def derive(
    template_ty: type, *tys_args, partial=False, name=None, union=False, **tys_kwargs
) -> type:
    """Creates a new struct class based on the given template class.

    :param template_ty: the template class
    :type template_ty: type
    :param partial: whether the resulting class is also a template, defaults to False
    :type partial: bool, optional
    :param name: the new class name, :code:`...` infers the outer variable name, defaults to None
    :type name: str | Ellipsis, optional
    :return: the derived type
    :rtype: type
    """
    if len(tys_args) == 0 and len(tys_kwargs) == 0:
        raise ValueError(
            (
                "To derive a class from a template class at least one "
                "type argument must be given!"
            )
        )
    if not istemplate(template_ty):
        raise TypeError(f"{template_ty.__name__} is not a template class!")

    info: TemplateInfo = getattr(template_ty, TEMPLATE_ATTR)
    if len(tys_args) > len(info.required_tys):
        raise ValueError(
            f"Expected max. {len(info.required_tys)} positional arguments - got {len(tys_args)}!"
        )

    # update necessary parameters
    required_tys = [x for x in info.required_tys if not info.required_tys[x]]
    for arg_name, value in zip(required_tys[: len(tys_args)], tys_args):
        tys_kwargs[arg_name] = value

    # validate against required type parameters
    if not partial:
        for arg_name, value in info.required_tys.items():
            if arg_name not in tys_kwargs and value is None:
                raise ValueError(f"Missing required type argument: {arg_name!r}")

    if isinstance(name, _GreedyType):
        try:
            # Just a hacky way of getting the variable name if possible
            frame = sys._getframe(1)
            context = inspect.getframeinfo(frame).code_context[0]
            if context.count("=") != 0:
                # definition must be <name> = <...>
                parts = context.split(" = ")
                if len(parts) >= 2:
                    name = parts[0]
        except (AttributeError, KeyError, IndexError, TypeError):
            pass

    if name is None:
        name = get_mangled_name(template_ty, tys_kwargs)

    # IF the target module already stores the new type, then return it
    # directly
    module = get_caller_module(2)
    new_ty = getattr(sys.modules[module], name, None)
    if new_ty is None:
        bases = list(template_ty.__bases__)
        for i, base_ty in enumerate(bases):
            if istemplate(base_ty):
                bases[i] = derive(base_ty, *tys_args, *tys_kwargs)

        new_ty = types.new_class(name, template_ty.__bases__, {})

    # prepare annotations
    annotations = inspect.get_annotations(template_ty)
    replaced = {}
    for name, value in annotations.items():
        if isinstance(value, TemplateTypeVar):
            replacement = tys_kwargs.get(value.name)
            if replacement is None:
                replacement = info.positional_tys.get(
                    value.name, info.positional_tys.get(value.name)
                )

            if replacement is None:
                if partial:
                    # missing types will be replaced later on
                    continue

                raise ValueError(
                    f"Could not find type replacement for {value.name!r} at {name!r}"
                )

            if isinstance(replacement, TemplateTypeVar):
                continue

            annotations[name] = value.to_field(
                replacement, default=getattr(template_ty, name, INVALID_DEFAULT)
            )
            replaced[value.name] = replacement

    new_ty.__annotations__ = annotations
    new_ty.__module__ = module
    if not partial:
        new_ty.__struct__ = Struct(new_ty, options={} if not union else {S_UNION})
    else:
        new_info = TemplateInfo(info.required_tys.copy(), info.positional_tys.copy())
        for name, replacement in replaced.items():
            if name in info.required_tys:
                new_info.required_tys[name] = replacement
            elif name in info.positional_tys:
                new_info.positional_tys[name] = replacement
        setattr(new_ty, TEMPLATE_ATTR, new_info)
    return new_ty
