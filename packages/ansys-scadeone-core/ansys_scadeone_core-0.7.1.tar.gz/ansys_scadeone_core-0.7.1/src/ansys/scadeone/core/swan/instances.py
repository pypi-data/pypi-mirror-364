# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module implements operator instances.
"""

from abc import ABC
from enum import Enum, auto
from typing import List, Optional, Union

import ansys.scadeone.core.swan.common as common
import ansys.scadeone.core.swan.scopes as scopes

from .expressions import ClockExpr, Group, GroupItem
from .variable import VarDecl


class OperatorBase(common.SwanItem, ABC):  # numpydoc ignore=PR01  # numpydoc ignore=PR01
    """Base class for: operator ::= prefix_op [[sizes]]."""

    def __init__(self, sizes: List[common.Expression]) -> None:
        common.SwanItem.__init__(self)
        self._sizes = sizes

    @property
    def sizes(self) -> List[common.Expression]:
        """Size parameters of call."""
        return self._sizes


class PathIdOpCall(OperatorBase, common.PragmaBase):  # numpydoc ignore=PR01
    """Call to user-defined operator: operator ::= path_id [[sizes]]."""

    def __init__(
        self,
        path_id: common.PathIdentifier,
        sizes: List[common.Expression],
        pragmas: List[common.Pragma],
    ) -> None:
        OperatorBase.__init__(self, sizes)
        common.PragmaBase.__init__(self, pragmas)
        self._path_id = path_id

    @property
    def path_id(self) -> common.PathIdentifier:
        """Operator path."""
        return self._path_id


class PrefixPrimitiveKind(Enum):
    """Prefix primitive kind: reverse, transpose, pack, and flatten."""

    # pylint disable=invalid-name

    #: **flatten** array operation.
    Flatten = auto()
    #: **pack** array operation.
    Pack = auto()
    #: **reverse** array operation.
    Reverse = auto()
    #: **transpose** array operation.
    Transpose = auto()

    @staticmethod
    def to_str(value: "PrefixPrimitiveKind") -> str:
        return value.name.lower()


class PrefixPrimitive(OperatorBase):  # numpydoc ignore=PR01
    """
    Call to primitive operator: operator ::= *prefix_primitive* [[sizes]]
    with *prefix_primitive*:
    **flatten**,
    **pack**,
    **reverse**,
    operators."""

    def __init__(self, kind: PrefixPrimitiveKind, sizes: List[common.Expression]) -> None:
        super().__init__(sizes)
        self._kind = kind

    @property
    def kind(self) -> PrefixPrimitiveKind:
        """Primitive kind."""
        return self._kind


class Transpose(PrefixPrimitive):  # numpydoc ignore=PR01
    """Transpose operator.

    Parameters are a list of integer, but could be a
    single string if the indices are syntactically incorrect."""

    def __init__(self, params: Union[List[str], str], sizes: List[common.Expression]) -> None:
        super().__init__(PrefixPrimitiveKind.Transpose, sizes)
        self._params = params
        self._is_valid = isinstance(params, list)

    @property
    def params(self) -> Union[List[str], str]:
        """Transpose indices as list of str is transpose indices
        are valid, else the invalid string of indices."""
        return self._params

    @property
    def is_valid(self) -> bool:
        """True when indices are a valid list, else one has a string."""
        return self._is_valid


class OperatorExpression(common.SwanItem, ABC):  # numpydoc ignore=PR01
    """Base class for *op_expr*."""

    def __init__(self) -> None:
        common.SwanItem.__init__(self)


class PrefixOperatorExpression(OperatorBase):  # numpydoc ignore=PR01
    """Call to *op_expr*: operator ::= (*op_expr*) [[sizes]]."""

    def __init__(self, op_expr: OperatorExpression, sizes: List[common.Expression]) -> None:
        super().__init__(sizes)
        self._op_expr = op_expr
        self._is_text = False
        self._is_op_expr = False

    @property
    def op_expr(self) -> OperatorExpression:
        """Operator expression."""
        return self._op_expr

    @property
    def is_text(self) -> bool:
        """Return True if *op_expr* is read from {text% ...%text}."""
        return self._is_text

    @is_text.setter
    def is_text(self, is_text: bool):
        self._is_text = is_text

    @property
    def is_op_expr(self) -> bool:
        """Return True if *op_expr* is read from {op_expr% ...%op_expr}."""
        return self._is_op_expr

    @is_op_expr.setter
    def is_op_expr(self, is_op_expr: bool):
        self._is_op_expr = is_op_expr


class IteratorKind(Enum):
    """Iterators kind: map, fold, mapfold, mapi, foldi, mapfoldi."""

    # pylint disable=invalid-name,no-else-return

    #: **map** iterator.
    Map = auto()
    #: **fold** iterator.
    Fold = auto()
    #: **mapfold** iterator.
    Mapfold = auto()
    #: **mapi** iterator.
    Mapi = auto()
    #: **foldi** iterator.
    Foldi = auto()
    #: **mapfoldi** iterator.
    Mapfoldi = auto()

    @staticmethod
    def to_str(value: "IteratorKind") -> str:
        if value == IteratorKind.Map:
            return "map"
        elif value == IteratorKind.Fold:
            return "fold"
        elif value == IteratorKind.Mapfold:
            return "mapfold"
        elif value == IteratorKind.Mapi:
            return "mapi"
        elif value == IteratorKind.Foldi:
            return "foldi"
        elif value == IteratorKind.Mapfoldi:
            return "mapfoldi"


class Iterator(OperatorExpression):  # numpydoc ignore=PR01
    """Iterators: map, fold, mapfold, mapi, foldi, mapfoldi."""

    def __init__(self, kind: IteratorKind, operator: OperatorBase) -> None:
        super().__init__()
        self._kind = kind
        self._operator = operator

    @property
    def kind(self) -> IteratorKind:
        """Iterator kind."""
        return self._kind

    @property
    def operator(self) -> OperatorBase:
        """Iterated operator."""
        return self._operator


class ActivateClock(OperatorExpression):  # numpydoc ignore=PR01
    """**activate** *operator* **every** *clock_expr*"""

    def __init__(self, operator: OperatorBase, clock: ClockExpr) -> None:
        super().__init__()
        self._operator = operator
        self._clock = clock

    @property
    def operator(self) -> OperatorBase:
        """Operator under activation"""
        return self._operator

    @property
    def clock(self) -> ClockExpr:
        """Activation clock expression"""
        return self._clock


class ActivateEvery(OperatorExpression):  # numpydoc ignore=PR01
    """Higher-order activate expression: **activate** *operator*
    **every** *expr* (( **last**| **default** )) *expr*."""

    def __init__(
        self,
        operator: OperatorBase,
        condition: common.Expression,
        is_last: bool,
        expr: common.Expression,
    ) -> None:
        super().__init__()
        self._operator = operator
        self._condition = condition
        self._is_last = is_last
        self._expr = expr

    @property
    def operator(self) -> OperatorBase:
        """Operator under activation."""
        return self._operator

    @property
    def condition(self) -> common.Expression:
        """Activation condition."""
        return self._condition

    @property
    def is_last(self) -> bool:
        """Returns true when **last** is set, false when **default** is set."""
        return self._is_last

    @property
    def expr(self) -> common.Expression:
        """Activation default/last expression."""
        return self._expr


class Restart(OperatorExpression):  # numpydoc ignore=PR01
    """Higher-order restart expression: **restart** *operator* **every** *expr*."""

    def __init__(self, operator: OperatorBase, condition: common.Expression) -> None:
        super().__init__()
        self._operator = operator
        self._condition = condition

    @property
    def operator(self) -> OperatorBase:
        """Operator under activation."""
        return self._operator

    @property
    def condition(self) -> common.Expression:
        """Activation condition."""
        return self._condition


class OptGroupItem(common.SwanItem):  # numpydoc ignore=PR01
    """Optional group item: *opt_group_item* ::= _ | *group_item*."""

    def __init__(self, item: Optional[GroupItem] = None) -> None:
        super().__init__()
        self._item = item

    @property
    def is_underscore(self) -> bool:
        """True when group item is '_'."""
        return self._item is None

    @property
    def item(self) -> Union[GroupItem, None]:
        """Returns the group item, either a GroupItem or None."""
        return self._item


class Partial(OperatorExpression):  # numpydoc ignore=PR01
    r"Partial operator expression: *operator* \ *partial_group*."

    def __init__(self, operator: OperatorBase, partial_group: List[OptGroupItem]) -> None:
        super().__init__()
        self._operator = operator
        self._partial_group = partial_group

    @property
    def operator(self) -> OperatorBase:
        """Called operator."""
        return self._operator

    @property
    def partial_group(self) -> List[OptGroupItem]:
        """Returns the partial group items."""
        return self._partial_group


class NaryOp(Enum):
    """N-ary operators."""

    # pylint disable=invalid-name,no-else-return
    #: (+) N-ary addition.
    Plus = auto()
    #: (*) N-ary multiplication.
    Mult = auto()
    #: (**land**) N-ary bitwise and.
    Land = auto()
    #: (**lor**) N-ary bitwise or.
    Lor = auto()
    #: (**and**) N-ary logical and.
    And = auto()
    #: (**or**) N-ary logical or.
    Or = auto()
    #: (**xor**) N-ary exclusive or.
    Xor = auto()
    #: (**@**) N-ary array concat.
    Concat = auto()

    @staticmethod
    def to_str(value: "NaryOp"):
        if value == NaryOp.Plus:
            return "+"
        elif value == NaryOp.Mult:
            return "*"
        elif value == NaryOp.Land:
            return "land"
        elif value == NaryOp.Lor:
            return "lor"
        elif value == NaryOp.And:
            return "and"
        elif value == NaryOp.Or:
            return "or"
        elif value == NaryOp.Xor:
            return "xor"
        elif value == NaryOp.Concat:
            return "@"


class NAryOperator(OperatorExpression):  # numpydoc ignore=PR01
    """N-ary operators: '+' | '*' | '@' | **and** | **or** | **xor** | **land** | **lor**."""

    def __init__(self, operator: NaryOp) -> None:
        super().__init__()
        self._operator = operator

    @property
    def operator(self) -> NaryOp:
        """N-ary operator."""
        return self._operator


class AnonymousOperatorWithExpression(OperatorExpression):  # numpydoc ignore=PR01
    """Anonymous operator expression:
    ((**node|function**)) id {{ , id }} *scope_sections* => *expr*."""

    def __init__(
        self,
        is_node: bool,
        params: List[common.Identifier],
        sections: List[scopes.ScopeSection],
        expr: common.Expression,
    ) -> None:
        super().__init__()
        self._is_node = is_node
        self._params = params
        self._sections = sections
        self._expr = expr

    @property
    def is_node(self) -> bool:
        """True when anonymous operator is a node, else a function."""
        return self._is_node

    @property
    def params(self) -> List[common.Identifier]:
        """Anonymous operator parameters list."""
        return self._params

    @property
    def sections(self) -> List[scopes.ScopeSection]:
        """Scope sections list."""
        return self._sections

    @property
    def expr(self) -> common.Expression:
        """Anonymous operator body."""
        return self._expr


class AnonymousOperatorWithDataDefinition(OperatorExpression):  # numpydoc ignore=PR01
    """Anonymous operator expression:
    ((**node|function**)) *params* **returns** *params* *data_def*."""

    def __init__(
        self,
        is_node: bool,
        inputs: List[VarDecl],
        outputs: List[VarDecl],
        data_def: Union[common.Equation, scopes.Scope],
    ) -> None:
        super().__init__()
        self._is_node = is_node
        self._inputs = inputs
        self._outputs = outputs
        self._data_def = data_def

    @property
    def is_node(self) -> bool:
        """True when anonymous operator is a node, else a function."""
        return self._is_node

    @property
    def inputs(self) -> List[VarDecl]:
        """Anonymous operator input list."""
        return self._inputs

    @property
    def outputs(self) -> List[VarDecl]:
        """Anonymous operator output list."""
        return self._outputs

    @property
    def data_def(self) -> Union[common.Equation, scopes.Scope]:
        """Anonymous operator data definition, either an equation or a scope."""
        return self._data_def


class OperatorInstance(common.Expression):  # numpydoc ignore=PR01
    """Operator instance call:

    *expr* := *operator_instance* ( *group* )

    *operator_instance* ::= *operator* [[ luid ]]"""

    def __init__(
        self, operator: OperatorBase, params: Group, luid: Optional[common.Luid] = None
    ) -> None:
        super().__init__()
        self._operator = operator
        self._params = params
        self._luid = luid

    @property
    def operator(self) -> OperatorBase:
        """Called operator."""
        return self._operator

    @property
    def params(self) -> Group:
        """Call parameters."""
        return self._params

    @property
    def luid(self) -> Union[common.Luid, None]:
        """Optional luid."""
        return self._luid


# =============================================
# Protected Items
# =============================================


class ProtectedOpExpr(OperatorExpression, common.ProtectedItem):  # numpydoc ignore=PR01
    """Protected operator expression,
    i.e., saved as string if syntactically incorrect."""

    def __init__(self, data: str, markup: str) -> None:
        common.ProtectedItem.__init__(self, data, markup)
