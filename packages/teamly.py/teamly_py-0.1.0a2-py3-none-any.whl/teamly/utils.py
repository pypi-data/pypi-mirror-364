'''
MIT License

Copyright (c) 2025 Fatih Kuloglu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import aiohttp
import json
from pathlib import Path
from typing import Any


class _MissingSentinel:

    __slots__ = ()

    def __eq__(self, value: object, /) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __repr__(self) -> str:
        return '...'

MISSING: Any = _MissingSentinel()

@staticmethod
def _to_json(data: Any):
    return json.loads(data)

class FormDataBuilder:

    def __init__(
        self,
        file_path: str,
        *,
        field_name: str,
        type: str = "attachment"
    ) -> None:
        self.file_path: Path = Path(file_path)
        self.field_name: str = field_name
        self.type: str = type

    def build(self) -> aiohttp.FormData:
        if not self.file_path.exists() or not self.file_path.is_file():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        form = aiohttp.FormData()
        form.add_field(
            self.field_name,
            self.file_path.open('rb'),
            filename=self.name,
            content_type="application/octet-stream"
        )
        form.add_field('type', self.type)

        return form
