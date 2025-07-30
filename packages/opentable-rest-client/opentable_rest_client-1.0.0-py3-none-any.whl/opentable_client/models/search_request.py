from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchRequest")


@_attrs_define
class SearchRequest:
    """
    Attributes:
        location (str):
        restaurant_name (Union[None, Unset, str]):
        date_time (Union[None, Unset, str]):
        party_size (Union[Unset, int]):  Default: 2.
        max_results (Union[Unset, int]):  Default: 20.
    """

    location: str
    restaurant_name: Union[None, Unset, str] = UNSET
    date_time: Union[None, Unset, str] = UNSET
    party_size: Union[Unset, int] = 2
    max_results: Union[Unset, int] = 20
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        location = self.location

        restaurant_name: Union[None, Unset, str]
        if isinstance(self.restaurant_name, Unset):
            restaurant_name = UNSET
        else:
            restaurant_name = self.restaurant_name

        date_time: Union[None, Unset, str]
        if isinstance(self.date_time, Unset):
            date_time = UNSET
        else:
            date_time = self.date_time

        party_size = self.party_size

        max_results = self.max_results

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "location": location,
            }
        )
        if restaurant_name is not UNSET:
            field_dict["restaurant_name"] = restaurant_name
        if date_time is not UNSET:
            field_dict["date_time"] = date_time
        if party_size is not UNSET:
            field_dict["party_size"] = party_size
        if max_results is not UNSET:
            field_dict["max_results"] = max_results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        location = d.pop("location")

        def _parse_restaurant_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        restaurant_name = _parse_restaurant_name(d.pop("restaurant_name", UNSET))

        def _parse_date_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        date_time = _parse_date_time(d.pop("date_time", UNSET))

        party_size = d.pop("party_size", UNSET)

        max_results = d.pop("max_results", UNSET)

        search_request = cls(
            location=location,
            restaurant_name=restaurant_name,
            date_time=date_time,
            party_size=party_size,
            max_results=max_results,
        )

        search_request.additional_properties = d
        return search_request

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
