from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.consumption_tier import ConsumptionTier
    from ..models.history_value import HistoryValue
    from ..models.values import Values


T = TypeVar("T", bound="CompletionSchema")


@_attrs_define
class CompletionSchema:
    """
    Attributes:
        rate (Union[None, Unset, str]):
        unit_prefix (Union[None, Unset, str]):  Default: 'k'.
        is_bimonthly (Union[None, Unset, bool]):
        zip_code (Union[None, Unset, str]):
        name (Union[None, Unset, str]):
        service_number (Union[None, Unset, str]):
        address (Union[None, Unset, str]):
        contracted_demand (Union[None, Unset, list['ConsumptionTier']]):
        values (Union['Values', None, Unset]):
        has_low_tension_concept (Union[None, Unset, bool]):  Default: False.
        applied_credit (Union[None, Unset, float]):  Default: 0.0.
        history (Union[None, Unset, list['HistoryValue']]):
    """

    rate: Union[None, Unset, str] = UNSET
    unit_prefix: Union[None, Unset, str] = "k"
    is_bimonthly: Union[None, Unset, bool] = UNSET
    zip_code: Union[None, Unset, str] = UNSET
    name: Union[None, Unset, str] = UNSET
    service_number: Union[None, Unset, str] = UNSET
    address: Union[None, Unset, str] = UNSET
    contracted_demand: Union[None, Unset, list["ConsumptionTier"]] = UNSET
    values: Union["Values", None, Unset] = UNSET
    has_low_tension_concept: Union[None, Unset, bool] = False
    applied_credit: Union[None, Unset, float] = 0.0
    history: Union[None, Unset, list["HistoryValue"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.values import Values

        rate: Union[None, Unset, str]
        if isinstance(self.rate, Unset):
            rate = UNSET
        else:
            rate = self.rate

        unit_prefix: Union[None, Unset, str]
        if isinstance(self.unit_prefix, Unset):
            unit_prefix = UNSET
        else:
            unit_prefix = self.unit_prefix

        is_bimonthly: Union[None, Unset, bool]
        if isinstance(self.is_bimonthly, Unset):
            is_bimonthly = UNSET
        else:
            is_bimonthly = self.is_bimonthly

        zip_code: Union[None, Unset, str]
        if isinstance(self.zip_code, Unset):
            zip_code = UNSET
        else:
            zip_code = self.zip_code

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        service_number: Union[None, Unset, str]
        if isinstance(self.service_number, Unset):
            service_number = UNSET
        else:
            service_number = self.service_number

        address: Union[None, Unset, str]
        if isinstance(self.address, Unset):
            address = UNSET
        else:
            address = self.address

        contracted_demand: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.contracted_demand, Unset):
            contracted_demand = UNSET
        elif isinstance(self.contracted_demand, list):
            contracted_demand = []
            for contracted_demand_type_0_item_data in self.contracted_demand:
                contracted_demand_type_0_item = contracted_demand_type_0_item_data.to_dict()
                contracted_demand.append(contracted_demand_type_0_item)

        else:
            contracted_demand = self.contracted_demand

        values: Union[None, Unset, dict[str, Any]]
        if isinstance(self.values, Unset):
            values = UNSET
        elif isinstance(self.values, Values):
            values = self.values.to_dict()
        else:
            values = self.values

        has_low_tension_concept: Union[None, Unset, bool]
        if isinstance(self.has_low_tension_concept, Unset):
            has_low_tension_concept = UNSET
        else:
            has_low_tension_concept = self.has_low_tension_concept

        applied_credit: Union[None, Unset, float]
        if isinstance(self.applied_credit, Unset):
            applied_credit = UNSET
        else:
            applied_credit = self.applied_credit

        history: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.history, Unset):
            history = UNSET
        elif isinstance(self.history, list):
            history = []
            for history_type_0_item_data in self.history:
                history_type_0_item = history_type_0_item_data.to_dict()
                history.append(history_type_0_item)

        else:
            history = self.history

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rate is not UNSET:
            field_dict["rate"] = rate
        if unit_prefix is not UNSET:
            field_dict["unit_prefix"] = unit_prefix
        if is_bimonthly is not UNSET:
            field_dict["is_bimonthly"] = is_bimonthly
        if zip_code is not UNSET:
            field_dict["zip_code"] = zip_code
        if name is not UNSET:
            field_dict["name"] = name
        if service_number is not UNSET:
            field_dict["service_number"] = service_number
        if address is not UNSET:
            field_dict["address"] = address
        if contracted_demand is not UNSET:
            field_dict["contracted_demand"] = contracted_demand
        if values is not UNSET:
            field_dict["values"] = values
        if has_low_tension_concept is not UNSET:
            field_dict["has_low_tension_concept"] = has_low_tension_concept
        if applied_credit is not UNSET:
            field_dict["applied_credit"] = applied_credit
        if history is not UNSET:
            field_dict["history"] = history

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.consumption_tier import ConsumptionTier
        from ..models.history_value import HistoryValue
        from ..models.values import Values

        d = dict(src_dict)

        def _parse_rate(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        rate = _parse_rate(d.pop("rate", UNSET))

        def _parse_unit_prefix(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        unit_prefix = _parse_unit_prefix(d.pop("unit_prefix", UNSET))

        def _parse_is_bimonthly(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_bimonthly = _parse_is_bimonthly(d.pop("is_bimonthly", UNSET))

        def _parse_zip_code(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        zip_code = _parse_zip_code(d.pop("zip_code", UNSET))

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_service_number(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        service_number = _parse_service_number(d.pop("service_number", UNSET))

        def _parse_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        address = _parse_address(d.pop("address", UNSET))

        def _parse_contracted_demand(data: object) -> Union[None, Unset, list["ConsumptionTier"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                contracted_demand_type_0 = []
                _contracted_demand_type_0 = data
                for contracted_demand_type_0_item_data in _contracted_demand_type_0:
                    contracted_demand_type_0_item = ConsumptionTier.from_dict(contracted_demand_type_0_item_data)

                    contracted_demand_type_0.append(contracted_demand_type_0_item)

                return contracted_demand_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["ConsumptionTier"]], data)

        contracted_demand = _parse_contracted_demand(d.pop("contracted_demand", UNSET))

        def _parse_values(data: object) -> Union["Values", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                values_type_0 = Values.from_dict(data)

                return values_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Values", None, Unset], data)

        values = _parse_values(d.pop("values", UNSET))

        def _parse_has_low_tension_concept(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        has_low_tension_concept = _parse_has_low_tension_concept(d.pop("has_low_tension_concept", UNSET))

        def _parse_applied_credit(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        applied_credit = _parse_applied_credit(d.pop("applied_credit", UNSET))

        def _parse_history(data: object) -> Union[None, Unset, list["HistoryValue"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                history_type_0 = []
                _history_type_0 = data
                for history_type_0_item_data in _history_type_0:
                    history_type_0_item = HistoryValue.from_dict(history_type_0_item_data)

                    history_type_0.append(history_type_0_item)

                return history_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["HistoryValue"]], data)

        history = _parse_history(d.pop("history", UNSET))

        completion_schema = cls(
            rate=rate,
            unit_prefix=unit_prefix,
            is_bimonthly=is_bimonthly,
            zip_code=zip_code,
            name=name,
            service_number=service_number,
            address=address,
            contracted_demand=contracted_demand,
            values=values,
            has_low_tension_concept=has_low_tension_concept,
            applied_credit=applied_credit,
            history=history,
        )

        completion_schema.additional_properties = d
        return completion_schema

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
