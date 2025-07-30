# Copyright 2025 Sreenath Somarajapuram

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
from typing import Union, Generator, Protocol, runtime_checkable
from contextlib import contextmanager

from .types import PYLTypes
from .loads import loads
from .consts import MAX_SIZE


@runtime_checkable
class FileLike(Protocol):
    def read(self, *args, **kwargs) -> str: ...
    """Method to read from the file-like object."""

@contextmanager
def _get_file(f: Union[str, Path, FileLike]) -> Generator[FileLike, None, None]:
    """
    Context manager to handle both file paths and file-like objects.

    Args:
        file: A string path, Path object, or file-like object

    Yields:
        FileLike: A file-like object ready to be read

    Raises:
        TypeError: If the input is not a string path or file-like object
        FileNotFoundError: If the file path doesn't exist
        PermissionError: If the file can't be read due to permissions
    """
    if isinstance(f, (str, Path)):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                yield file
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"File not found: {f}") from exc
        except PermissionError as exc:
            raise PermissionError(f"Permission denied to read file: {f}") from exc
    elif isinstance(f, FileLike):
        yield f
    else:
        raise TypeError("Expected a file path (str or Path) or a file-like object")


def load(f: Union[str, Path, FileLike], max_size: int = MAX_SIZE) -> PYLTypes:
    """
    Load and parse a Python literal expression from a file.

    Args:
        file: A file path (as string or Path) or a file-like object containing the Python literal

    Returns:
        The Python object represented by the literal expression

    Raises:
        TypeError: If the input is not a string path or file-like object
        FileNotFoundError: If the file path doesn't exist
        PermissionError: If the file can't be read due to permissions
        ValueError: If the content cannot be parsed as a Python literal
    """
    with _get_file(f) as file:
        content = file.read(max_size)
        return loads(content, max_size=max_size)
