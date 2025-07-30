from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CancelRequest")


@_attrs_define
class CancelRequest:
    """
    Attributes:
        restaurant_id (int): Restaurant ID from the original booking
        reservation_token (str): The unique token from the original booking confirmation
    """

    restaurant_id: int
    reservation_token: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        restaurant_id = self.restaurant_id

        reservation_token = self.reservation_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "restaurant_id": restaurant_id,
                "reservation_token": reservation_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        restaurant_id = d.pop("restaurant_id")

        reservation_token = d.pop("reservation_token")

        cancel_request = cls(
            restaurant_id=restaurant_id,
            reservation_token=reservation_token,
        )

        cancel_request.additional_properties = d
        return cancel_request

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
