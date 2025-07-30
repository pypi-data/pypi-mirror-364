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


from .types.user import User as UserPayload
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Literal

if TYPE_CHECKING:
    from .state import ConnectionState
    from .enums import Status

    StatusLiteral = Literal[Status.OFFLINE, Status.ONLINE, Status.IDLE, Status.DO_DO_DISTURB]

__all__ = (
    "ClientUser",
    "User"
)

class _UserTag:
    __slots__ = ()
    id: str

class BaseUser(_UserTag):

    __slots__ = (
        "_state",
        "id",
        "username",
        "subdomain",
        "profile_picture",
        "banner",
        "bot",
        "presence",
        "flags",
        "badges",
        "_user_status",
        "user_rpc",
        "connections",
        "created_at",
        "system",
    )

    def __init__(self,*, state: ConnectionState, data: UserPayload) -> None:
        self._state = state
        self._update(data)

    def _update(self, data: UserPayload):
        self.id: str = data['id']
        self.username: str = data['username']
        self.subdomain: str = data.get('subdomain')
        self.profile_picture: Optional[str] = data.get('profilePicture', None)
        self.banner: Optional[str] = data.get('banner', None)

        self.bot: bool = data['bot']
        self.presence: StatusLiteral = data.get('presence', 0)
        self.flags: str = data['flags']
        self.badges: List[Dict[str,Any]] = data['badges']
        self._user_status: Optional[Dict[str,Any]] = data.get('userStatus', None)
        self.user_rpc: Optional[Dict[str,Any]] = data.get('userRPC', None)
        self.connections: List[str] = data.get('connections', [])
        self.created_at: str = data['createdAt']
        self.system: bool = data.get('system', False)


    def to_dict(self):
        payload = {
            "id": self.id,
            "username": self.username,
            "subdomain": self.subdomain,
            "profilePicture": self.profile_picture,
            "banner": self.banner,
            "bot": self.bot,
            "presence": self.presence,
            "flags": self.flags,
            "badges": self.badges,
            "userStatus": self._user_status,
            "userRPC": self.user_rpc,
            "connections": self.connections,
            "createdAt": self.created_at,
            "system": self.system
        }

        return payload

    def __repr__(self) -> str:
        return (
            f"<BaseUser id={self.id} username={self.username} subdomain={self.subdomain} "
            f"bot={self.bot} system={self.system}>"
        )

    def __eq__(self, other: object, /) -> bool:
        return isinstance(other, _UserTag) and self.id == other.id


class ClientUser(BaseUser):

    __slots__ = (
        "verified",
        "disabled",
        "last_online",
    )

    def __init__(self, *, state: ConnectionState, data: UserPayload) -> None:
        super().__init__(state=state, data=data)

    def _update(self, data: UserPayload):
        super()._update(data)

        self.verified: bool = data.get('verified', False)
        self.disabled: bool = data.get('disabled', False)
        self.last_online: str = data.get('lastOnline', None)

    def __repr__(self) -> str:
        return (
            f"<ClientUser id={self.id} username={self.username} subdoamin={self.subdomain} "
            f"bot={self.bot} system={self.system}>"
        )

class User(BaseUser):

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} username={self.username} subdomain={self.subdomain} "
            f"bot={self.bot} system={self.system}>"
        )
