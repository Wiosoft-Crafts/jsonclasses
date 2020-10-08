from __future__ import annotations
from typing import Any, NamedTuple, List
from unittest import TestCase
from jsonclasses.owned_list import OwnedList


class AddRecord(NamedTuple):
    olist: OwnedList
    idx: int
    val: Any


class DelRecord(NamedTuple):
    olist: OwnedList
    val: Any


class SorRecord(NamedTuple):
    olist: OwnedList


class Owner:

    def __init__(self):
        self.add_records: List[AddRecord] = []
        self.del_records: List[DelRecord] = []
        self.sor_records: List[SorRecord] = []

    def __olist_add__(self, olist: OwnedList, index: int, val: Any) -> None:
        self.add_records.append(AddRecord(olist, index, val))

    def __olist_del__(self, olist: OwnedList, val: Any) -> None:
        self.del_records.append(DelRecord(olist, val))

    def __olist_sor__(self, olist: OwnedList) -> None:
        self.sor_records.append(SorRecord(olist))


class TestOwnedList(TestCase):

    def test_owned_list_can_be_created_with_owner_arg(self):
        owner = Owner()
        owned_list = OwnedList(owner)
        self.assertEqual(owned_list, [])
        self.assertEqual(owned_list.__class__, OwnedList)
        self.assertEqual(owned_list.owner, owner)

    def test_owned_list_can_be_created_with_owner_kwarg(self):
        owner = Owner()
        owned_list = OwnedList(owner=owner)
        self.assertEqual(owned_list, [])
        self.assertEqual(owned_list.__class__, OwnedList)
        self.assertEqual(owned_list.owner, owner)

    def test_owned_list_can_be_created_with_owner_and_iterable_arg(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        self.assertEqual(owned_list, [1, 2, 3])
        self.assertEqual(owned_list.__class__, OwnedList)
        self.assertEqual(owned_list.owner, owner)

    def test_owned_list_can_be_created_with_owner_and_iterable_kwarg(self):
        owner = Owner()
        owned_list = OwnedList(iterable=[1, 2, 3], owner=owner)
        self.assertEqual(owned_list, [1, 2, 3])
        self.assertEqual(owned_list.__class__, OwnedList)
        self.assertEqual(owned_list.owner, owner)

    def test_owned_list_get_notified_thru_append(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        owned_list.append(4)
        self.assertEqual(owned_list, [1, 2, 3, 4])
        self.assertEqual(owner.add_records, [AddRecord(owned_list, 3, 4)])

    def test_owned_list_get_notified_thru_extend(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        owned_list.extend([4, 5])
        self.assertEqual(owned_list, [1, 2, 3, 4, 5])
        self.assertEqual(owner.add_records, [
            AddRecord(owned_list, 3, 4),
            AddRecord(owned_list, 4, 5)])

    def test_owned_list_get_notified_thru_insert(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        owned_list.insert(0, 0)
        self.assertEqual(owned_list, [0, 1, 2, 3])
        self.assertEqual(owner.add_records, [AddRecord(owned_list, 0, 0)])

    def test_owned_list_get_notified_thru_insert_idx_overflow(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        owned_list.insert(100, 0)
        self.assertEqual(owned_list, [1, 2, 3, 0])
        self.assertEqual(owner.add_records, [AddRecord(owned_list, 3, 0)])

    def test_owned_list_get_notified_thru_remove(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        owned_list.remove(1)
        self.assertEqual(owned_list, [2, 3])
        self.assertEqual(owner.del_records, [DelRecord(owned_list, 1)])

    def test_owned_list_get_notified_thru_sort(self):
        owner = Owner()
        owned_list = OwnedList([1, 5, 3], owner)
        owned_list.sort()
        self.assertEqual(owned_list, [1, 3, 5])
        self.assertEqual(owner.sor_records, [SorRecord(owned_list)])

    def test_owned_list_get_notified_thru_clear(self):
        owner = Owner()
        owned_list = OwnedList([1, 5, 3], owner)
        owned_list.clear()
        self.assertEqual(owned_list, [])
        self.assertEqual(owner.del_records, [
            DelRecord(owned_list, 1),
            DelRecord(owned_list, 5),
            DelRecord(owned_list, 3)])

    def test_owned_list_get_notified_thru_pop(self):
        owner = Owner()
        owned_list = OwnedList([1, 5, 3], owner)
        owned_list.pop()
        self.assertEqual(owned_list, [1, 5])
        self.assertEqual(owner.del_records, [DelRecord(owned_list, 3)])

    def test_owned_list_get_notified_thru_pop_argument(self):
        owner = Owner()
        owned_list = OwnedList([1, 5, 3], owner)
        owned_list.pop(0)
        self.assertEqual(owned_list, [5, 3])
        self.assertEqual(owner.del_records, [DelRecord(owned_list, 1)])

    def test_owned_list_get_notified_thru_reverse(self):
        owner = Owner()
        owned_list = OwnedList([1, 5, 3], owner)
        owned_list.reverse()
        self.assertEqual(owned_list, [3, 5, 1])
        self.assertEqual(owner.sor_records, [SorRecord(owned_list)])

    def test_owned_list_get_notified_thru_plus_equal_sign(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        owned_list += [4, 5]
        self.assertEqual(owned_list, [1, 2, 3, 4, 5])
        self.assertEqual(owner.add_records, [
            AddRecord(owned_list, 3, 4),
            AddRecord(owned_list, 4, 5)])

    def test_owned_list_get_notified_thru_subscript_set(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        owned_list[0] = -1
        self.assertEqual(owned_list, [-1, 2, 3])
        self.assertEqual(owner.del_records, [DelRecord(owned_list, 1)])
        self.assertEqual(owner.add_records, [AddRecord(owned_list, 0, -1)])

    def test_owned_list_get_notified_thru_subscript_set_negative(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        owned_list[-1] = 9
        self.assertEqual(owned_list, [1, 2, 9])
        self.assertEqual(owner.del_records, [DelRecord(owned_list, 3)])
        self.assertEqual(owner.add_records, [AddRecord(owned_list, 2, 9)])

    def test_owned_list_raises_if_subscript_set_out_of_index_range(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        with self.assertRaisesRegex(IndexError,
                                    'list assignment index out of range'):
            owned_list[10] = -1

    def test_owned_list_raises_if_subscript_set_neg_out_of_index_range(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3], owner)
        with self.assertRaisesRegex(IndexError,
                                    'list assignment index out of range'):
            owned_list[-10] = -1

    def test_owned_list_get_notified_thru_subscript_slice_set(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3, 4, 5], owner)
        owned_list[1:3] = [7, 8]
        self.assertEqual(owned_list, [1, 7, 8, 4, 5])
        self.assertEqual(owner.del_records, [
            DelRecord(owned_list, 2),
            DelRecord(owned_list, 3)])
        self.assertEqual(owner.add_records, [
            AddRecord(owned_list, 1, 7),
            AddRecord(owned_list, 2, 8)])

    def test_owned_list_get_notified_thru_subscript_slice_set_overflow(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3, 4, 5], owner)
        owned_list[100:1] = [6, 7]
        self.assertEqual(owned_list, [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(owner.del_records, [])
        self.assertEqual(owner.add_records, [
            AddRecord(owned_list, 5, 6),
            AddRecord(owned_list, 6, 7)])

    def test_owned_list_get_notified_thru_subscript_slice_set_neg(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3, 4, 5], owner)
        owned_list[-3:] = [7, 8, 9]
        self.assertEqual(owned_list, [1, 2, 7, 8, 9])
        self.assertEqual(owner.del_records, [
            DelRecord(owned_list, 3),
            DelRecord(owned_list, 4),
            DelRecord(owned_list, 5)])
        self.assertEqual(owner.add_records, [
            AddRecord(owned_list, 2, 7),
            AddRecord(owned_list, 3, 8),
            AddRecord(owned_list, 4, 9)])

    def test_owned_list_get_notified_thru_subscript_slice_set_neg_ovfl(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3, 4, 5], owner)
        owned_list[-999:1] = [-1, 0]
        self.assertEqual(owned_list, [-1, 0, 2, 3, 4, 5])
        self.assertEqual(owner.del_records, [
            DelRecord(owned_list, 1)])
        self.assertEqual(owner.add_records, [
            AddRecord(owned_list, 0, -1),
            AddRecord(owned_list, 1, 0)])

    def test_owned_list_get_notified_thru_subscript_slice_set_step(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3, 4, 5], owner)
        owned_list[0::2] = [7, 8, 9]
        self.assertEqual(owned_list, [7, 2, 8, 4, 9])
        self.assertEqual(owner.del_records, [
            DelRecord(owned_list, 1),
            DelRecord(owned_list, 3),
            DelRecord(owned_list, 5)])
        self.assertEqual(owner.add_records, [
            AddRecord(owned_list, 0, 7),
            AddRecord(owned_list, 2, 8),
            AddRecord(owned_list, 4, 9)])

    def test_owned_list_get_notified_thru_subscript_slice_set_step_neg(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3, 4, 5], owner)
        owned_list[-5::2] = [7, 8, 9]
        self.assertEqual(owned_list, [7, 2, 8, 4, 9])
        self.assertEqual(owner.del_records, [
            DelRecord(owned_list, 1),
            DelRecord(owned_list, 3),
            DelRecord(owned_list, 5)])
        self.assertEqual(owner.add_records, [
            AddRecord(owned_list, 0, 7),
            AddRecord(owned_list, 2, 8),
            AddRecord(owned_list, 4, 9)])

    def test_owned_list_get_notified_thru_subscript_slice_set_step_err(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3, 4, 5], owner)
        with self.assertRaisesRegex(ValueError,
                                    ('attempt to assign sequence of size 3 to'
                                     ' extended slice of size 1')):
            owned_list[2::10] = [7, 8, 9]

    def test_owned_list_get_notified_thru_subscript_slice_set_step_ovfl(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3, 4, 5], owner)
        owned_list[10::2] = []
        self.assertEqual(owned_list, [1, 2, 3, 4, 5])
        self.assertEqual(owner.del_records, [])
        self.assertEqual(owner.add_records, [])

    def test_owned_list_get_notified_thru_sub_slice_set_step_neg_ovfl(self):
        owner = Owner()
        owned_list = OwnedList([1, 2, 3, 4, 5], owner)
        owned_list[-100::2] = [7, 8, 9]
        self.assertEqual(owned_list, [7, 2, 8, 4, 9])
        self.assertEqual(owner.del_records, [
            DelRecord(owned_list, 1),
            DelRecord(owned_list, 3),
            DelRecord(owned_list, 5)])
        self.assertEqual(owner.add_records, [
            AddRecord(owned_list, 0, 7),
            AddRecord(owned_list, 2, 8),
            AddRecord(owned_list, 4, 9)])
