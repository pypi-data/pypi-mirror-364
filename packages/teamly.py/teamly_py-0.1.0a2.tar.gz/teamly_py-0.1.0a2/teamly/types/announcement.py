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

from typing import List, Optional, TypedDict

from teamly.user import User

class AnnouncementMedia(TypedDict):
    url: str

class AnnouncementEmojis(TypedDict):
    emojiId: str

class AnnouncementMentions(TypedDict):
    users: List[str]

class AnnouncementReactedUsers(TypedDict):
    userId: str
    timestamp: str

class AnnouncementReactions(TypedDict):
    emojiId: Optional[str]
    count: Optional[int]
    users: Optional[List[AnnouncementReactedUsers]]


class Announcement(TypedDict):
    id: str
    channelId: str
    title: str
    content: str
    createdBy: User
    attachments: Optional[List[AnnouncementMedia]]
    emojis: Optional[List[AnnouncementEmojis]]
    mentions: AnnouncementMentions
    reactions: List[AnnouncementReactions]
    createdAt: str
    editedAt: Optional[str]
