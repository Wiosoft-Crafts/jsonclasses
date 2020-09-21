"""module for linkedin validator."""
from typing import Any
from ..field_description import FieldDescription, FieldStorage
from ..config import Config
from .validator import Validator


class LinkedInValidator(Validator):
    """Linked in validator marks a field linked with a joinning table which is
    also a JSON Class."""

    def __init__(self, cls: Any) -> None:
        self.cls = cls

    def define(self, field_description: FieldDescription) -> None:
        field_description.field_storage = FieldStorage.FOREIGN_KEY
        field_description.join_table_cls = self.cls
        field_description.use_join_table = True

    def validate(self, value: Any, key_path: str, root: Any, all_fields: bool, config: Config) -> None:
        pass