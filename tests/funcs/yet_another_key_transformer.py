from jsonclasses.field_definition import FieldStorage, FieldType
from jsonclasses.jsonclass_field import JSONClassField


def yet_another_key_transformer(field: JSONClassField) -> str:
    if field.definition.field_storage not in \
            [FieldStorage.FOREIGN_KEY, FieldStorage.LOCAL_KEY]:
        raise ValueError(f"field named {field.name} is not a reference field")
    if field.definition.field_type == FieldType.LIST:
        return field.name + '_ids'
    elif field.definition.field_type == FieldType.INSTANCE:
        return field.name + '_id'
    else:
        raise ValueError(f"field type {field.definition.field_type} is not a "
                         "supported reference field type")
