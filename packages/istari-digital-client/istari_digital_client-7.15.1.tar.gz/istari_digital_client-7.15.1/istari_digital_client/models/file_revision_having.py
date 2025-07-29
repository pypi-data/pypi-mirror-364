import abc
from pydantic import BaseModel

from istari_digital_client.models.file_revision import FileRevision
from istari_digital_client.models.readable import Readable
from istari_digital_client.models.properties import Properties
from istari_digital_client.log_utils import log_method


class FileRevisionHaving(BaseModel, Readable, abc.ABC):
    @property
    @abc.abstractmethod
    def revision(self) -> FileRevision: ...

    @log_method
    def read_bytes(self) -> bytes:
        return self.revision.read_bytes()

    @property
    @log_method
    def properties(self) -> Properties:
        return self.revision.properties

    @property
    @log_method
    def extension(self) -> str | None:
        return self.revision.extension

    @property
    @log_method
    def name(self) -> str | None:
        if self.revision.name is None or self.extension is None:
            return None

        file_name = self.revision.name
        if file_name.lower().endswith(f".{self.extension}"):
            return file_name
        return ".".join([file_name, self.extension])

    @property
    @log_method
    def stem(self) -> str | None:
        return self.revision.stem

    @property
    @log_method
    def suffix(self) -> str | None:
        return self.revision.suffix

    @property
    @log_method
    def description(self) -> str | None:
        return self.revision.description

    @property
    @log_method
    def size(self) -> int | None:
        return self.revision.size

    @property
    @log_method
    def mime(self) -> str | None:
        return self.revision.mime

    @property
    @log_method
    def version_name(self) -> str | None:
        return self.revision.version_name

    @property
    @log_method
    def external_identifier(self) -> str | None:
        return self.revision.external_identifier

    @property
    @log_method
    def display_name(self) -> str | None:
        return self.revision.display_name
