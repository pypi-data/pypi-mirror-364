from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="BodyProjectsProjectsuploadDocuments")


@_attrs_define
class BodyProjectsProjectsuploadDocuments:
    """
    Attributes:
        files (list[File]):
        overwrite (Union[Unset, bool]):  Default: True.
        country (Union[Unset, str]):  Default: 'México'.
    """

    files: list[File]
    overwrite: Union[Unset, bool] = True
    country: Union[Unset, str] = "México"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            files.append(files_item)

        overwrite = self.overwrite

        country = self.country

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )
        if overwrite is not UNSET:
            field_dict["overwrite"] = overwrite
        if country is not UNSET:
            field_dict["country"] = country

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        for files_item_element in self.files:
            files.append(("files", files_item_element.to_tuple()))

        if not isinstance(self.overwrite, Unset):
            files.append(("overwrite", (None, str(self.overwrite).encode(), "text/plain")))

        if not isinstance(self.country, Unset):
            files.append(("country", (None, str(self.country).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = File(payload=BytesIO(files_item_data))

            files.append(files_item)

        overwrite = d.pop("overwrite", UNSET)

        country = d.pop("country", UNSET)

        body_projects_projectsupload_documents = cls(
            files=files,
            overwrite=overwrite,
            country=country,
        )

        body_projects_projectsupload_documents.additional_properties = d
        return body_projects_projectsupload_documents

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
