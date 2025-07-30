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

import teamly.abc
from teamly.todo import TodoItem

from .enums import ChannelType

from .types.channel import (
    TextChannel as TextChannelPayload,
    DMChannel as DMChannelPayload,
    VoiceChannel as VoiceChannelPayload,
    AnnouncementChannel as AnnouncementChannelPayload,
    TodoChannel as TodoChannelPayload
)
from typing import TYPE_CHECKING, Dict, Any, List, Optional

if TYPE_CHECKING:
    from .state import ConnectionState
    from .team import Team


__all__ = [
    'TextChannel',
    'DMChannel',
    'VoiceChannel',
    'AnnouncementChannel',
    'TodoChannel'
]

class TextChannel(teamly.abc.MessageAble):

    __slots__ = (
        '_state',
        'team',
        'id',
        'type',
        'name',
        'description',
        'created_by',
        'parent_id',
        'priority',
        'rate_limit_per_user',
        'created_at',
        'permissions',
        'additional_data'
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        team: Team,
        data: TextChannelPayload
    ) -> None:
        self._state: ConnectionState = state
        self.team: Team = team
        self._update(data)

    def _update(self, data: TextChannelPayload):
        self.id: str = data['id']
        self.type: str = data['type']
        self.name: str = data['name']

        self.description: Optional[str] = data.get('description', None)
        self.created_by: str = data.get('createdBy')
        self.parent_id: Optional[str] = data.get('parentId', None)
        self.priority: int = data['priority']
        self.rate_limit_per_user: int = data['rateLimitPerUser']
        self.created_at: str = data['createdAt']
        self.permissions: Dict[str,Any] = data['permissions'].get('role', {})
        self.additional_data: Dict[str,Any] = data.get('additionalData', {})


    def __repr__(self) -> str:
        return f"<TextChannel id={self.id} name={self.name!r} type={self.type} teamId={self.team.id}>"

    async def delete_message(self, messageId: str):
        return await self._state.http.delete_message(self.id, messageId)

    async def react_message(self, messageId: str, emojiId: str):
        return await self._state.http.react_to_message(self.id, messageId, emojiId)


class DMChannel:

    def __init__(self, state: ConnectionState, data: DMChannelPayload) -> None:
        self._state: ConnectionState = state
        

class VoiceChannel:

    __slots__ = (
        '_state',
        'team',
        'id',
        'type',
        'name',
        'description',
        'created_by',
        'parent_id',
        'priority',
        '_participants',
        'created_at',
        'permissions',
        'additional_data'
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        team: Team,
        data: VoiceChannelPayload
    ) -> None:
        self._state: ConnectionState = state
        self.team: Team = team
        self._update(data)

    def _update(self, data: VoiceChannelPayload):
        self.id: str = data['id']
        self.type: str = data['type']
        self.name: str = data['name']

        self.description: Optional[str] = data.get('description', None)
        self.created_by: str = data.get('createdBy')
        self.parent_id: Optional[str] = data.get('parentId', None)
        self.priority: int = data['priority']
        self._participants: List[Dict[str,str]] = data.get('participants', [])
        self.created_at: str = data['createdAt']
        self.permissions: Dict[str,Any] = data['permissions'].get('role', {})
        self.additional_data: Dict[str,Any] = data.get('additionalData', {})

    @property
    def participants(self):
        return [p.get('id') for p in self._participants if self._participants] if self._participants else []


    def __repr__(self) -> str:
        return f"<VoiceChannel id={self.id} name={self.name!r} type={self.type} teamId={self.team.id}>"


class AnnouncementChannel:

    __slots__ = (
        '_state',
        'team',
        'id',
        'type',
        'name',
        'description',
        'created_by',
        'parent_id',
        'priority',
        'rate_limit_per_user',
        'created_at',
        'permissions',
        'additional_data'
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        team: Team,
        data: AnnouncementChannelPayload
    ) -> None:
        self._state: ConnectionState = state
        self.team: Team = team
        self._update(data)

    def _update(self, data: AnnouncementChannelPayload):
        self.id: str = data['id']
        self.type: str = data['type']
        self.name: str = data['name']

        self.description: Optional[str] = data.get('description', None)
        self.created_by: str = data.get('createdBy')
        self.parent_id: Optional[str] = data.get('parentId', None)
        self.priority: int = data['priority']
        self.created_at: str = data['createdAt']
        self.permissions: Dict[str,Any] = data['permissions'].get('role', {})
        self.additional_data: Dict[str,Any] = data.get('additionalData', {})

    def __repr__(self) -> str:
        return f"<VoiceChannel id={self.id} name={self.name!r} type={self.type} teamId={self.team.id}>"

class TodoChannel:
    def __init__(
        self,
        *,
        state: ConnectionState,
        team: Team,
        data: TodoChannelPayload
    ) -> None:
        self._state: ConnectionState = state
        self.team: Team = team
        self._update(data)

    def _update(self, data: TodoChannelPayload):
        self.id: str = data['id']
        self.type: str = data['type']
        self.name: str = data['name']

        self.description: Optional[str] = data.get('description', None)
        self.created_by: str = data.get('createdBy')
        self.parent_id: Optional[str] = data.get('parentId', None)
        self.priority: int = data['priority']
        self.created_at: str = data['createdAt']
        self.permissions: Dict[str,Any] = data['permissions'].get('role', {})
        self.additional_data: Dict[str,Any] = data.get('additionalData', {})

    async def fetch_todoitems(self):
        return self._state.http.get_todo_items(channelId=self.id)

    async def create_todo(self, content: str):
        if len(content) >= 256:
            raise ValueError("Content is too long, max 256 characters")

        todo = await self._state.http.create_todo_item(channelId=self.id, content=content)
        return TodoItem(state=self._state, channel=self, data=todo['todo'])

    async def delete_todo(self, todoId: str):
        return await self._state.http.delete_todo_item(channelId=self.id, todoId=todoId)

    async def clone_todoitem(self, todoId: str):
        clone = await self._state.http.clone_todo_item(channelId=self.id, todoId=todoId)
        return TodoItem(state=self._state,channel=self,data=clone['todo'])


    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<TodoChannel id={self.id} name={self.name!r} type={self.type} teamId={self.team.id}>"


class WatchStreamChannel:
    def __init__(
        self,
        *,
        state: ConnectionState,
        team: Team,
        data: TodoChannelPayload
    ) -> None:
        self._state: ConnectionState = state
        self.team: Team = team
        self._update(data)

    def _update(self, data: TodoChannelPayload):
        self.id: str = data['id']
        self.type: str = data['type']
        self.name: str = data['name']

        self.description: Optional[str] = data.get('description', None)
        self.created_by: str = data.get('createdBy')
        self.parent_id: Optional[str] = data.get('parentId', None)
        self.priority: int = data['priority']
        self.created_at: str = data['createdAt']
        self.permissions: Dict[str,Any] = data['permissions'].get('role', {})
        self.additional_data: Dict[str,Any] = data.get('additionalData', {})

    def __repr__(self) -> str:
        return f"<WatchStreamChannel id={self.id} name={self.name!r} type={self.type} teamId={self.team.id}>"


@staticmethod
def _channel_factory(type: str) -> Any | None:
    if ChannelType.TEXT == type:
        return TextChannel
    elif ChannelType.VOICE == type:
        return VoiceChannel
    elif ChannelType.ANNOUNCEMENT == type:
        return AnnouncementChannel
    elif ChannelType.TODO == type:
        return TodoChannel
    elif ChannelType.WATCHSTREAM == type:
        return WatchStreamChannel
    else:
        return None
