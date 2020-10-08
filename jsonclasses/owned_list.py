"""The owner observable list."""
from __future__ import annotations
from typing import (Generic, Iterable, Any, List, Optional, Protocol, TypeVar,
                    MutableSequence, overload, cast)

T_contra = TypeVar('T_contra', contravariant=True)
_T = TypeVar('_T')


class ListOwner(Protocol[T_contra]):

    def __olist_add__(self,
                      olist: OwnedList,
                      index: int,
                      val: T_contra) -> None: ...

    def __olist_del__(self, olist: OwnedList, val: T_contra) -> None: ...

    def __olist_sor__(self, olist: OwnedList) -> None: ...


def is_list_owner(obj: Any):
    has_add = hasattr(obj, '__olist_add__')
    has_del = hasattr(obj, '__olist_del__')
    has_sor = hasattr(obj, '__olist_sor__')
    return has_add and has_del and has_sor


class OwnedList(list, MutableSequence[_T], Generic[_T]):

    @overload
    def __init__(self, owner: ListOwner) -> None: ...

    @overload
    def __init__(self, iterable: Iterable[_T], owner: ListOwner) -> None: ...

    def __init__(self, *args, **kwargs) -> None:
        owner: Optional[ListOwner[_T]] = kwargs.get('owner')
        iterable: Optional[Iterable[_T]] = kwargs.get('iterable')
        for arg in args:
            if is_list_owner(arg):
                owner = arg
            else:
                iterable = arg
        if iterable is not None:
            super().__init__(iterable)
        else:
            super().__init__()
        self.owner = cast(ListOwner[_T], owner)

    def append(self, value: _T) -> None:
        super().append(value)
        self.owner.__olist_add__(self, len(self) - 1, value)

    def extend(self, values: Iterable[_T]) -> None:
        curlen = len(self)
        super().extend(values)
        for v in values:
            self.owner.__olist_add__(self, curlen, v)
            curlen += 1

    def insert(self, index: int, value: _T) -> None:
        curlen = len(self)
        super().insert(index, value)
        idx = min(curlen, index)
        self.owner.__olist_add__(self, idx, value)

    def remove(self, value: _T) -> None:
        super().remove(value)
        self.owner.__olist_del__(self, value)

    def sort(self, **kwargs) -> None:  # TODO: fix argument type hint
        super().sort(**kwargs)
        self.owner.__olist_sor__(self)

    def clear(self) -> None:
        items = [item for item in self]
        super().clear()
        for item in items:
            self.owner.__olist_del__(self, item)

    def pop(self, *args) -> _T:  # TODO: fix argument type hint
        retval = super().pop(*args)
        self.owner.__olist_del__(self, retval)
        return retval

    def reverse(self) -> None:
        super().reverse()
        self.owner.__olist_sor__(self)

    def __add__(self, x: List[_T]) -> List[_T]:
        return super().__add__(x)

    def __iadd__(self, x: Iterable[_T]) -> OwnedList[_T]:
        curlen = len(self)
        retval = super().__iadd__(x)
        for v in x:
            self.owner.__olist_add__(self, curlen, v)
            curlen += 1
        return retval

    def __setitem__(self, *args) -> None:
        len_self = len(self)
        if isinstance(args[0], int):
            idx: int = args[0]
            if idx < 0:
                idx = len_self + idx
            val = self[idx] if 0 <= idx < len_self else None
            super().__setitem__(*args)
            self.owner.__olist_del__(self, val)
            self.owner.__olist_add__(self, idx, args[1])
        elif isinstance(args[0], slice):
            slc: slice = args[0]
            remove_list = self[slc]
            start = slc.start or 0
            step = slc.step or 1
            if start < 0:
                start = len_self + start
            start = min(max(0, start), len_self)
            super().__setitem__(*args)
            for item in remove_list:
                self.owner.__olist_del__(self, item)
            for item in args[1]:
                self.owner.__olist_add__(self, start, item)
                start += step
        else:
            super().__setitem__(*args)

    # # def __delitem__(self, i: slice) -> None: