import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="HistoryValue")


@_attrs_define
class HistoryValue:
    """
    Attributes:
        initial_date (datetime.date):
        final_date (datetime.date):
        consumption (float):
        demand (Union[None, Unset, float]):
        fp (Union[None, Unset, float]):
    """

    initial_date: datetime.date
    final_date: datetime.date
    consumption: float
    demand: Union[None, Unset, float] = UNSET
    fp: Union[None, Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        initial_date = self.initial_date.isoformat()

        final_date = self.final_date.isoformat()

        consumption = self.consumption

        demand: Union[None, Unset, float]
        if isinstance(self.demand, Unset):
            demand = UNSET
        else:
            demand = self.demand

        fp: Union[None, Unset, float]
        if isinstance(self.fp, Unset):
            fp = UNSET
        else:
            fp = self.fp

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "initial_date": initial_date,
                "final_date": final_date,
                "consumption": consumption,
            }
        )
        if demand is not UNSET:
            field_dict["demand"] = demand
        if fp is not UNSET:
            field_dict["fp"] = fp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        initial_date = isoparse(d.pop("initial_date")).date()

        final_date = isoparse(d.pop("final_date")).date()

        consumption = d.pop("consumption")

        def _parse_demand(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        demand = _parse_demand(d.pop("demand", UNSET))

        def _parse_fp(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        fp = _parse_fp(d.pop("fp", UNSET))

        history_value = cls(
            initial_date=initial_date,
            final_date=final_date,
            consumption=consumption,
            demand=demand,
            fp=fp,
        )

        history_value.additional_properties = d
        return history_value

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
