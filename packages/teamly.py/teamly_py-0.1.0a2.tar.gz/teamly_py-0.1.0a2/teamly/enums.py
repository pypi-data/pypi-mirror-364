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


from enum import Enum, IntFlag


class ChannelType(str, Enum):
    TEXT = 'text'
    VOICE = 'voice'
    TODO = 'todo'
    WATCHSTREAM = 'watchstream'
    ANNOUNCEMENT = 'announcement'

    def __str__(self) -> str:
        return self.value


class Status(int,Enum):
    OFFLINE = 0
    ONLINE = 1
    IDLE = 2
    DO_DO_DISTURB = 3

class AppStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return self.value

class Permissions(IntFlag):
    ADMINISTRATOR = 1 << 0
    MANAGE_CHANNELS = 1 << 1
    MANAGE_ROLES = 1 << 2
    MANAGE_TEAM = 1 << 3
    VIEW_AUDIT_LOG = 1 << 4
    BAN_MEMBERS = 1 << 5
    DELETE_MESSAGES = 1 << 6
    MANAGE_APPLICATIONS = 1 << 7
    JOIN_TOURNAMENTS = 1 << 8
    CREATE_INVITES = 1 << 9
    MENTION_EVERYONE_AND_HERE = 1 << 10
    MANAGE_BLOGS = 1 << 11
    KICK_MEMBERS = 1 << 12
    MOVE_MEMBERS = 1 << 13
