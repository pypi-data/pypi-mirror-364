from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Set
from typing_extensions import Self

from istari_digital_client.models.control_tag import ControlTag
from istari_digital_client.models.artifact import Artifact
from istari_digital_client.models.comment import Comment
from istari_digital_client.models.file import File
from istari_digital_client.models.job import Job
from istari_digital_client.models.resource_archive_status import ResourceArchiveStatus
from istari_digital_client.models.shareable import Shareable
from istari_digital_client.models.file_having import FileHaving
from istari_digital_client.models.archivable import Archivable
from istari_digital_client.models.client_having import ClientHaving
from istari_digital_client.log_utils import log_method
from istari_digital_client.models.json_type import JSON
from istari_digital_client.models.pathlike import PathLike
from istari_digital_client.models.new_source import NewSource


class Model(ClientHaving, FileHaving, Shareable, Archivable):
    """
    A class representing a model. Models have artifacts.
    """ # noqa: E501
    id: StrictStr
    created: datetime
    file: File
    comments: List[Comment]
    archive_status_history: List[ResourceArchiveStatus]
    created_by_id: StrictStr
    artifacts: List[Artifact]
    jobs: Optional[List[Job]] = None
    control_tags: Optional[List[ControlTag]] = None
    __client_fields__: ClassVar[List[str]] = ["file", "comments", "artifacts", "jobs"]
    __properties: ClassVar[List[str]] = ["id", "created", "file", "comments", "archive_status_history", "created_by_id", "artifacts", "jobs"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    @log_method
    def add_job(
        self,
        function: str,
        *,
        parameters: JSON | None = None,
        parameters_file: PathLike | None = None,
        tool_name: str | None = None,
        tool_version: str | None = None,
        operating_system: str | None = None,
        assigned_agent_id: str | None = None,
        agent_identifier: str | None = None,
        sources: list[NewSource | str] | None = None,
        description: str | None = None,
        version_name: str | None = None,
        external_identifier: str | None = None,
        display_name: str | None = None,
        **kwargs,
    ) -> Job:
        if not self.client:
            raise ValueError("Client is not set. Please set the client before calling this method.")

        return self.client.add_job(
            self.id,
            function,
            parameters,
            parameters_file,
            tool_name,
            tool_version,
            operating_system,
            assigned_agent_id,
            agent_identifier,
            sources,
            description,
            version_name,
            external_identifier,
            display_name,
            **kwargs,
        )

    @property
    @log_method
    def archive_status(self) -> ResourceArchiveStatus:
        return self.archive_status_history[-1]

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of Model from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of file
        if self.file:
            _dict['file'] = self.file.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in comments (list)
        _items = []
        if self.comments:
            for _item_comments in self.comments:
                if _item_comments:
                    _items.append(_item_comments.to_dict())
            _dict['comments'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in archive_status_history (list)
        _items = []
        if self.archive_status_history:
            for _item_archive_status_history in self.archive_status_history:
                if _item_archive_status_history:
                    _items.append(_item_archive_status_history.to_dict())
            _dict['archive_status_history'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in artifacts (list)
        _items = []
        if self.artifacts:
            for _item_artifacts in self.artifacts:
                if _item_artifacts:
                    _items.append(_item_artifacts.to_dict())
            _dict['artifacts'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in jobs (list)
        _items = []
        if self.jobs:
            for _item_jobs in self.jobs:
                if _item_jobs:
                    _items.append(_item_jobs.to_dict())
            _dict['jobs'] = _items

        # override the default output from pydantic by calling `to_dict()` of each item in control_tags (list)
        _items = []
        if self.control_tags:
            for _item_control_tags in self.control_tags:
                if _item_control_tags:
                    _items.append(_item_control_tags.to_dict())
            _dict['control_tags'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of Model from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "created": obj.get("created"),
            "file": File.from_dict(obj["file"]) if obj.get("file") is not None else None,
            "comments": [Comment.from_dict(_item) for _item in obj["comments"]] if obj.get("comments") is not None else None,
            "archive_status_history": [ResourceArchiveStatus.from_dict(_item) for _item in obj["archive_status_history"]] if obj.get("archive_status_history") is not None else None,
            "created_by_id": obj.get("created_by_id"),
            "artifacts": [Artifact.from_dict(_item) for _item in obj["artifacts"]] if obj.get("artifacts") is not None else None,
            "jobs": [Job.from_dict(_item) for _item in obj["jobs"]] if obj.get("jobs") is not None else None,
            "control_tags": [ControlTag.from_dict(_item) for _item in obj["control_tags"]] if obj.get("control_tags") is not None else None,
        })
        return _obj
