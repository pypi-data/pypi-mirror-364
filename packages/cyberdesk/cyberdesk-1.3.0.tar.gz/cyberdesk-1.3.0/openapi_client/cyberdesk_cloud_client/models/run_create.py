from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RunCreate")


@_attrs_define
class RunCreate:
    """Schema for creating a run

    Attributes:
        workflow_id (UUID):
        machine_id (Union[None, UUID, Unset]): Machine ID. If not provided, an available machine will be automatically
            selected.
    """

    workflow_id: UUID
    machine_id: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workflow_id = str(self.workflow_id)

        machine_id: Union[None, Unset, str]
        if isinstance(self.machine_id, Unset):
            machine_id = UNSET
        elif isinstance(self.machine_id, UUID):
            machine_id = str(self.machine_id)
        else:
            machine_id = self.machine_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workflow_id": workflow_id,
            }
        )
        if machine_id is not UNSET:
            field_dict["machine_id"] = machine_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        workflow_id = UUID(d.pop("workflow_id"))

        def _parse_machine_id(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                machine_id_type_0 = UUID(data)

                return machine_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        machine_id = _parse_machine_id(d.pop("machine_id", UNSET))

        run_create = cls(
            workflow_id=workflow_id,
            machine_id=machine_id,
        )

        run_create.additional_properties = d
        return run_create

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
