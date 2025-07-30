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

from teamly.reaction import PartialReaction
from teamly.user import User
from .types.announcement import (
    Announcement as AnnouncementPayload,
    AnnouncementEmojis,
    AnnouncementMedia,
    AnnouncementMentions,
    AnnouncementReactions as AnnouncementReactionsPayload)
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .state import ConnectionState
    from .channel import AnnouncementChannel


class Announcement:

    def __init__(
        self,
        *,
        state: ConnectionState,
        channel: AnnouncementChannel,
        data: AnnouncementPayload
    ) -> None:
        self._state: ConnectionState = state
        self.channel = channel
        self._update(data=data)

    def _update(self, data: AnnouncementPayload):
        self.id: str = data['id']
        self.title: str = data['title']
        self.content: str = data['content']

        self._created_by: User = User(state=self._state, data=data['createdBy'])
        self._attachments: Optional[List[AnnouncementMedia]] = data.get('attachments')
        self._emojis: Optional[List[AnnouncementEmojis]] = data.get('emojis')
        self._mentions: Optional[AnnouncementMentions] = data.get('mentions')
        self._reactions: Optional[List[AnnouncementReactionsPayload]] = data.get('reactions')

        self._created_at: str = data['createdAt']
        self._edited_at: Optional[str] = data.get('editedAt')

    @property
    def user(self):
        return self._created_by

    @property
    def attachments(self):
        if self._attachments:
            return [x.get('url') for x in self._attachments]
        else:
            return []

    @property
    def emojis(self):
        if self._emojis:
            return [x.get('emojis') for x in self._emojis]
        else:
            return []

    @property
    def mentions(self):
        if self._mentions:
            return self._mentions['users']
        else:
            return []

    @property
    def reactions(self):
        if self._reactions:
            return [PartialReaction(r) for r in self._reactions]
        else:
            return []

    @property
    def createdAt(self):
        return self._created_at

    @property
    def editedAt(self):
        return self._edited_at

    def __repr__(self) -> str:
        return f"<Announcement id={self.id} title={self.title!r} channelId={self.channel.id}>"
