import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.consumption_tier import ConsumptionTier
    from ..models.history_value import HistoryValue
    from ..models.lisa_schema_values import LisaSchemaValues


T = TypeVar("T", bound="LisaSchema")


@_attrs_define
class LisaSchema:
    """
    Attributes:
        rate (str):
        initial_date (datetime.date):
        final_date (datetime.date):
        service_number (str):
        name (Union[None, str]):
        zip_code (Union[None, str]):
        address (Union[None, str]):
        rate_dom (Union[Unset, str]):  Default: ''.
        connected_load (Union[None, Unset, str]):  Default: ''.
        contracted_demand (Union[None, Unset, list['ConsumptionTier']]):
        has_low_tension_concept (Union[None, Unset, bool]):  Default: False.
        summer (Union[None, Unset, str]):  Default: ''.
        neighborhood (Union[None, Unset, str]):  Default: ''.
        street1 (Union[None, Unset, str]):  Default: ''.
        street2 (Union[None, Unset, str]):  Default: ''.
        dp2 (Union[Unset, str]):  Default: ''.
        dp1 (Union[Unset, str]):  Default: ''.
        rmu (Union[None, Unset, str]):
        subsidy_rate (Union[None, Unset, str]):
        division (Union[None, Unset, str]):
        values (Union['LisaSchemaValues', None, Unset]):
        is_bimonthly (Union[None, Unset, bool]):
        history (Union[None, Unset, list['HistoryValue']]):
    """

    rate: str
    initial_date: datetime.date
    final_date: datetime.date
    service_number: str
    name: Union[None, str]
    zip_code: Union[None, str]
    address: Union[None, str]
    rate_dom: Union[Unset, str] = ""
    connected_load: Union[None, Unset, str] = ""
    contracted_demand: Union[None, Unset, list["ConsumptionTier"]] = UNSET
    has_low_tension_concept: Union[None, Unset, bool] = False
    summer: Union[None, Unset, str] = ""
    neighborhood: Union[None, Unset, str] = ""
    street1: Union[None, Unset, str] = ""
    street2: Union[None, Unset, str] = ""
    dp2: Union[Unset, str] = ""
    dp1: Union[Unset, str] = ""
    rmu: Union[None, Unset, str] = UNSET
    subsidy_rate: Union[None, Unset, str] = UNSET
    division: Union[None, Unset, str] = UNSET
    values: Union["LisaSchemaValues", None, Unset] = UNSET
    is_bimonthly: Union[None, Unset, bool] = UNSET
    history: Union[None, Unset, list["HistoryValue"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.lisa_schema_values import LisaSchemaValues

        rate = self.rate

        initial_date = self.initial_date.isoformat()

        final_date = self.final_date.isoformat()

        service_number = self.service_number

        name: Union[None, str]
        name = self.name

        zip_code: Union[None, str]
        zip_code = self.zip_code

        address: Union[None, str]
        address = self.address

        rate_dom = self.rate_dom

        connected_load: Union[None, Unset, str]
        if isinstance(self.connected_load, Unset):
            connected_load = UNSET
        else:
            connected_load = self.connected_load

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

        has_low_tension_concept: Union[None, Unset, bool]
        if isinstance(self.has_low_tension_concept, Unset):
            has_low_tension_concept = UNSET
        else:
            has_low_tension_concept = self.has_low_tension_concept

        summer: Union[None, Unset, str]
        if isinstance(self.summer, Unset):
            summer = UNSET
        else:
            summer = self.summer

        neighborhood: Union[None, Unset, str]
        if isinstance(self.neighborhood, Unset):
            neighborhood = UNSET
        else:
            neighborhood = self.neighborhood

        street1: Union[None, Unset, str]
        if isinstance(self.street1, Unset):
            street1 = UNSET
        else:
            street1 = self.street1

        street2: Union[None, Unset, str]
        if isinstance(self.street2, Unset):
            street2 = UNSET
        else:
            street2 = self.street2

        dp2 = self.dp2

        dp1 = self.dp1

        rmu: Union[None, Unset, str]
        if isinstance(self.rmu, Unset):
            rmu = UNSET
        else:
            rmu = self.rmu

        subsidy_rate: Union[None, Unset, str]
        if isinstance(self.subsidy_rate, Unset):
            subsidy_rate = UNSET
        else:
            subsidy_rate = self.subsidy_rate

        division: Union[None, Unset, str]
        if isinstance(self.division, Unset):
            division = UNSET
        else:
            division = self.division

        values: Union[None, Unset, dict[str, Any]]
        if isinstance(self.values, Unset):
            values = UNSET
        elif isinstance(self.values, LisaSchemaValues):
            values = self.values.to_dict()
        else:
            values = self.values

        is_bimonthly: Union[None, Unset, bool]
        if isinstance(self.is_bimonthly, Unset):
            is_bimonthly = UNSET
        else:
            is_bimonthly = self.is_bimonthly

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
        field_dict.update(
            {
                "rate": rate,
                "initial_date": initial_date,
                "final_date": final_date,
                "service_number": service_number,
                "name": name,
                "zip_code": zip_code,
                "address": address,
            }
        )
        if rate_dom is not UNSET:
            field_dict["rate_dom"] = rate_dom
        if connected_load is not UNSET:
            field_dict["connected_load"] = connected_load
        if contracted_demand is not UNSET:
            field_dict["contracted_demand"] = contracted_demand
        if has_low_tension_concept is not UNSET:
            field_dict["has_low_tension_concept"] = has_low_tension_concept
        if summer is not UNSET:
            field_dict["summer"] = summer
        if neighborhood is not UNSET:
            field_dict["neighborhood"] = neighborhood
        if street1 is not UNSET:
            field_dict["street1"] = street1
        if street2 is not UNSET:
            field_dict["street2"] = street2
        if dp2 is not UNSET:
            field_dict["dp2"] = dp2
        if dp1 is not UNSET:
            field_dict["dp1"] = dp1
        if rmu is not UNSET:
            field_dict["rmu"] = rmu
        if subsidy_rate is not UNSET:
            field_dict["subsidy_rate"] = subsidy_rate
        if division is not UNSET:
            field_dict["division"] = division
        if values is not UNSET:
            field_dict["values"] = values
        if is_bimonthly is not UNSET:
            field_dict["is_bimonthly"] = is_bimonthly
        if history is not UNSET:
            field_dict["history"] = history

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.consumption_tier import ConsumptionTier
        from ..models.history_value import HistoryValue
        from ..models.lisa_schema_values import LisaSchemaValues

        d = dict(src_dict)
        rate = d.pop("rate")

        initial_date = isoparse(d.pop("initial_date")).date()

        final_date = isoparse(d.pop("final_date")).date()

        service_number = d.pop("service_number")

        def _parse_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        name = _parse_name(d.pop("name"))

        def _parse_zip_code(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        zip_code = _parse_zip_code(d.pop("zip_code"))

        def _parse_address(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        address = _parse_address(d.pop("address"))

        rate_dom = d.pop("rate_dom", UNSET)

        def _parse_connected_load(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        connected_load = _parse_connected_load(d.pop("connected_load", UNSET))

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

        def _parse_has_low_tension_concept(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        has_low_tension_concept = _parse_has_low_tension_concept(d.pop("has_low_tension_concept", UNSET))

        def _parse_summer(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        summer = _parse_summer(d.pop("summer", UNSET))

        def _parse_neighborhood(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        neighborhood = _parse_neighborhood(d.pop("neighborhood", UNSET))

        def _parse_street1(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        street1 = _parse_street1(d.pop("street1", UNSET))

        def _parse_street2(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        street2 = _parse_street2(d.pop("street2", UNSET))

        dp2 = d.pop("dp2", UNSET)

        dp1 = d.pop("dp1", UNSET)

        def _parse_rmu(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        rmu = _parse_rmu(d.pop("rmu", UNSET))

        def _parse_subsidy_rate(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        subsidy_rate = _parse_subsidy_rate(d.pop("subsidy_rate", UNSET))

        def _parse_division(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        division = _parse_division(d.pop("division", UNSET))

        def _parse_values(data: object) -> Union["LisaSchemaValues", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                values_type_0 = LisaSchemaValues.from_dict(data)

                return values_type_0
            except:  # noqa: E722
                pass
            return cast(Union["LisaSchemaValues", None, Unset], data)

        values = _parse_values(d.pop("values", UNSET))

        def _parse_is_bimonthly(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_bimonthly = _parse_is_bimonthly(d.pop("is_bimonthly", UNSET))

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

        lisa_schema = cls(
            rate=rate,
            initial_date=initial_date,
            final_date=final_date,
            service_number=service_number,
            name=name,
            zip_code=zip_code,
            address=address,
            rate_dom=rate_dom,
            connected_load=connected_load,
            contracted_demand=contracted_demand,
            has_low_tension_concept=has_low_tension_concept,
            summer=summer,
            neighborhood=neighborhood,
            street1=street1,
            street2=street2,
            dp2=dp2,
            dp1=dp1,
            rmu=rmu,
            subsidy_rate=subsidy_rate,
            division=division,
            values=values,
            is_bimonthly=is_bimonthly,
            history=history,
        )

        lisa_schema.additional_properties = d
        return lisa_schema

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
