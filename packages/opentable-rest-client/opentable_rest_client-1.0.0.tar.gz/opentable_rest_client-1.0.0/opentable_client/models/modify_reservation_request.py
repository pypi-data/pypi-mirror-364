from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ModifyReservationRequest")


@_attrs_define
class ModifyReservationRequest:
    """
    Attributes:
        new_slot_hash (str): The 'slotHash' of the new desired timeslot from the availability endpoint.
        new_date_time (str): The 'dateTime' of the new desired timeslot (e.g., '2025-07-27T17:15').
        new_availability_token (str): The 'token' of the new desired timeslot.
        reservation_token (str): The 'token' from the original reservation object.
        restaurant_id (int): The ID of the restaurant.
        party_size (Union[None, Unset, int]): The new party size.
        special_requests (Union[None, Unset, str]): New special requests for the reservation.
        occasion (Union[None, Unset, str]): New occasion (e.g., 'birthday').
        phone_number (Union[None, Unset, str]): New phone number for the reservation.
        seating_preference (Union[None, Unset, str]): New seating preference. Default: 'default'.
    """

    new_slot_hash: str
    new_date_time: str
    new_availability_token: str
    reservation_token: str
    restaurant_id: int
    party_size: Union[None, Unset, int] = UNSET
    special_requests: Union[None, Unset, str] = UNSET
    occasion: Union[None, Unset, str] = UNSET
    phone_number: Union[None, Unset, str] = UNSET
    seating_preference: Union[None, Unset, str] = "default"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_slot_hash = self.new_slot_hash

        new_date_time = self.new_date_time

        new_availability_token = self.new_availability_token

        reservation_token = self.reservation_token

        restaurant_id = self.restaurant_id

        party_size: Union[None, Unset, int]
        if isinstance(self.party_size, Unset):
            party_size = UNSET
        else:
            party_size = self.party_size

        special_requests: Union[None, Unset, str]
        if isinstance(self.special_requests, Unset):
            special_requests = UNSET
        else:
            special_requests = self.special_requests

        occasion: Union[None, Unset, str]
        if isinstance(self.occasion, Unset):
            occasion = UNSET
        else:
            occasion = self.occasion

        phone_number: Union[None, Unset, str]
        if isinstance(self.phone_number, Unset):
            phone_number = UNSET
        else:
            phone_number = self.phone_number

        seating_preference: Union[None, Unset, str]
        if isinstance(self.seating_preference, Unset):
            seating_preference = UNSET
        else:
            seating_preference = self.seating_preference

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_slot_hash": new_slot_hash,
                "new_date_time": new_date_time,
                "new_availability_token": new_availability_token,
                "reservation_token": reservation_token,
                "restaurant_id": restaurant_id,
            }
        )
        if party_size is not UNSET:
            field_dict["party_size"] = party_size
        if special_requests is not UNSET:
            field_dict["special_requests"] = special_requests
        if occasion is not UNSET:
            field_dict["occasion"] = occasion
        if phone_number is not UNSET:
            field_dict["phone_number"] = phone_number
        if seating_preference is not UNSET:
            field_dict["seating_preference"] = seating_preference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        new_slot_hash = d.pop("new_slot_hash")

        new_date_time = d.pop("new_date_time")

        new_availability_token = d.pop("new_availability_token")

        reservation_token = d.pop("reservation_token")

        restaurant_id = d.pop("restaurant_id")

        def _parse_party_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        party_size = _parse_party_size(d.pop("party_size", UNSET))

        def _parse_special_requests(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        special_requests = _parse_special_requests(d.pop("special_requests", UNSET))

        def _parse_occasion(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        occasion = _parse_occasion(d.pop("occasion", UNSET))

        def _parse_phone_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        phone_number = _parse_phone_number(d.pop("phone_number", UNSET))

        def _parse_seating_preference(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        seating_preference = _parse_seating_preference(d.pop("seating_preference", UNSET))

        modify_reservation_request = cls(
            new_slot_hash=new_slot_hash,
            new_date_time=new_date_time,
            new_availability_token=new_availability_token,
            reservation_token=reservation_token,
            restaurant_id=restaurant_id,
            party_size=party_size,
            special_requests=special_requests,
            occasion=occasion,
            phone_number=phone_number,
            seating_preference=seating_preference,
        )

        modify_reservation_request.additional_properties = d
        return modify_reservation_request

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
