from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Set, Union
from typing_extensions import Self

from istari_digital_client.models.system_configuration import SystemConfiguration
from istari_digital_client.models.page_snapshot_revision_search_item import PageSnapshotRevisionSearchItem
from istari_digital_client.models.snapshot import Snapshot
from istari_digital_client.models.snapshot_tag import SnapshotTag
from istari_digital_client.models.shareable import Shareable
from istari_digital_client.models.archivable import Archivable
from istari_digital_client.models.client_having import ClientHaving
from istari_digital_client.log_utils import log_method


class System(BaseModel, ClientHaving, Shareable, Archivable):
    """
    System
    """ # noqa: E501
    id: StrictStr
    created: datetime
    created_by_id: StrictStr
    name: StrictStr
    description: StrictStr
    archive_status: StrictStr
    configurations: Optional[List[SystemConfiguration]] = None
    baseline_tagged_snapshot_id: Optional[StrictStr] = None
    __properties: ClassVar[List[str]] = ["id", "created", "created_by_id", "name", "description", "archive_status", "configurations", "baseline_tagged_snapshot_id"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    @log_method
    def list_file_revisions_by_snapshot(
            self,
            snapshot: Optional[Union[Snapshot | str]] = None,
            page: Optional[int] = None,
            size: Optional[int] = None,
            name: Optional[List[str]] = None,
            extension: Optional[List[str]] = None,
            sort: Optional[str] = None,
    ) -> PageSnapshotRevisionSearchItem:
        """
        Retrieves a list of File Revisions for a given snapshot.

        If no snapshot ID is provided, the baseline_tagged_snapshot_id will be used.

        :param snapshot: The snapshot to retrieve the file revision from.
        :type snapshot: Optional[Snapshot]
        :param page: The page number to retrieve.
        :type page: Optional[int]
        :param size: The number of items per page.
        :type size: Optional[int]
        :param name: List of file names to filter the revisions.
        :type name: Optional[List[str]]
        :param extension: List of file extensions to filter the revisions.
        :type extension: Optional[List[str]]
        :param sort: Sorting criteria for the revisions.
        :type sort: Optional[str]
        """

        if self.client is None:
            raise ValueError("Client is not set. Please set the client before calling this method.")

        if snapshot is None:
            snapshot_id = self.baseline_tagged_snapshot_id or self.client.get_system_baseline(system_id=self.id).snapshot_id
            if snapshot_id is None:
                raise ValueError("No snapshot provided and no baseline snapshot exists.")
        elif isinstance(snapshot, Snapshot):
            snapshot_id = snapshot.id
        elif isinstance(snapshot, str):
            snapshot_id = snapshot
        else:
            raise ValueError("Invalid type for snapshot. Must be Snapshot, str, or None.")

        return self.client.list_snapshot_revisions(
            snapshot_id=snapshot_id,
            page=page,
            size=size,
            name=name,
            extension=extension,
            sort=sort,
        )

    @log_method
    def list_file_revisions_by_snapshot_tag(
        self,
        snapshot_tag: SnapshotTag,
        page: Optional[int] = None,
        size: Optional[int] = None,
        name: Optional[List[str]] = None,
        extension: Optional[List[str]] = None,
        sort: Optional[str] = None,
    ) -> PageSnapshotRevisionSearchItem:
        """
        Retrieves a list of File Revisions for a given snapshot tag.
        :param snapshot_tag: The snapshot tag to retrieve the file revisions from.
        :type snapshot_tag: SnapshotTag
        :param page: The page number to retrieve.
        :type page: Optional[int]
        :param size: The number of items per page.
        :type size: Optional[int]
        :param name: List of file names to filter the revisions.
        :type name: Optional[List[str]]
        :param extension: List of file extensions to filter the revisions.
        :type extension: Optional[List[str]]
        :param sort: Sorting criteria for the revisions.
        :type sort: Optional[str]
        """
        if self.client is None:
            raise ValueError("Client is not set. Please set the client before calling this method.")

        return self.list_file_revisions_by_snapshot(
            snapshot=snapshot_tag.snapshot_id,
            page=page,
            size=size,
            name=name,
            extension=extension,
            sort=sort
        )

    @log_method
    def get_json_file_contents_by_snapshot(self, snapshot: Optional[Union[Snapshot]] = None) -> Dict[str, Any]:
        """
        Retrieves the contents of all JSON files for a given snapshot.

        If no snapshot ID is provided, the baseline_tagged_snapshot_id will be used.

        param snapshot: The Snapshot object to retrieve JSON files from.
        type snapshot: Optional[Union[Snapshot, str]]
        """
        if self.client is None:
            raise ValueError("Client is not set. Please set the client before calling this method.")

        if snapshot is None:
            baseline_snapshot_id = self.baseline_tagged_snapshot_id or self.client.get_system_baseline(system_id=self.id).snapshot_id
            if baseline_snapshot_id is None:
                raise ValueError("No snapshot provided and no baseline snapshot exists.")
            snapshot = self.client.get_snapshot(snapshot_id=baseline_snapshot_id)

        result: Dict[str, Any] = {"metadata": {
            "system_name": self.name,
            "system_id": self.id,
            "system_snapshot_id": snapshot.id,
            "system_snapshot_created": snapshot.created.isoformat(),
        }}

        snapshot_revision_items = self.list_file_revisions_by_snapshot(
            snapshot=snapshot,
            size=100,
            extension=[".json"]
        )

        for revision_item in snapshot_revision_items:
            if revision_item.name:
                result[revision_item.name] = revision_item.read_json()

        return result

    @log_method
    def get_json_file_contents_by_snapshot_tag(self, snapshot_tag: SnapshotTag) -> Dict[str, Any]:
        """
        Retrieves the contents of all JSON files for a given snapshot tag.

        param snapshot_tag: The SnapshotTag object containing the snapshot ID.
        type snapshot_tag: SnapshotTag
        """

        if self.client is None:
            raise ValueError("Client is not set. Please set the client before calling this method.")

        snapshot = self.client.get_snapshot(snapshot_id=snapshot_tag.snapshot_id)

        return self.get_json_file_contents_by_snapshot(snapshot=snapshot)

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of System from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in configurations (list)
        _items = []
        if self.configurations:
            for _item_configurations in self.configurations:
                if _item_configurations:
                    _items.append(_item_configurations.to_dict())
            _dict['configurations'] = _items
        # set to None if baseline_tagged_snapshot_id (nullable) is None
        # and model_fields_set contains the field
        if self.baseline_tagged_snapshot_id is None and "baseline_tagged_snapshot_id" in self.model_fields_set:
            _dict['baseline_tagged_snapshot_id'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of System from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "id": obj.get("id"),
            "created": obj.get("created"),
            "created_by_id": obj.get("created_by_id"),
            "name": obj.get("name"),
            "description": obj.get("description"),
            "archive_status": obj.get("archive_status"),
            "configurations": [SystemConfiguration.from_dict(_item) for _item in obj["configurations"]] if obj.get("configurations") is not None else None,
            "baseline_tagged_snapshot_id": obj.get("baseline_tagged_snapshot_id")
        })
        return _obj
