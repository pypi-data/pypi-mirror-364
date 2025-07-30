from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.card_create import CardCreate


T = TypeVar("T", bound="BookingRequest")


@_attrs_define
class BookingRequest:
    """
    Attributes:
        restaurant_id (int): Restaurant ID from search results
        slot_hash (str): Slot hash from availability results
        date_time (str): Date/time in YYYY-MM-DDTHH:MM format
        availability_token (str): Availability token from timeslot
        location (str): Location for geocoding
        party_size (Union[Unset, int]): Number of diners Default: 2.
        table_attribute (Union[Unset, str]): Seating preference Default: 'default'.
        special_requests (Union[Unset, str]): Special requests Default: ''.
        occasion (Union[None, Unset, str]): Special occasion
        sms_opt_in (Union[Unset, bool]): SMS notifications opt-in Default: True.
        requires_credit_card (Union[Unset, bool]): Whether credit card is required for this booking Default: False.
        card_details (Union['CardCreate', None, Unset]): Credit card details (required only if slot requires card)
    """

    restaurant_id: int
    slot_hash: str
    date_time: str
    availability_token: str
    location: str
    party_size: Union[Unset, int] = 2
    table_attribute: Union[Unset, str] = "default"
    special_requests: Union[Unset, str] = ""
    occasion: Union[None, Unset, str] = UNSET
    sms_opt_in: Union[Unset, bool] = True
    requires_credit_card: Union[Unset, bool] = False
    card_details: Union["CardCreate", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.card_create import CardCreate

        restaurant_id = self.restaurant_id

        slot_hash = self.slot_hash

        date_time = self.date_time

        availability_token = self.availability_token

        location = self.location

        party_size = self.party_size

        table_attribute = self.table_attribute

        special_requests = self.special_requests

        occasion: Union[None, Unset, str]
        if isinstance(self.occasion, Unset):
            occasion = UNSET
        else:
            occasion = self.occasion

        sms_opt_in = self.sms_opt_in

        requires_credit_card = self.requires_credit_card

        card_details: Union[None, Unset, dict[str, Any]]
        if isinstance(self.card_details, Unset):
            card_details = UNSET
        elif isinstance(self.card_details, CardCreate):
            card_details = self.card_details.to_dict()
        else:
            card_details = self.card_details

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "restaurant_id": restaurant_id,
                "slot_hash": slot_hash,
                "date_time": date_time,
                "availability_token": availability_token,
                "location": location,
            }
        )
        if party_size is not UNSET:
            field_dict["party_size"] = party_size
        if table_attribute is not UNSET:
            field_dict["table_attribute"] = table_attribute
        if special_requests is not UNSET:
            field_dict["special_requests"] = special_requests
        if occasion is not UNSET:
            field_dict["occasion"] = occasion
        if sms_opt_in is not UNSET:
            field_dict["sms_opt_in"] = sms_opt_in
        if requires_credit_card is not UNSET:
            field_dict["requires_credit_card"] = requires_credit_card
        if card_details is not UNSET:
            field_dict["card_details"] = card_details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.card_create import CardCreate

        d = dict(src_dict)
        restaurant_id = d.pop("restaurant_id")

        slot_hash = d.pop("slot_hash")

        date_time = d.pop("date_time")

        availability_token = d.pop("availability_token")

        location = d.pop("location")

        party_size = d.pop("party_size", UNSET)

        table_attribute = d.pop("table_attribute", UNSET)

        special_requests = d.pop("special_requests", UNSET)

        def _parse_occasion(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        occasion = _parse_occasion(d.pop("occasion", UNSET))

        sms_opt_in = d.pop("sms_opt_in", UNSET)

        requires_credit_card = d.pop("requires_credit_card", UNSET)

        def _parse_card_details(data: object) -> Union["CardCreate", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                card_details_type_0 = CardCreate.from_dict(data)

                return card_details_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CardCreate", None, Unset], data)

        card_details = _parse_card_details(d.pop("card_details", UNSET))

        booking_request = cls(
            restaurant_id=restaurant_id,
            slot_hash=slot_hash,
            date_time=date_time,
            availability_token=availability_token,
            location=location,
            party_size=party_size,
            table_attribute=table_attribute,
            special_requests=special_requests,
            occasion=occasion,
            sms_opt_in=sms_opt_in,
            requires_credit_card=requires_credit_card,
            card_details=card_details,
        )

        booking_request.additional_properties = d
        return booking_request

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
