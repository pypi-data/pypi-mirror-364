import os
import abc
import json
from typing import TypeAlias, Union
from pathlib import Path

from istari_digital_client.log_utils import log_method

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
PathLike = Union[str, os.PathLike, Path]


class Readable(abc.ABC):
    @abc.abstractmethod
    def read_bytes(self) -> bytes: ...

    @log_method
    def read_text(self, encoding: str = "utf-8") -> str:
        return self.read_bytes().decode(encoding)

    @log_method
    def copy_to(self, dest: PathLike) -> Path:
        dest_path = Path(str(dest))
        dest_path.write_bytes(self.read_bytes())
        return dest_path

    @log_method
    def read_json(self, encoding: str = "utf-8") -> JSON:
        return json.loads(self.read_text(encoding=encoding))
