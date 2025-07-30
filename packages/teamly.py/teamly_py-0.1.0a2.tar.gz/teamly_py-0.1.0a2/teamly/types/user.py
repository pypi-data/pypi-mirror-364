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

from typing import TYPE_CHECKING, List, Optional, TypedDict, Literal

if TYPE_CHECKING:
    from teamly.enums import Status

    StatusLiteral = Literal[Status.OFFLINE, Status.ONLINE, Status.IDLE, Status.DO_DO_DISTURB]

class UserRPC(TypedDict):
    type: Optional[str]
    name: Optional[str]
    id: Optional[str]
    startedAt: Optional[str]

class UserStatus(TypedDict):
    content: Optional[str]
    emojiId: Optional[str]

class Badges(TypedDict):
    id: str
    name: str
    icon: str

class User(TypedDict):
    id: str
    username: str
    subdomain: str
    profilePicture: Optional[str]
    banner: Optional[str]
    bot: bool
    presence: StatusLiteral
    flags: str
    badges: List[Badges]
    userStatus: Optional[UserRPC]
    userRPC: Optional[UserRPC]
    connections: List[str]
    createdAt: str
    system: bool
    verified: bool
    disabled: bool
