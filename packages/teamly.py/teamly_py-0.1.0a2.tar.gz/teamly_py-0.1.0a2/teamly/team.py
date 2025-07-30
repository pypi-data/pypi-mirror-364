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

from loguru import logger




from .types.team import TeamPayload, TeamGames as TeamGamesPayload
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .state import ConnectionState
    from .role import Role


__all__ = ['Team']

class TeamGames:

    __slots__ = (
        'id',
        'platforms',
        'region'
    )

    def __init__(self, data: TeamGamesPayload) -> None:
        self.id: str = data['id']
        self.platforms: List[str] = data['platforms']
        self.region: str = data['region']

class Team:

    __slots__ = (
        '_state',
        'id',
        'name',
        '_profile_picture',
        'banner',
        'description',
        '_is_verified',
        '_is_safe_for_teen',
        '_is_suspended',
        '_created_by',
        '_default_channel_id',
        'games',
        '_is_discoverable',
        '_is_tournament',
        '_discoverable_invite',
        '_created_at',
        '_member_count'
    )

    def __init__(self,*, state: ConnectionState, data: TeamPayload) -> None:
        self._state = state
        self._update(data)

    def _update(self, data: TeamPayload):
        self.id: str = data['id']
        self.name: str = data['name']
        self._profile_picture: Optional[str] = data.get('profilePicture')
        self.banner: Optional[str] = data.get('banner')
        self.description: Optional[str] = data.get('description')

        self._is_verified: bool = data['isVerified']
        self._is_safe_for_teen: bool = data.get('isSafeForTeen', False)
        self._is_suspended: bool = data['isSuspended']
        self._created_by: str = data['createdBy']
        self._default_channel_id: str = data.get('defaultChannelId')
        self.games: List[TeamGames] = [TeamGames(g) for g in data.get('games')]
        self._is_discoverable: bool = data.get('idDiscoverable', False)
        self._is_tournament: bool = data.get('isTournament', False)
        self._discoverable_invite: Optional[str] = data.get('discoverableInvite')
        self._created_at: str = data['createdAt']
        self._member_count: int = data['memberCount']

    #Team

    async def edit(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        banner: Optional[str] = None,
        profilePicture: Optional[str] = None
    ):
        if len(name) > 12:
            raise ValueError("\'name\' must be smaller or equel then 12 characters")

        if len(description) > 1000:
            raise ValueError("\'description\' must be smaller or equel then 1000 characters")

        payload = {
            k:v
            for k,v in locals().items()
            if v is not None
        }

        try:
            await self._state.http.update_team(self.id, payload=payload)
        except Exception as e:
            logger.error(f"Exception error: {e}")


    def info(self) -> str:
        return (
            f"""
            Team:
                ID: {self.id}
                Name: {self.name}
                ProfilePicture: {self.profile_picture[:10] + '...' if self.profile_picture else 'N/A'}
                Banner: {self.banner[:10] + '...' if self.banner else 'N/A'}
                Description: {self.description[:25] + '...' if self.description else 'N/A'}
                IsVerified: {self.is_verified}
                IsSafeForTeen: {self._is_safe_for_teen}
                IsSuspended: {self.is_suspended}
                CreatedBy: {self._created_by}
                CreatedAt: {self._created_at}
                DefaultChannel: {self._default_channel_id if self._default_channel_id else 'N/A'}
                Games: {[t.id for t in self.games]}
                IsDiscoverable: {self._is_discoverable}
                IsTournament: {self._is_tournament}
                DiscoverableInvite: {self._discoverable_invite}
            """
        )

    #Member

    def fetch_members(self):
        return self._state.cache.get_members(teamId=self.id)

    def get_members_count(self):
        return len(self._state.cache.get_members(teamId=self.id))

    def get_member(self, userId: str):
        return self._state.cache.get_member(teamId=self.id, userId=userId)




    async def ban(self, userId: str, reason: str):
        return await self._state.http.ban(teamId=self.id, userId=userId, reason=reason)

    async def unban(self, userId: str):
        return await self._state.http.unban(teamId=self.id, userId=userId)

    async def get_banned_users(self, teamId: str, limit: int = 10):
        return await self._state.http.get_banned_users(teamId=teamId, limit=limit)


    async def kick(self, userId: str):
        return await self._state.http.kick_member(teamId=self.id, userId=userId)


    #Role

    async def add_role(self, role: Role):
        return await self._state.http.create_role(teamId=self.id, payload=role.to_dict())

    async def remove_role(self, roleId: str):
        return await self._state.http.delete_role(teamId=self.id, roleId=roleId)

    async def list_roles(self):
        return await self._state.http.get_roles(teamId=self.id)

    async def assigne_role(self, userId: str, roleId: str):
        return await self._state.http.add_role_to_member(teamId=self.id, userId=userId, roleId=roleId)

    async def unassigne_role(self, userId: str, roleId: str):
        return await self._state.http.remove_role_from_member(teamId=self.id, userId=userId, roleId=roleId)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            f"<Team id={self.id} name={self.name} description={self.description}"
            f" isVerified={self.is_verified} isDiscoverable={self.is_discoverable}>"
        )
