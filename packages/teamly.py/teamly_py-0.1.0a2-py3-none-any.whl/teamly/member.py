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

from datetime import datetime, timezone

from .user import _UserTag, User
from .types.member import Member as MemberPayload
from typing import TYPE_CHECKING, Dict, List, Mapping, Any, cast

if TYPE_CHECKING:
    from .state import ConnectionState
    from .user import UserPayload


class Member(User,_UserTag):

    def __init__(self,*, state: ConnectionState, data: MemberPayload) -> None:
        self._state: ConnectionState = state
        self._update(data)

    def _update(self, data: Mapping):
        super()._update(data)
        self.joined_at: str = data['joinedAt']
        self.roles: List[str] = data.get('roles', [])
        self.teamId: str = data['teamId']

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _UserTag) and other.id == self.id

    @classmethod
    def _new_member(cls,state: ConnectionState, data: UserPayload, teamId: str):

        member_data: Dict[str,Any] = dict(data)
        member_data['joinedAt'] = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
        member_data['roles'] = []
        member_data[teamId] = teamId

        return cls(state=state, data=cast(MemberPayload, member_data))

    def __repr__(self) -> str:
        return f"<Member username={self._user.username} joined_at={self.joined_at} roles={self.roles} teamId={self.teamId}>"
