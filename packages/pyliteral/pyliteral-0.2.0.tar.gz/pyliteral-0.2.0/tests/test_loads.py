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
# tests/test_loads.py
This module tests loading Python literal expressions from various sources.
"""

import pytest
from pyliteral.loads import loads


SAMPLE_DICT = '{"a": 1, "b": [2, 3], "c": None}'

def test_loads_dict():
    result = loads(SAMPLE_DICT)
    assert isinstance(result, dict)
    assert result["a"] == 1
    assert result["b"] == [2, 3]
    assert result["c"] is None


def test_loads_list():
    s = '[1, 2, 3]'
    result = loads(s)
    assert isinstance(result, list)
    assert result == [1, 2, 3]


def test_loads_tuple():
    s = '(1, 2, 3)'
    result = loads(s)
    assert isinstance(result, tuple)
    assert result == (1, 2, 3)


def test_loads_str():
    s = '"hello"'
    result = loads(s)
    assert isinstance(result, str)
    assert result == "hello"


def test_loads_int():
    s = '42'
    result = loads(s)
    assert isinstance(result, int)
    assert result == 42


def test_loads_float():
    s = '3.14'
    result = loads(s)
    assert isinstance(result, float)
    assert result == 3.14


def test_loads_bool():
    s_true = 'True'
    s_false = 'False'
    assert loads(s_true) is True
    assert loads(s_false) is False


def test_loads_none():
    s = 'None'
    result = loads(s)
    assert result is None


def test_loads_invalid():
    with pytest.raises(Exception):
        loads('{invalid:}')


def test_loads_type_check():
    with pytest.raises(Exception):
        loads(123) # type: ignore


def test_loads_max_size_assertion():
    with pytest.raises(Exception):
        loads(SAMPLE_DICT, max_size=10)  # Exceeds max size of 10 characters
