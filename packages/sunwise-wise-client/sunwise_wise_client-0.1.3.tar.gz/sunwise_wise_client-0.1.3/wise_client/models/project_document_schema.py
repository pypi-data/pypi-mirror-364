from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.project_document_status import ProjectDocumentStatus

if TYPE_CHECKING:
    from ..models.completion_schema import CompletionSchema


T = TypeVar("T", bound="ProjectDocumentSchema")


@_attrs_define
class ProjectDocumentSchema:
    """
    Attributes:
        id (UUID):
        file (str):
        status (ProjectDocumentStatus): SUCCESS = 0

            PARTIALLY_SOLVED = 1

            UNSOLVED = 2

            FAILED = -1
        completion (Union['CompletionSchema', None]):
    """

    id: UUID
    file: str
    status: ProjectDocumentStatus
    completion: Union["CompletionSchema", None]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.completion_schema import CompletionSchema

        id = str(self.id)

        file = self.file

        status = self.status.value

        completion: Union[None, dict[str, Any]]
        if isinstance(self.completion, CompletionSchema):
            completion = self.completion.to_dict()
        else:
            completion = self.completion

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "file": file,
                "status": status,
                "completion": completion,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.completion_schema import CompletionSchema

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        file = d.pop("file")

        status = ProjectDocumentStatus(d.pop("status"))

        def _parse_completion(data: object) -> Union["CompletionSchema", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                completion_type_0 = CompletionSchema.from_dict(data)

                return completion_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CompletionSchema", None], data)

        completion = _parse_completion(d.pop("completion"))

        project_document_schema = cls(
            id=id,
            file=file,
            status=status,
            completion=completion,
        )

        project_document_schema.additional_properties = d
        return project_document_schema

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
