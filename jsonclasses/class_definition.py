"""
This module defines `ClassDefinition`. Each JSON class has its own class
definition. The class definition object contains detailed information about how
user defines a JSON class. This is used by the framework to lookup class fields
and class field settings.
"""
from __future__ import annotations
from typing import Optional, final, TYPE_CHECKING
from dataclasses import fields, Field
from inflection import camelize
from .jsonclass_field import JSONClassField
if TYPE_CHECKING:
    from .new_config import Config
    from .types import Types
    from .new_types_resolver import TypesResolver


@final
class ClassDefinition:
    """Class definition represents the class definition of JSON classes. Each
    JSON class has its own class definition. The class definition object
    contains detailed information about how user defines a JSON class. This is
    used by the framework to lookup class fields and class field settings.
    """

    def __init__(self: ClassDefinition, class_: type, config: Config) -> None:
        """
        Initialize a new class definition.

        Args:
            class_ (type): The JSON class for which the class definition is \
                created.
            config (Config): The configuration object for the targeted class.
        """
        self._list_fields: list[JSONClassField] = []
        self._dict_fields: dict[str, JSONClassField] = {}
        self._primary_field: Optional[JSONClassField] = None
        self._created_at_field: Optional[JSONClassField] = None
        self._updated_at_field: Optional[JSONClassField] = None
        self._deleted_at_field: Optional[JSONClassField] = None
        for field in fields(class_):
            name = field.name
            if config.camelize_json_keys:
                json_name = camelize(name, False)
            else:
                json_name = name
            if config.camelize_db_keys:
                db_name = camelize(name, False)
            else:
                db_name = name
            types = self._get_types(field, config.linked_class)
            if isinstance(field.default, Types):
                default = None
            elif field.default == field.default_factory:
                default = None
            else:
                default = field.default
            jsonclass_field = JSONClassField(
                name=name,
                json_name=json_name,
                db_name=db_name,
                default=default,
                types=types,
                definition=types.fdesc,
                validator=types.validator)
            self._list_fields.append(jsonclass_field)
            self._dict_fields[name] = jsonclass_field
            types.fdesc
            if types.fdesc.primary:
                self._primary_field = jsonclass_field
            if types.fdesc.usage == 'created_at':
                self._created_at_field = jsonclass_field
            elif types.fdesc.usage == 'updated_at':
                self._updated_at_field = jsonclass_field
            elif types.fdesc.usage == 'deleted_at':
                self._deleted_at_field = jsonclass_field

    def _get_types(self: ClassDefinition,
                   field: Field,
                   config: Config) -> Types:
        """
        Try to fetch the types definition from the field definition. If user
        hasn't define a types definition, an automatically synthesized one is
        returned.
        """
        from .types import Types
        if isinstance(field.default, Types):
            return field.default
        else:
            return TypesResolver().to_types(field.type, config)

    def field_named(self: ClassDefinition, name: str) -> JSONClassField:
        """
        Get the field which is named `name`.

        Args:
            name (str): The name of the field to return.

        Returns:
            JSONClassField: The field named `name`.

        Raises:
            ValueError: If can't find a field with name `name`.
        """
        if not self._dict_fields.get(name):
            raise ValueError(f'no field named {name} in class definition')
        return self._dict_fields[name]

    @property
    def created_at_field(self: ClassDefinition) -> Optional[JSONClassField]:
        """
        The class definition's field which represents the created at field.

        This is used by the framework to locate the correct field to find the
        record's created at timestamp.
        """
        return self._created_at_field

    @property
    def updated_at(self: ClassDefinition) -> Optional[JSONClassField]:
        """The class definition's field which represents the updated at field.

        This is used by the framework to locate the correct field to find the
        record's updated at timestamp.
        """
        return self._updated_at_field

    @property
    def deleted_at_field(self: ClassDefinition) -> Optional[JSONClassField]:
        """The class definition's field which represents the deleted at field.

        This is used by the framework to locate the correct field to find the
        record's deleted at timestamp.
        """
        return self._deleted_at_field

    @property
    def primary_field(self: ClassDefinition) -> Optional[JSONClassField]:
        """The class definition's primary field. This can be None if it's not
        defined by user.
        """
        return self._primary_field