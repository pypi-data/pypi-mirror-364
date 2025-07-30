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

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from teamly.state import ConnectionState
    from .types.blog import Blog as BlogPayload
    from .team import Team

__all__ = [
    "Blog"
]


class Blog:

    __slots__ = (
        '_state',
        'id',
        'title',
        'content',
        '_created_at',
        '_created_by',
        '_edited_at',
        'team',
        '_hero_image'
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        team: Team,
        data: BlogPayload
    ) -> None:
        self._state: ConnectionState = state
        self.team: Team = team
        self._update(data)

    def _update(self, data: BlogPayload):
        self.id: str = data['id']
        self.title: str = data['title']
        self.content: str = data['content']

        self._created_at: str = data['createdAt']
        self._created_by: str = data['createdBy']
        self._edited_at: Optional[str] = data.get('editedAt')
        self._hero_image: Optional[str] = data.get('heroImage')

    @property
    def createdAt(self):
        return self._created_at

    @property
    def createdBy(self):
        return self._created_by

    @property
    def editedAt(self):
        return self._edited_at if self._edited_at else None

    @property
    def heroImage(self):
        return self._hero_image if self._hero_image else None



    def to_dict(self):
        result = {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "createdAt": self._created_at,
            "createdBy": self._created_by,
            "editedAt": self._edited_at,
            "teamId": self.team.id,
            "heroImage": self._hero_image
        }

        return result
