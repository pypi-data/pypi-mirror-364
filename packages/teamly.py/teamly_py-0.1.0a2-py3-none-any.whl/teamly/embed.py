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

from typing import Optional, Dict

from .color import Color


class Embed:

    __slots__ = (
        "title",
        "description",
        "url",
        "color",
        "_author",
        "_thumbnail",
        "_image",
        "_footer",
    )

    def __init__(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        color: Optional[Color] = None
    ):
        if title and len(title) > 16:
            raise ValueError("title must be 16 characters or fewer")
        if description and len(description) > 1024:
            raise ValueError("description must be 1024 characters or fewer")

        self.title = title
        self.description = description
        self.url = url
        self.color = int(color) if color else None

        self._author: Optional[Dict[str, str]] = None
        self._thumbnail: Optional[Dict[str, str]] = None
        self._image: Optional[Dict[str, str]] = None
        self._footer: Optional[Dict[str, str]] = None

    @property
    def author(self) -> Dict[str,str] | None:
        return self._author if self._author else None

    @property
    def thumbnail(self) -> str | None:
        return self._thumbnail['url'] if self._thumbnail else None

    @property
    def image(self) -> str | None:
        return self._image['url'] if self._image else None

    @property
    def footer(self) -> Dict[str,str] | None:
        return self._footer if self._footer else None

    def set_author(self, *, name: Optional[str] = None, icon_url: Optional[str] = None):
        self._author = {}
        if name:
            self._author["name"] = name
        if icon_url:
            self._author["icon_url"] = icon_url
        return self

    def set_thumbnail(self, *, url: str):
        self._thumbnail = {"url": url}
        return self

    def set_image(self, *, url: str):
        self._image = {"url": url}
        return self

    def set_footer(self, *, text: Optional[str] = None, icon_url: Optional[str] = None):
        self._footer = {}
        if text:
            self._footer["text"] = text
        if icon_url:
            self._footer["icon_url"] = icon_url
        return self

    def to_dict(self) -> Dict:
        data = {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "color": self.color,
            "author": self._author,
            "thumbnail": self._thumbnail,
            "image": self._image,
            "footer": self._footer,
        }
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict):
        self = cls.__new__(cls)

        self.title = data.get('title')
        self.description = data.get('description')
        self.url = data.get('url')
        self._author = data.get('author')
        self._thumbnail = data.get('thumbnail')
        self._image = data.get('image')
        self._footer = data.get('footer')
