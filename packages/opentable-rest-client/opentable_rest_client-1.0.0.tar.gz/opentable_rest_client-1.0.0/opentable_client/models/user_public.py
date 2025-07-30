from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserPublic")


@_attrs_define
class UserPublic:
    """
    Attributes:
        user_id (str):
        api_token (str):
        email (str):
        first_name (str):
        last_name (str):
        phone_number (str):
        created_at (str):
        org_id (str):
    """

    user_id: str
    api_token: str
    email: str
    first_name: str
    last_name: str
    phone_number: str
    created_at: str
    org_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        api_token = self.api_token

        email = self.email

        first_name = self.first_name

        last_name = self.last_name

        phone_number = self.phone_number

        created_at = self.created_at

        org_id = self.org_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "api_token": api_token,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "created_at": created_at,
                "org_id": org_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        api_token = d.pop("api_token")

        email = d.pop("email")

        first_name = d.pop("first_name")

        last_name = d.pop("last_name")

        phone_number = d.pop("phone_number")

        created_at = d.pop("created_at")

        org_id = d.pop("org_id")

        user_public = cls(
            user_id=user_id,
            api_token=api_token,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            created_at=created_at,
            org_id=org_id,
        )

        user_public.additional_properties = d
        return user_public

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
