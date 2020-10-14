from __future__ import annotations
from jsonclasses.orm_object import ORMObject
from unittest import TestCase
from jsonclasses import (jsonclass, JSONObject, ORMObject, types,
                         ValidationException)


class TestSetOnSaveVailidator(TestCase):

    def test_orm_objects_if_new_trigger_setonsave(self):
        @jsonclass(class_graph='test_setonsave_0')
        class ClassOne(ORMObject):
            a: str = types.str.required
            b: int = types.int.setonsave(lambda x: x + 1).required
        item = ClassOne(a='a', b=1)
        item.a = 'b'
        item._setonsave()
        self.assertEqual(item.a, 'b')
        self.assertEqual(item.b, 2)

    def test_orm_objects_if_modified_trigger_setonsave(self):
        @jsonclass(class_graph='test_setonsave_1')
        class ClassOne(ORMObject):
            a: str = types.str.required
            b: int = types.int.setonsave(lambda x: x + 1).required
        item = ClassOne(a='a', b=1)
        setattr(item, '_is_new', False)
        item.a = 'b'
        item._setonsave()
        self.assertEqual(item.a, 'b')
        self.assertEqual(item.b, 2)

    def test_orm_objects_if_modified_trigger_setonsave_0_args(self):
        x = 52

        @jsonclass(class_graph='test_setonsave_2')
        class ClassOne(ORMObject):
            a: str = types.str.required
            b: int = types.int.setonsave(lambda: x).required
        item = ClassOne(a='a', b=1)
        setattr(item, '_is_new', False)
        item.a = 'b'
        item._setonsave()
        self.assertEqual(item.a, 'b')
        self.assertEqual(item.b, 52)

    def test_orm_objects_setonsave_triggers_for_modified_linked_objects(self):
        @jsonclass(class_graph='test_setonsave_3')
        class User(ORMObject):
            id: int = types.int.primary.required
            name: str = types.str.required
            value: int = types.int.setonsave(lambda x: x + 1).required
            books: list[Book] = types.nonnull.listof('Book').linkedby('user').required

        @jsonclass(class_graph='test_setonsave_3')
        class Book(ORMObject):
            id: int = types.int.primary.required
            name: str = types.str.required
            value: int = types.int.setonsave(lambda x: x + 1).required
            user: User = types.linkto.instanceof(User).required

        book1 = Book(id=1, name='B1', value=1)
        book2 = Book(id=2, name='B2', value=1)
        setattr(book1, '_is_new', False)
        setattr(book2, '_is_new', False)
        user = User(id=1, name='U', value=1)
        setattr(user, '_is_new', False)
        user.books.append(book1)
        user.books.append(book2)
        user._setonsave()

        self.assertEqual(user.value, 2)
        self.assertEqual(book1.value, 2)
        self.assertEqual(book2.value, 2)

    def test_orm_objects_setonsave_triggers_even_root_is_not_modified(self):
        @jsonclass(class_graph='test_setonsave_4')
        class User(ORMObject):
            id: int = types.int.primary.required
            name: str = types.str.required
            value: int = types.int.setonsave(lambda x: x + 1).required
            books: list[Book] = types.nonnull.listof('Book').linkedby('user').required

        @jsonclass(class_graph='test_setonsave_4')
        class Book(ORMObject):
            id: int = types.int.primary.required
            name: str = types.str.required
            value: int = types.int.setonsave(lambda x: x + 1).required
            user: User = types.linkto.instanceof(User).required

        book1 = Book(id=1, name='B1', value=1)
        book2 = Book(id=2, name='B2', value=1)
        setattr(book1, '_is_new', False)
        setattr(book2, '_is_new', False)
        user = User(id=1, name='U', value=1)
        setattr(user, '_is_new', False)
        user.books.append(book1)
        user.books.append(book2)
        setattr(user, '_is_modified', False)
        setattr(user, '_modified_fields', set())
        user._setonsave()

        self.assertEqual(user.value, 1)
        self.assertEqual(book1.value, 2)
        self.assertEqual(book2.value, 2)
