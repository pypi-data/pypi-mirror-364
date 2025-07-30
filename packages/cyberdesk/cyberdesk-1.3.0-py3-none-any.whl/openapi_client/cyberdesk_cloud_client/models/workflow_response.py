import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.workflow_response_old_versions_type_0_item import WorkflowResponseOldVersionsType0Item


T = TypeVar("T", bound="WorkflowResponse")


@_attrs_define
class WorkflowResponse:
    """Workflow response schema

    Attributes:
        main_prompt (str):
        id (UUID):
        user_id (UUID):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        name (Union[None, Unset, str]):
        cleanup_prompt (Union[None, Unset, str]):
        old_versions (Union[None, Unset, list['WorkflowResponseOldVersionsType0Item']]):
    """

    main_prompt: str
    id: UUID
    user_id: UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    name: Union[None, Unset, str] = UNSET
    cleanup_prompt: Union[None, Unset, str] = UNSET
    old_versions: Union[None, Unset, list["WorkflowResponseOldVersionsType0Item"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        main_prompt = self.main_prompt

        id = str(self.id)

        user_id = str(self.user_id)

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        cleanup_prompt: Union[None, Unset, str]
        if isinstance(self.cleanup_prompt, Unset):
            cleanup_prompt = UNSET
        else:
            cleanup_prompt = self.cleanup_prompt

        old_versions: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.old_versions, Unset):
            old_versions = UNSET
        elif isinstance(self.old_versions, list):
            old_versions = []
            for old_versions_type_0_item_data in self.old_versions:
                old_versions_type_0_item = old_versions_type_0_item_data.to_dict()
                old_versions.append(old_versions_type_0_item)

        else:
            old_versions = self.old_versions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "main_prompt": main_prompt,
                "id": id,
                "user_id": user_id,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if cleanup_prompt is not UNSET:
            field_dict["cleanup_prompt"] = cleanup_prompt
        if old_versions is not UNSET:
            field_dict["old_versions"] = old_versions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workflow_response_old_versions_type_0_item import WorkflowResponseOldVersionsType0Item

        d = dict(src_dict)
        main_prompt = d.pop("main_prompt")

        id = UUID(d.pop("id"))

        user_id = UUID(d.pop("user_id"))

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_cleanup_prompt(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        cleanup_prompt = _parse_cleanup_prompt(d.pop("cleanup_prompt", UNSET))

        def _parse_old_versions(data: object) -> Union[None, Unset, list["WorkflowResponseOldVersionsType0Item"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                old_versions_type_0 = []
                _old_versions_type_0 = data
                for old_versions_type_0_item_data in _old_versions_type_0:
                    old_versions_type_0_item = WorkflowResponseOldVersionsType0Item.from_dict(
                        old_versions_type_0_item_data
                    )

                    old_versions_type_0.append(old_versions_type_0_item)

                return old_versions_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["WorkflowResponseOldVersionsType0Item"]], data)

        old_versions = _parse_old_versions(d.pop("old_versions", UNSET))

        workflow_response = cls(
            main_prompt=main_prompt,
            id=id,
            user_id=user_id,
            created_at=created_at,
            updated_at=updated_at,
            name=name,
            cleanup_prompt=cleanup_prompt,
            old_versions=old_versions,
        )

        workflow_response.additional_properties = d
        return workflow_response

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
