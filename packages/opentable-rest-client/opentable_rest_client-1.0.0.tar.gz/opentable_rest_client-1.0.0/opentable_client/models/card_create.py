from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CardCreate")


@_attrs_define
class CardCreate:
    """
    Attributes:
        card_full_name (str): Full name on the credit card
        card_number (str): Credit card number
        card_exp_month (int): Expiration month (1-12)
        card_exp_year (int): Expiration year (YYYY)
        card_cvv (str): CVV/security code
        card_zip (str): Billing ZIP/postal code
    """

    card_full_name: str
    card_number: str
    card_exp_month: int
    card_exp_year: int
    card_cvv: str
    card_zip: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        card_full_name = self.card_full_name

        card_number = self.card_number

        card_exp_month = self.card_exp_month

        card_exp_year = self.card_exp_year

        card_cvv = self.card_cvv

        card_zip = self.card_zip

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "card_full_name": card_full_name,
                "card_number": card_number,
                "card_exp_month": card_exp_month,
                "card_exp_year": card_exp_year,
                "card_cvv": card_cvv,
                "card_zip": card_zip,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        card_full_name = d.pop("card_full_name")

        card_number = d.pop("card_number")

        card_exp_month = d.pop("card_exp_month")

        card_exp_year = d.pop("card_exp_year")

        card_cvv = d.pop("card_cvv")

        card_zip = d.pop("card_zip")

        card_create = cls(
            card_full_name=card_full_name,
            card_number=card_number,
            card_exp_month=card_exp_month,
            card_exp_year=card_exp_year,
            card_cvv=card_cvv,
            card_zip=card_zip,
        )

        card_create.additional_properties = d
        return card_create

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
