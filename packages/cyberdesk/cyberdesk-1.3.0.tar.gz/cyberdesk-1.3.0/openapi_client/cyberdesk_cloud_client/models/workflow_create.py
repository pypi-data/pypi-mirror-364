from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowCreate")


@_attrs_define
class WorkflowCreate:
    """Schema for creating a workflow

    Attributes:
        main_prompt (str):
        name (Union[None, Unset, str]):
        cleanup_prompt (Union[None, Unset, str]):
    """

    main_prompt: str
    name: Union[None, Unset, str] = UNSET
    cleanup_prompt: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        main_prompt = self.main_prompt

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "main_prompt": main_prompt,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if cleanup_prompt is not UNSET:
            field_dict["cleanup_prompt"] = cleanup_prompt

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        main_prompt = d.pop("main_prompt")

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

        workflow_create = cls(
            main_prompt=main_prompt,
            name=name,
            cleanup_prompt=cleanup_prompt,
        )

        workflow_create.additional_properties = d
        return workflow_create

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
