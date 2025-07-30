import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.trajectory_response_trajectory_data_item import TrajectoryResponseTrajectoryDataItem


T = TypeVar("T", bound="TrajectoryResponse")


@_attrs_define
class TrajectoryResponse:
    """Trajectory response schema

    Attributes:
        workflow_id (UUID):
        trajectory_data (list['TrajectoryResponseTrajectoryDataItem']):
        id (UUID):
        user_id (UUID):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    workflow_id: UUID
    trajectory_data: list["TrajectoryResponseTrajectoryDataItem"]
    id: UUID
    user_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workflow_id = str(self.workflow_id)

        trajectory_data = []
        for trajectory_data_item_data in self.trajectory_data:
            trajectory_data_item = trajectory_data_item_data.to_dict()
            trajectory_data.append(trajectory_data_item)

        id = str(self.id)

        user_id = str(self.user_id)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workflow_id": workflow_id,
                "trajectory_data": trajectory_data,
                "id": id,
                "user_id": user_id,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.trajectory_response_trajectory_data_item import TrajectoryResponseTrajectoryDataItem

        d = dict(src_dict)
        workflow_id = UUID(d.pop("workflow_id"))

        trajectory_data = []
        _trajectory_data = d.pop("trajectory_data")
        for trajectory_data_item_data in _trajectory_data:
            trajectory_data_item = TrajectoryResponseTrajectoryDataItem.from_dict(trajectory_data_item_data)

            trajectory_data.append(trajectory_data_item)

        id = UUID(d.pop("id"))

        user_id = UUID(d.pop("user_id"))

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        trajectory_response = cls(
            workflow_id=workflow_id,
            trajectory_data=trajectory_data,
            id=id,
            user_id=user_id,
            created_at=created_at,
            updated_at=updated_at,
        )

        trajectory_response.additional_properties = d
        return trajectory_response

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
