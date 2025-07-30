from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.trajectory_create_trajectory_data_item import TrajectoryCreateTrajectoryDataItem


T = TypeVar("T", bound="TrajectoryCreate")


@_attrs_define
class TrajectoryCreate:
    """Schema for creating a trajectory

    Attributes:
        workflow_id (UUID):
        trajectory_data (list['TrajectoryCreateTrajectoryDataItem']):
    """

    workflow_id: UUID
    trajectory_data: list["TrajectoryCreateTrajectoryDataItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workflow_id = str(self.workflow_id)

        trajectory_data = []
        for trajectory_data_item_data in self.trajectory_data:
            trajectory_data_item = trajectory_data_item_data.to_dict()
            trajectory_data.append(trajectory_data_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workflow_id": workflow_id,
                "trajectory_data": trajectory_data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.trajectory_create_trajectory_data_item import TrajectoryCreateTrajectoryDataItem

        d = dict(src_dict)
        workflow_id = UUID(d.pop("workflow_id"))

        trajectory_data = []
        _trajectory_data = d.pop("trajectory_data")
        for trajectory_data_item_data in _trajectory_data:
            trajectory_data_item = TrajectoryCreateTrajectoryDataItem.from_dict(trajectory_data_item_data)

            trajectory_data.append(trajectory_data_item)

        trajectory_create = cls(
            workflow_id=workflow_id,
            trajectory_data=trajectory_data,
        )

        trajectory_create.additional_properties = d
        return trajectory_create

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
