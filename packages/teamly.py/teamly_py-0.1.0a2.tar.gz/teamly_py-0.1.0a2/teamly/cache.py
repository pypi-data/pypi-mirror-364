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

import asyncio
from collections import OrderedDict
import json
from typing import Dict, Optional, Union, Any, TYPE_CHECKING

from loguru import logger

from .channel import TextChannel, VoiceChannel, _channel_factory
from .http import HTTPClient
from .message import Message
from .team import Team
from .member import Member
from .user import ClientUser

if TYPE_CHECKING:
    from .state import ConnectionState
    from .channel import (
        TextChannel,
        VoiceChannel
    )
    from .message import Message
    MessageAbleChannel = Union[TextChannel]
    Channel = Union[TextChannel, VoiceChannel]

__all__ = [
    "Cache"
]

class Cache:

    def __init__(self, state: ConnectionState) -> None:
        self._state: ConnectionState = state
        self._http: HTTPClient = self._state.http
        self.maxLength: int = 100
        self.clear()

    def clear(self):
        self.__user: Optional[ClientUser] = None
        self.__teams: Dict[str, Team] = {}
        self.__channels: Dict[str, Dict[str, Channel]] = {}
        self.__messages: Dict[str, Dict[str, OrderedDict[str, Message]]] = {}
        self.__members: Dict[str, Dict[str, Member]] = {}

    async def setup_cache(self, data: Any):
        #get ClietnUser Payload
        self.__user = ClientUser(state=self._state, data=data['user'])
        logger.info(f"Bot connected as {self.__user.username!r}")
        await self.__fetch_teams(data['teams'])
        tasks = []
        for team in self.__teams:
            tasks.append(self.__fetch_channels(team))
            tasks.append(self.__fetch_team_members(team))

        await asyncio.gather(*tasks)

    async def __fetch_teams(self, teams: Dict[str, Any]):
        for team in teams:
            self.__teams[team['id']] = Team(state=self._state, data=team)

    async def __fetch_channels(self, teamId: str):
        channels = await self._http.get_channels(teamId)
        channels = json.loads(channels)

        for data in channels['channels']:
            factory = _channel_factory(data['type'])
            channel: Channel = None
            team: Team = None

            if teamId not in self.__channels:
                self.__channels[teamId] = {}

            if factory:
                team = self.__teams[teamId]
                self.__channels[teamId][data['id']] = channel = factory(state=self._state,team=team, data=data)

            if teamId not in self.__messages:
                self.__messages[teamId] = OrderedDict()

            if data['type'] == 'text':
                self.__messages[teamId][channel.id] = await self.__fetch_channel_messages(channel=channel)

    async def __fetch_channel_messages(self, channel: MessageAbleChannel):
        try:
            messages = await self._http.get_channel_messages(channelId=channel.id, limit=50)
            messages = json.loads(messages)

            message_dict = {}

            if messages['messages']:
                for message in messages['messages']:
                    message_dict[message['id']] = Message(state=self._state, channel=channel, data=message)

            if messages['replyMessages']:
                for message in messages['replyMessages']:
                    message_dict[message['id']] = Message(state=self._state, channel=channel, data=message)

            return message_dict
        except Exception as e:
            logger.error(f"Exception error: {e}")
            return {}

    async def __fetch_team_members(self, teamId: str):
        members = await self._http.get_member(teamId, "")
        members = json.loads(members)

        if teamId not in self.__members:
            self.__members[teamId] = {}

        for member in members['members']:
            if member['id'] not in self.__members:
                self.__members[member['id']] = Member(state=self._state, data=member)


    #Team Cache
    def get_team(self, teamId):
        if teamId in self.__teams:
            return self.__teams[teamId]


    #Channel Cache
    def add_channel(self, teamId: str, channelId: str, channel: MessageAbleChannel):
        if teamId not in self.__channels:
            self.__channels[teamId] = {}

        if channelId not in self.__channels[teamId]:
            self.__channels[teamId][channelId] = channel
            logger.opt(colors=True).debug(f"<cyan>Added channel {channelId!r} to cache successfuly</cyan>")

    def delete_channel(self, teamId: str, channelId: str):
        if channelId in self.__channels[teamId]:
            self.__channels[teamId].pop(channelId)
            logger.opt(colors=True).debug(f"<cyan>Deleted channel {channelId!r} from cache successfuly</cyan>")

    def update_channel(self, teamId: str, channelId: str, channel: MessageAbleChannel):
        if channelId in self.__channels[teamId]:
            self.__channels[teamId][channelId] = channel
            logger.opt(colors=True).debug(f"<cyan>Updated channel {channelId!r} from cache successfuly</cyan>")

    def get_channel(self, teamId: str, channelId: str) -> Channel | None:
        try:
            if channelId in self.__channels[teamId]:
                return self.__channels[teamId][channelId]
        except Exception as e:
            logger.error(f"Exception error: {e}")

    #Voice Channel
    def voice_participants_joined(self,teamId: str, channelId: str, participantId: str):
        if self.__channels[teamId][channelId]:
            voice = self.__channels[teamId][channelId]
            if not any(p.get('id') == participantId for p in voice._participants):
                voice._participants.append({"id": participantId})

    def voice_participants_leaved(self, teamId:str, channelId: str, participantId: str):
        if self.__channels[teamId][channelId]:
            voice = self.__channels[teamId][channelId]
            for par in voice._participants:
                if par.get('id') == participantId:
                    voice._participants.remove({"id": participantId})


    #Message Cache

    def add_message(self, teamId: str, channelId: str, message: Message):
        if channelId in self.__messages[teamId]:
            self.__messages[teamId][channelId][message.id] = message

        if len(self.__messages[teamId][channelId]) > self.maxLength:
            self.__messages[teamId][channelId].popitem(last=False)

    def update_message(self, teamId: str, channelId: str, message: Message):
        if channelId in self.__messages[teamId]:
            if message.id in self.__messages[teamId][channelId]:
                upt_message = self.__messages[teamId][channelId][message.id]
                self.__messages[teamId][channelId][message.id] = message
                logger.opt(colors=True).debug(f"<cyan>updated channel message {message.id!r} from cache successfuly</cyan>")
                return upt_message


    def delete_message(self, teamId: str, channelId: str, messageId: str):
        if channelId in self.__messages[teamId]:
            if messageId in self.__messages[channelId][messageId]:
                message = self.__messages[teamId][channelId].pop(messageId)
                logger.opt(colors=True).debug(f"<cyan>deleted channel message {messageId!r} from cache successfuly</cyan>")
                return message



    #Member

    def get_members(self, teamId: str):
        return self.__members[teamId].values

    def get_member(self, teamId: str, userId: str):
        return self.__members[teamId][userId] if userId in self.__members[teamId] else None

    def add_member(self, teamId: str, member: Member):
        if member.id not in self.__members[teamId]:
            self.__members[teamId][member.id] = member

    def delete_member(self, teamId: str, memberId: str):
        if memberId in self.__members[teamId]:
            self.__members[teamId].pop(memberId)
