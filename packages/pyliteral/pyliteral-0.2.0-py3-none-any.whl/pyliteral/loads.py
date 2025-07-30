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

import ast

from .types import PYLTypes
from .consts import MAX_SIZE


def loads(s: str, max_size: int = MAX_SIZE) -> PYLTypes:
    """ Parse a Python literal expression from a string. """

    assert isinstance(s, str), "Input must be a string"
    assert len(s) <= max_size, f"Input exceeds maximum size of {max_size} characters"

    return ast.literal_eval(s)
