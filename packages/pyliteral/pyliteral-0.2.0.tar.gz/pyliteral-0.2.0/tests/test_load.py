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

"""
# tests/test_load.py
Tests for the `load` function in the pyliteral module.
This module tests loading Python literal expressions from various sources.
"""

import os
import tempfile
import pytest
from pathlib import Path
from io import StringIO

from pyliteral.load import load


# Sample data for testing
SAMPLE_DICT = '{"a": 1, "b": [2, 3], "c": None}'
SAMPLE_LIST = '[1, 2, 3]'


def test_load_from_file_path():
    with tempfile.NamedTemporaryFile('w+', delete=False, encoding='utf-8') as tmp:
        tmp.write(SAMPLE_DICT)
        tmp_path = tmp.name
    try:
        result = load(tmp_path)
        assert isinstance(result, dict)
        assert result["a"] == 1
        assert result["b"] == [2, 3]
        assert result["c"] is None
    finally:
        os.remove(tmp_path)


def test_load_from_path_object():
    with tempfile.NamedTemporaryFile('w+', delete=False, encoding='utf-8') as tmp:
        tmp.write(SAMPLE_LIST)
        tmp_path = Path(tmp.name)
    try:
        result = load(tmp_path)
        assert isinstance(result, list)
        assert result == [1, 2, 3]
    finally:
        os.remove(tmp_path)


def test_load_from_file_object():
    with tempfile.NamedTemporaryFile('w+', delete=False, encoding='utf-8') as tmp:
        tmp.write(SAMPLE_LIST)
    with open(tmp.name, 'r', encoding='utf-8') as file_obj:
        try:
            result = load(file_obj)
            assert isinstance(result, list)
            assert result == [1, 2, 3]
        finally:
            os.remove(tmp.name)


def test_load_from_StringIO_object():
    file_obj = StringIO(SAMPLE_DICT)
    result = load(file_obj)
    assert isinstance(result, dict)
    assert result["a"] == 1
    assert result["b"] == [2, 3]
    assert result["c"] is None


def test_load_invalid_type():
    with pytest.raises(TypeError):
        load(123) # type: ignore


def test_load_file_not_found():
    with pytest.raises(FileNotFoundError):
        load("/tmp/nonexistent_file_123456789.txt")


def test_load_permission_error(monkeypatch):
    # Simulate permission error by patching open
    def raise_permission(*args, **kwargs):
        raise PermissionError("Permission denied")
    monkeypatch.setattr("builtins.open", raise_permission)
    with pytest.raises(PermissionError):
        load("/tmp/should_fail.txt")
