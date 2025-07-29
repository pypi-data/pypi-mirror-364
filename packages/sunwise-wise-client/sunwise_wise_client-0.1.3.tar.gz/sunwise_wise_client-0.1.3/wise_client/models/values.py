import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.consumption_tier import ConsumptionTier


T = TypeVar("T", bound="Values")


@_attrs_define
class Values:
    """
    Attributes:
        initial_date (Union[None, Unset, datetime.date]):
        final_date (Union[None, Unset, datetime.date]):
        energy (Union[None, Unset, list['ConsumptionTier']]):
        demand (Union[None, Unset, list['ConsumptionTier']]):
        fp (Union[None, Unset, float]):
        solar_generation (Union[None, Unset, float]):
        season_change (Union[None, Unset, bool]):  Default: False.
    """

    initial_date: Union[None, Unset, datetime.date] = UNSET
    final_date: Union[None, Unset, datetime.date] = UNSET
    energy: Union[None, Unset, list["ConsumptionTier"]] = UNSET
    demand: Union[None, Unset, list["ConsumptionTier"]] = UNSET
    fp: Union[None, Unset, float] = UNSET
    solar_generation: Union[None, Unset, float] = UNSET
    season_change: Union[None, Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        initial_date: Union[None, Unset, str]
        if isinstance(self.initial_date, Unset):
            initial_date = UNSET
        elif isinstance(self.initial_date, datetime.date):
            initial_date = self.initial_date.isoformat()
        else:
            initial_date = self.initial_date

        final_date: Union[None, Unset, str]
        if isinstance(self.final_date, Unset):
            final_date = UNSET
        elif isinstance(self.final_date, datetime.date):
            final_date = self.final_date.isoformat()
        else:
            final_date = self.final_date

        energy: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.energy, Unset):
            energy = UNSET
        elif isinstance(self.energy, list):
            energy = []
            for energy_type_0_item_data in self.energy:
                energy_type_0_item = energy_type_0_item_data.to_dict()
                energy.append(energy_type_0_item)

        else:
            energy = self.energy

        demand: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.demand, Unset):
            demand = UNSET
        elif isinstance(self.demand, list):
            demand = []
            for demand_type_0_item_data in self.demand:
                demand_type_0_item = demand_type_0_item_data.to_dict()
                demand.append(demand_type_0_item)

        else:
            demand = self.demand

        fp: Union[None, Unset, float]
        if isinstance(self.fp, Unset):
            fp = UNSET
        else:
            fp = self.fp

        solar_generation: Union[None, Unset, float]
        if isinstance(self.solar_generation, Unset):
            solar_generation = UNSET
        else:
            solar_generation = self.solar_generation

        season_change: Union[None, Unset, bool]
        if isinstance(self.season_change, Unset):
            season_change = UNSET
        else:
            season_change = self.season_change

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if initial_date is not UNSET:
            field_dict["initial_date"] = initial_date
        if final_date is not UNSET:
            field_dict["final_date"] = final_date
        if energy is not UNSET:
            field_dict["energy"] = energy
        if demand is not UNSET:
            field_dict["demand"] = demand
        if fp is not UNSET:
            field_dict["fp"] = fp
        if solar_generation is not UNSET:
            field_dict["solar_generation"] = solar_generation
        if season_change is not UNSET:
            field_dict["season_change"] = season_change

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.consumption_tier import ConsumptionTier

        d = dict(src_dict)

        def _parse_initial_date(data: object) -> Union[None, Unset, datetime.date]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                initial_date_type_0 = isoparse(data).date()

                return initial_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.date], data)

        initial_date = _parse_initial_date(d.pop("initial_date", UNSET))

        def _parse_final_date(data: object) -> Union[None, Unset, datetime.date]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                final_date_type_0 = isoparse(data).date()

                return final_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.date], data)

        final_date = _parse_final_date(d.pop("final_date", UNSET))

        def _parse_energy(data: object) -> Union[None, Unset, list["ConsumptionTier"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                energy_type_0 = []
                _energy_type_0 = data
                for energy_type_0_item_data in _energy_type_0:
                    energy_type_0_item = ConsumptionTier.from_dict(energy_type_0_item_data)

                    energy_type_0.append(energy_type_0_item)

                return energy_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["ConsumptionTier"]], data)

        energy = _parse_energy(d.pop("energy", UNSET))

        def _parse_demand(data: object) -> Union[None, Unset, list["ConsumptionTier"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                demand_type_0 = []
                _demand_type_0 = data
                for demand_type_0_item_data in _demand_type_0:
                    demand_type_0_item = ConsumptionTier.from_dict(demand_type_0_item_data)

                    demand_type_0.append(demand_type_0_item)

                return demand_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["ConsumptionTier"]], data)

        demand = _parse_demand(d.pop("demand", UNSET))

        def _parse_fp(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        fp = _parse_fp(d.pop("fp", UNSET))

        def _parse_solar_generation(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        solar_generation = _parse_solar_generation(d.pop("solar_generation", UNSET))

        def _parse_season_change(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        season_change = _parse_season_change(d.pop("season_change", UNSET))

        values = cls(
            initial_date=initial_date,
            final_date=final_date,
            energy=energy,
            demand=demand,
            fp=fp,
            solar_generation=solar_generation,
            season_change=season_change,
        )

        values.additional_properties = d
        return values

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
