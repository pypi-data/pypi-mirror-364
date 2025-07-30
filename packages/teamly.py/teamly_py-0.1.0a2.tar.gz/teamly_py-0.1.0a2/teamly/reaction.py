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

from teamly.user import User




from .types.reaction import Reaction as ReactionPayload
from typing import TYPE_CHECKING, Mapping, List

if TYPE_CHECKING:
    from .state import ConnectionState
    from .message import Message
    from .abc import MessageAbleChannel

class PartialReaction:

    def __init__(self, data: dict) -> None:
        self._emoji_id: str = data.get('emojiId')
        self._count: int = data.get('count')
        self._users: List[dict] = data.get('users')

    @property
    def emojiId(self):
        return self._emoji_id

    @property
    def count(self):
        return self._count

    @property
    def users(self):
        return [[u.get('userId'),u.get('timestamp')] for u in self._users]

class Reaction:

    def __init__(
        self,
        *,
        state: ConnectionState,
        channel: MessageAbleChannel,
        message: Message,
        data: ReactionPayload
    ) -> None:
        self._state: ConnectionState = state
        self.channel: MessageAbleChannel = channel
        self.message: Message = message
        self._update(data)

    def _update(self, data: Mapping):
        self._emoji_id: str = data['emojiId']
        self.team_id: str = data['teamId']
        self.user: User = User(state=self._state, data=data['reactedBy'])

    @property
    def emojiId(self):
        return self._emoji_id

    def __repr__(self) -> str:
        return f"<Reaction emojiId={self._emoji_id} username={self.user.username}>"
