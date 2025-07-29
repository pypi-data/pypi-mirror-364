# 2025/07/22
"""
each.py - Apply operations to each item.

Defines both function `each` and class `EachContainer`. Instances of
`EachContainer` delegate all operations performed on the to the items that
compose them. For example:

    x = EachContainer([1, 2, 3])
    x += 1
    print(x)  # Output: EachContainer([2, 3, 4])

Function `each` is a convenience function that creates an `EachContainer` in
different ways. This should be the preferred way to create an `EachContainer`.

A special exception `EachError` is raised when an operation cannot be applied
to a specific item in the container, providing information about the operation
performed, the type of the item, and its position in the container. This
exception will always be raised from the one that caused the error, so that the
context of the error is preserved.

"""
from __future__ import annotations

import operator
import sys
from typing import Any, Callable, Iterable


class EachError(Exception):
    """Custom exception for `each` operations"""

    def __init__(
        self,
        position: int,
        obj_type: type[Any],
        fun_name: str,
        fun_symbol: str | None = None,
        fun_args: tuple[Any, ...] = (),
        fun_kwargs: dict[str, Any] | None = None,
    ) -> None:
        s_args = ", ".join(f"{arg!r}" for arg in fun_args)
        s_kwargs = ", ".join(f"{k}={v!r}" for k, v in (fun_kwargs or {}).items())
        base = f"Object of {obj_type} at position {position} raised an error while performing "

        if fun_symbol:
            base += f"'obj {fun_symbol} {fun_args[0]}'"
        elif fun_name == "call":
            base += f"'obj({s_args}, {s_kwargs})'"
        else:
            base += f"'{fun_name}(obj, {s_args}, {s_kwargs})'"

        super().__init__(base.replace("(,", "(").replace(", )", ")").strip())


