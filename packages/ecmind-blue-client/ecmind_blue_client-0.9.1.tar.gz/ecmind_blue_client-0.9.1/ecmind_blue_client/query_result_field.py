"""
QueryResultField object
"""

from typing import Union

from XmlElement import XmlElement

from ecmind_blue_client.const import SortOrder, SystemFields


class QueryResultField:
    """Create a new QueryResultField() object.

    Args:
        field (Union[str, SystemFields]):
            A internal name as string or a instance of SystemFields.
            Internal names beeing automatically checked against known system field names.
        sort_pos (Union[int, None], optional): (Optional) int of the sort position in a query, default = None.
        sort_order (Union[SortOrder, None], optional):
            (Optional) SortOrder instance for this field, default = SortOrder.NONE if sort_pos = None else SortOrder.ASC
    """

    def __init__(
        self,
        field: Union[str, SystemFields],
        sort_pos: Union[int, None] = None,
        sort_order: Union[SortOrder, None] = None,
    ):
        if isinstance(field, SystemFields):
            self.internal_name = field.name
            self.system = True
        elif field in [system_field.name for system_field in SystemFields]:
            self.internal_name = field
            self.system = True
        else:
            self.internal_name = field
            self.system = False

        self.sort_pos = sort_pos

        if sort_order is None and sort_pos is not None:
            self.sort_order = SortOrder.ASC
        else:
            self.sort_order = sort_order if sort_order else SortOrder.NONE

    def __repr__(self) -> str:
        return f"{self.internal_name} (system:{1 if self.system else 0}, sort_pos:{self.sort_pos}, sort_order:{self.sort_order.name})"

    def __len__(self) -> int:
        return self.internal_name.__len__()

    def to_xml_element(self) -> XmlElement:
        """Render self to XmlElement

        Returns:
            XmlElement: The field as XMLElement instance
        """
        xml = XmlElement("Field", {"internal_name": self.internal_name})
        if self.system:
            xml.attributes["system"] = "1"

        if self.sort_pos and self.sort_pos > 0 and self.sort_order != SortOrder.NONE:
            xml.attributes["sortpos"] = str(self.sort_pos)
            xml.attributes["sortorder"] = self.sort_order.name

        return xml
