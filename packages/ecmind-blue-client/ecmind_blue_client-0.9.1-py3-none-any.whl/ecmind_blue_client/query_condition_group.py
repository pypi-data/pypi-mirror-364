"""
QueryConditionGroup object
"""

from __future__ import annotations

from typing import List, Optional, Union

from XmlElement import XmlElement

from ecmind_blue_client.const import FieldGroupOperators
from ecmind_blue_client.query_condition_field import QueryConditionField


class QueryConditionGroup:
    """Create a new QueryConditionGroup() object combining the `<ConditionObject>` and `<FieldGroup>` tags.

    Args:
        object_name (str): The internal name of a folder, register or document type.
        field_conditions (Union[QueryConditionField, List[QueryConditionField]]): A list of or single QueryConditionField(s).
        field_groups (FieldGroupOperators, optional): A list of or single QueryConditionGroup(s).
        group_operator (Optional[Union[QueryConditionGroup, List[QueryConditionGroup]]], optional):
            FieldGroupOperators, default = FieldGroupOperators.AND.
    """

    def __init__(
        self,
        object_name: str,
        field_conditions: Union[QueryConditionField, List[QueryConditionField]],
        group_operator: FieldGroupOperators = FieldGroupOperators.AND,
        field_groups: Optional[Union[QueryConditionGroup, List[QueryConditionGroup]]] = None,
    ):
        self.internal_name = object_name
        if isinstance(field_conditions, list):
            self.field_conditions = field_conditions
        else:
            self.field_conditions = [field_conditions]

        if field_groups is None:
            self.field_groups = []
        elif isinstance(field_groups, list):
            self.field_groups = field_groups
        else:
            self.field_groups = [field_groups]

        for field_group in self.field_groups:
            assert field_group.internal_name == self.internal_name, (
                "The object_name of a sub field_group must match the object_name parent field_group."
                f"parent: {self.internal_name} != sub: {field_group.internal_name}"
            )

        self.group_operator = group_operator

    def __repr__(self) -> str:
        return f"{self.internal_name} ({self.group_operator.value}): {self.field_conditions}"

    def to_xml_element(self) -> XmlElement:
        """Render self to XmlElement"""
        return XmlElement(
            "FieldGroup",
            {"operator": self.group_operator.value},
            [x.to_xml_element() for x in self.field_conditions] + [x.to_xml_element() for x in self.field_groups],
        )