class EachContainer:
    """Class that contains a list of objects and applies every operation to
    each of them.

    Inner list of objects is accessible through the `list` attribute.

    Constructor requires an iterable, which will be converted to said list.
    If the iterable is empty, the list will be empty as well.

    """

    def __init__(self, iterable: Iterable[Any]) -> None:
        super().__setattr__("list", list(iterable))

    # Internal

    def __apply(
        self,
        fun_name: str,
        fun: Callable | None = None,
        fun_symbol: str | None = None,
        inplace: bool = False,  # For in-place operations
        swapped: bool = False,  # For reflected operations
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
    ) -> EachContainer[Any] | None:
        """Internal method that actually performs most operations."""
        kwargs = kwargs or {}
        xlen = len(self.list)

        # If function is None, get it from the 'operator' module
        fun = fun or getattr(operator, fun_name)

        # Convert arguments to the appropriate shape
        args_aux = []
        for arg in args:
            if isinstance(arg, EachContainer):
                if xlen != len(arg.list):
                    raise ValueError(
                        "EachContainer used as arguments must have the same"
                        " length as the EachContainer being operated on."
                    )
                arg = arg.list
            else:
                arg = [arg for _ in range(xlen)]
            args_aux.append(arg)
        args_list = [list(arg) for arg in zip(*args_aux)]
        args_list = args_list or [() for _ in range(xlen)]

        kwargs_aux = {}
        for key, value in kwargs.items():
            if isinstance(value, EachContainer):
                if xlen != len(value.list):
                    raise ValueError(
                        "EachContainer used as arguments must have the same"
                        " length as the EachContainer being operated on."
                    )
                value = value.list
            else:
                value = [value for _ in range(xlen)]
            kwargs_aux[key] = value
        kwargs_list = [{} for _ in range(xlen)]
        for i in range(xlen):
            kwargs_list[i] = {key: value[i] for key, value in kwargs_aux.items()}

        # Apply the function to each element
        if inplace:
            res = self.list
        else:
            res = [None for _ in range(xlen)]
        try:
            for i in range(xlen):
                if swapped:
                    res[i] = fun(*args_list[i], self.list[i], **kwargs_list[i])
                else:
                    res[i] = fun(self.list[i], *args_list[i], **kwargs_list[i])
        except Exception as err:
            raise EachError(
                i,
                type(self.list[i]),
                fun_name,
                fun_symbol,
                args_list[i],
                kwargs_list[i],
            ) from err

        # Convert to EachContainer and return (if not inplace)
        if not inplace:
            return EachContainer(res)
        return self

    # Representation

    def __repr__(self) -> str:
        return f"each({self.list})"

    def __str__(self) -> str:
        res = self.__apply("str", fun=str)
        return "[" + ", ".join(res.list) + "]"

    def __bytes__(self) -> bytes:
        res = self.__apply("bytes", fun=bytes)
        return b"".join(res.list)

    def __format__(self, format_spec: str) -> str:
        res = self.__apply("format", fun=format, args=(format_spec,))
        return "[" + ", ".join(res.list) + "]"

    # Comparison

    def __lt__(self, other: Any) -> EachContainer[bool]:
        return self.__apply("lt", fun_symbol="<", args=(other,))

    def __le__(self, other: Any) -> EachContainer[bool]:
        return self.__apply("le", fun_symbol="<=", args=(other,))

    def __eq__(self, other: Any) -> EachContainer[bool]:
        return self.__apply("eq", fun_symbol="==", args=(other,))

    def __ne__(self, other: Any) -> EachContainer[bool]:
        return self.__apply("ne", fun_symbol="!=", args=(other,))

    def __gt__(self, other: Any) -> EachContainer[bool]:
        return self.__apply("gt", fun_symbol=">", args=(other,))

    def __ge__(self, other: Any) -> EachContainer[bool]:
        return self.__apply("ge", fun_symbol=">=", args=(other,))

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, tuple(self.list)))

    def __bool__(self) -> bool:
        """True if all evaluate to True"""
        return all(bool(obj) for obj in self.list) if self.list else False

    # Attribute access

    def __getattr__(self, attr_name: str) -> EachContainer[Any]:
        return self.__apply("getattr", fun=getattr, args=(attr_name,))

    def __setattr__(self, attr_name: str, attr_value: Any) -> None:
        if attr_name == "list":
            return super().__setattr__(attr_name, attr_value)
        return self.__apply("setattr", fun=setattr, args=(attr_name, attr_value))

    def __delattr__(self, attr_name: str) -> None:
        return self.__apply("delattr", fun=delattr, args=(attr_name,))

    def __dir__(self) -> list[str]:
        """List of the union of each object's 'dir()' result."""
        return set.intersection(*(set(dir(obj)) for obj in self.list))

    # Function behavior

    def __call__(self, *args: Any, **kwargs: Any) -> EachContainer[Any]:
        """Apply a function to each element in the list.

        `operator.call` is only available in Python 3.11+.

        """
        fun = None
        if sys.version_info < (3, 11):

            def fun(obj: Any, *args: Any, **kwargs: Any) -> Any:
                """Defined as in '/Lib/operator.py'"""
                return obj(*args, **kwargs)

        return self.__apply("call", fun=fun, args=args, kwargs=kwargs)

    # Container behavior -- list-like operations

    def __len__(self) -> int:
        """Returns the length of the inner list."""
        return len(self.list)

    def __iter__(self) -> Iterable[Any]:
        """Iters through the inner list."""
        yield from self.list

    def __reversed__(self) -> Iterable[Any]:
        yield from reversed(self.list)

    # Container methods -- non-list-like operations

    def __contains__(self, item: Any) -> bool:
        """Returns True if all the objects in the list contain the item."""
        return bool(self.__apply("contains", fun_symbol="in", args=(item,)))

    def __getitem__(self, key: Any) -> Any:
        """Returns the item at the given key from each object in the list.

        This means that objects in the list must support the '__getitem__'
        method, otherwise, an exception will be raised. But, there is an
        special case if an EachContainer of pure booleans is passed as the key:
        it will return a new EachContainer containing the items at the
        positions where the boolean is True.

        Note that, if an EachContainer of any other type is passed as the key,
        the standard behavior will be applied: it will match each key in the
        EachContainer passed as key, to each object in the list; and return a
        new EachContainer containing the items at those positions.

        """
        if isinstance(key, EachContainer) and all(isinstance(k, bool) for k in key.list):
            if len(key.list) != len(self.list):
                raise ValueError(
                    "EachContainer used as key must have the same length as the "
                    "EachContainer being used on."
                )
            return EachContainer([obj for obj, k in zip(self.list, key.list) if k is True])
        return self.__apply("getitem", args=(key,))

    def __setitem__(self, key: Any, value: Any) -> None:
        """Sets the item at the given key in each object in the list.

        Parallel to '__getitem__', if an EachContainer of pure booleans is
        passed as the key, it will set the value at the positions where the
        boolean is True. In this case, if the value given is also an EachContainer, it will
        match each value in the EachContainer to each position where the boolean is
        True, and set the value at those positions. If the value is not an
        EachContainer, it will set the same value at all positions where the boolean
        is True.

        """
        if isinstance(key, EachContainer) and all(isinstance(k, bool) for k in key.list):
            if len(key.list) != len(self.list):
                raise ValueError(
                    "EachContainer used as key must have the same length as the "
                    "EachContainer being used on."
                )
            if isinstance(value, EachContainer):
                if len(value.list) != sum(key.list):
                    raise ValueError(
                        "EachContainer used as value must match the number of "
                        "True items in the key EachContainer."
                    )
                for i, k in enumerate(key.list):
                    if k:
                        self.list[i] = value.list.pop(0)
            else:
                for i, k in enumerate(key.list):
                    if k:
                        self.list[i] = value
        else:
            self.__apply("setitem", args=(key, value))

    def __delitem__(self, key: Any) -> None:
        """Deletes the item at the given key in each object in the list.

        Parallel to '__getitem__', if an EachContainer of pure booleans is passed
        as the key, it will delete the items at the positions where the boolean
        is True.

        """
        if isinstance(key, EachContainer) and all(isinstance(k, bool) for k in key.list):
            if len(key.list) != len(self.list):
                raise ValueError(
                    "EachContainer used as key must have the same length as the"
                    " EachContainer being used on."
                )
            self.list = [obj for i, obj in enumerate(self.list) if not key.list[i]]
        else:
            self.__apply("delitem", args=(key,))

    # Arithmetic and logical operations

    def __add__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("add", fun_symbol="+", args=(other,))

    def __sub__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("sub", fun_symbol="-", args=(other,))

    def __mul__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("mul", fun_symbol="*", args=(other,))

    def __matmul__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("matmul", fun_symbol="@", args=(other,))

    def __truediv__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("truediv", fun_symbol="/", args=(other,))

    def __floordiv__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("floordiv", fun_symbol="//", args=(other,))

    def __mod__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("mod", fun_symbol="%", args=(other,))

    def __divmod__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("divmod", fun=divmod, args=(other,))

    def __pow__(self, other: Any, modulo: Any = None) -> EachContainer[Any]:
        if modulo:
            return self.__apply("pow", fun=pow, args=(other, modulo))
        return self.__apply("pow", fun_symbol="**", args=(other,))

    def __lshift__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("lshift", fun_symbol="<<", args=(other,))

    def __rshift__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("rshift", fun_symbol=">>", args=(other,))

    def __and__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("and_", fun_symbol="&", args=(other,))

    def __xor__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("xor", fun_symbol="^", args=(other,))

    def __or__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("or_", fun_symbol="|", args=(other,))

    # Arithmetic and logical operations, reflected

    def __radd__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("add", fun_symbol="+", swapped=True, args=(other,))

    def __rsub__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("sub", fun_symbol="-", swapped=True, args=(other,))

    def __rmul__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("mul", fun_symbol="*", swapped=True, args=(other,))

    def __rmatmul__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("matmul", fun_symbol="@", swapped=True, args=(other,))

    def __rtruediv__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("truediv", fun_symbol="/", swapped=True, args=(other,))

    def __rfloordiv__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("floordiv", fun_symbol="//", swapped=True, args=(other,))

    def __rmod__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("mod", fun_symbol="%", swapped=True, args=(other,))

    def __rdivmod__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("divmod", fun=divmod, swapped=True, args=(other,))

    def __rpow__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("pow", fun_symbol="**", swapped=True, args=(other,))

    def __rlshift__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("lshift", fun_symbol="<<", swapped=True, args=(other,))

    def __rrshift__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("rshift", fun_symbol=">>", swapped=True, args=(other,))

    def __rand__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("and_", fun_symbol="&", swapped=True, args=(other,))

    def __rxor__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("xor", fun_symbol="^", swapped=True, args=(other,))

    def __ror__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("or_", fun_symbol="|", swapped=True, args=(other,))

    # Arithmetic and logical operations, identity

    def __iadd__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("add", fun_symbol="+=", inplace=True, args=(other,))

    def __isub__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("sub", fun_symbol="-=", inplace=True, args=(other,))

    def __imul__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("mul", fun_symbol="*=", inplace=True, args=(other,))

    def __imatmul__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("matmul", fun_symbol="@=", inplace=True, args=(other,))

    def __itruediv__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("truediv", fun_symbol="/=", inplace=True, args=(other,))

    def __ifloordiv__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("floordiv", fun_symbol="//=", inplace=True, args=(other,))

    def __imod__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("mod", fun_symbol="%=", inplace=True, args=(other,))

    def __ipow__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("pow", fun_symbol="**=", inplace=True, args=(other,))

    def __ilshift__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("lshift", fun_symbol="<<=", inplace=True, args=(other,))

    def __irshift__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("rshift", fun_symbol=">>=", inplace=True, args=(other,))

    def __iand__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("and_", fun_symbol="&=", inplace=True, args=(other,))

    def __ixor__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("xor", fun_symbol="^=", inplace=True, args=(other,))

    def __ior__(self, other: Any) -> EachContainer[Any]:
        return self.__apply("or_", fun_symbol="|=", inplace=True, args=(other,))

    # Unitary operations

    def __neg__(self) -> EachContainer[Any]:
        return self.__apply("neg", fun_symbol="-")

    def __pos__(self) -> EachContainer[Any]:
        return self.__apply("pos", fun_symbol="+")


