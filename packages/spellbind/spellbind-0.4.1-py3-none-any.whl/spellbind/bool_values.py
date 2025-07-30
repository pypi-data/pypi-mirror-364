from __future__ import annotations

import operator
from abc import ABC
from typing import TypeVar, Generic, overload, TYPE_CHECKING, TypeAlias, Callable, Iterable

from typing_extensions import override

from spellbind.values import Value, OneToOneValue, Constant, SimpleVariable, TwoToOneValue, \
    ManyToSameValue, ThreeToOneValue

if TYPE_CHECKING:
    from spellbind.float_values import FloatValue  # pragma: no cover
    from spellbind.int_values import IntValue  # pragma: no cover
    from spellbind.str_values import StrValue  # pragma: no cover

IntValueLike: TypeAlias = 'IntValue | int'
FloatValueLike: TypeAlias = 'FloatValue | float'
StrValueLike: TypeAlias = 'StrValue | str'
BoolValueLike: TypeAlias = 'BoolValue | bool'

_S = TypeVar('_S')
_T = TypeVar('_T')
_U = TypeVar('_U')
_V = TypeVar('_V')


BoolLike = bool | Value[bool]
IntLike = int | Value[int]
FloatLike = float | Value[float]
StrLike = str | Value[str]


def _select_function(b: bool, t: _S, f: _S) -> _S:
    if b:
        return t
    return f


class BoolValue(Value[bool], ABC):
    @property
    def logical_not(self) -> BoolValue:
        return NotBoolValue(self)

    def __and__(self, other: BoolLike) -> BoolValue:
        return BoolValue.derive_from_many(all, self, other, is_associative=True)

    def __rand__(self, other: bool) -> BoolValue:
        return BoolValue.derive_from_many(all, other, self, is_associative=True)

    def __or__(self, other: BoolLike) -> BoolValue:
        return BoolValue.derive_from_many(any, self, other, is_associative=True)

    def __ror__(self, other: bool) -> BoolValue:
        return BoolValue.derive_from_many(any, other, self, is_associative=True)

    def __xor__(self, other: BoolLike) -> BoolValue:
        return BoolValue.derive_from_two(operator.xor, self, other)

    def __rxor__(self, other: bool) -> BoolValue:
        return BoolValue.derive_from_two(operator.xor, other, self)

    def select_int(self, if_true: IntLike, if_false: IntLike) -> IntValue:
        from spellbind.int_values import IntValue
        return IntValue.derive_from_three(_select_function, self, if_true, if_false)

    def select_float(self, if_true: FloatLike, if_false: FloatLike) -> FloatValue:
        from spellbind.float_values import FloatValue
        return FloatValue.derive_from_three(_select_function, self, if_true, if_false)

    def select_bool(self, if_true: BoolLike, if_false: BoolLike) -> BoolValue:
        return BoolValue.derive_from_three(_select_function, self, if_true, if_false)

    def select_str(self, if_true: StrLike, if_false: StrLike) -> StrValue:
        from spellbind.str_values import StrValue
        return StrValue.derive_from_three(_select_function, self, if_true, if_false)

    @overload
    def select(self, if_true: FloatValueLike, if_false: FloatValueLike) -> FloatValue: ...

    @overload
    def select(self, if_true: StrValueLike, if_false: StrValueLike) -> StrValue: ...

    @overload
    def select(self, if_true: BoolValue, if_false: BoolValue) -> BoolValue: ...

    @overload
    def select(self, if_true: Value[_S] | _S, if_false: Value[_S] | _S) -> Value[_S]: ...

    def select(self, if_true: Value[_S] | _S, if_false: Value[_S] | _S) -> Value[_S]:
        from spellbind.str_values import StrValue
        from spellbind.float_values import FloatValue
        from spellbind.int_values import IntValue

        # suppressing errors, because it seems mypy does not understand the connection between
        # parameter type and return type as it could be inferred from the overloads
        if isinstance(if_true, (FloatValue, float)) and isinstance(if_false, (FloatValue, float)):
            return self.select_float(if_true, if_false)  # type: ignore[return-value]
        elif isinstance(if_true, (StrValue, str)) and isinstance(if_false, (StrValue, str)):
            return self.select_str(if_true, if_false)  # type: ignore[return-value]
        elif isinstance(if_true, (BoolValue, bool)) and isinstance(if_false, (BoolValue, bool)):
            return self.select_bool(if_true, if_false)  # type: ignore[return-value]
        elif isinstance(if_true, (IntValue, int)) and isinstance(if_false, (IntValue, int)):
            return self.select_int(if_true, if_false)  # type: ignore[return-value]
        else:
            return Value.derive_three_value(_select_function, self, if_true, if_false)

    @classmethod
    def derive_from_two(cls, transformer: Callable[[bool, bool], bool],
                        first: BoolLike, second: BoolLike) -> BoolValue:
        return Value.derive_from_two_with_factory(
            transformer,
            first, second,
            create_value=TwoToBoolValue.create,
            create_constant=BoolConstant.of,
        )

    @classmethod
    def derive_from_three(cls, transformer: Callable[[_S, _T, _U], bool],
                          first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> BoolValue:
        return Value.derive_from_three_with_factory(
            transformer,
            first, second, third,
            create_value=ThreeToBoolValue.create,
            create_constant=BoolConstant.of,
        )

    @classmethod
    def derive_from_many(cls, transformer: Callable[[Iterable[bool]], bool], *values: BoolLike, is_associative: bool = False) -> BoolValue:
        return Value.derive_from_many_with_factory(
            transformer,
            *values,
            create_value=ManyBoolToBoolValue.create,
            create_constant=BoolConstant.of,
            is_associative=is_associative,
        )


class OneToBoolValue(OneToOneValue[_S, bool], BoolValue, Generic[_S]):
    pass


class NotBoolValue(OneToOneValue[bool, bool], BoolValue):
    def __init__(self, value: Value[bool]) -> None:
        super().__init__(operator.not_, value)


class ManyBoolToBoolValue(ManyToSameValue[bool], BoolValue):
    @staticmethod
    def create(transformer: Callable[[Iterable[bool]], bool], values: Iterable[BoolLike]) -> BoolValue:
        return ManyBoolToBoolValue(transformer, *values)


class BoolConstant(BoolValue, Constant[bool]):
    @classmethod
    @override
    def of(cls, value: bool) -> BoolConstant:
        if value:
            return TRUE
        return FALSE

    @property
    @override
    def logical_not(self) -> BoolConstant:
        return BoolConstant.of(not self.value)


class BoolVariable(SimpleVariable[bool], BoolValue):
    pass


class ThreeToBoolValue(ThreeToOneValue[_S, _T, _U, bool], BoolValue):
    @staticmethod
    @override
    def create(transformer: Callable[[_S, _T, _U], bool],
               first: _S | Value[_S], second: _T | Value[_T], third: _U | Value[_U]) -> BoolValue:
        return ThreeToBoolValue(transformer, first, second, third)


class TwoToBoolValue(TwoToOneValue[_S, _T, bool], BoolValue):
    @staticmethod
    def create(transformer: Callable[[_S, _T], bool],
               first: _S | Value[_S], second: _T | Value[_T]) -> BoolValue:
        return TwoToBoolValue(transformer, first, second)


TRUE = BoolConstant(True)
FALSE = BoolConstant(False)