def each(*args: Any) -> EachContainer[Any]:
    """Creates an "each" container.

    An "each" container is a container that applies any operation performed on
    it to each of its items. Most of the time, this operations will also
    return a new "each" container with the results of the operation on each
    of the items. For example:

    >>> x = each([1, 2, 3])
    >>> x + 1
    each([2, 3, 4])

    Operands can also be "each" containers, meaning things like this are
    possible:

    >>> each([1, 2, 3]) + each([4, 5, 6])
    each([5, 7, 9])

    When interpreted as a boolean, an "each" container will return True if
    all of its items evaluate to True, and False otherwise:

    >>> x = each([1, 2, 3])
    >>> (x > 0) is True
    True

    Note that "each" containers are not meant to behave like lists, so common
    list operations, like item accessing, can be confusing:

    >>> x = each([1, 2, 3])
    >>> x[0]  # [0] applies to each item, but 'int' does not support indexing
    each(...)

    >>> y = each([[1, 2], [3, 4], [5, 6]])
    >>> y[0]  # This works, as the items are lists
    each([1, 3, 5])

    >>> len(x)  # 'len()' and 'iter()' do work like with lists
    3

    If you need to access items in the container, attribute 'list' is
    available, and can even be modified directly:

    >>> x.list[0]
    1
    >>> x.list[0] = 10
    >>> x.list
    [10, 2, 3]


    `args` can be:
    - Empty: returns an empty container.
    - A single iterable: returns a container with the items of the iterable.
    - A single non-iterable item: returns a container with the item as its only
    element.
    - Multiple items: returns a container with the items as elements.

    """
    if not args:
        return EachContainer([])
    if len(args) == 1 and isinstance(args[0], Iterable):
        return EachContainer(args[0])
    return EachContainer(list(args))