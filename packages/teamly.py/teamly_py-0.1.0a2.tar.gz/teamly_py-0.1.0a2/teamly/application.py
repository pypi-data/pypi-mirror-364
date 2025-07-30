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

from typing import TYPE_CHECKING, List, Literal, Optional, Union

if TYPE_CHECKING:
    from .state import ConnectionState
    from .user import User
    from .team import Team
    from .enums import AppStatus
    from types.application import Application as ApplicationPayload, Answers as AnswersPayload


class Answers:

    def __init__(self, data: AnswersPayload) -> None:
        self.question_id: str = data['questionId']
        self.answer: Optional[Union[str, List[str]]] = data.get('answer')
        self.question: str = data['question']
        self.optional: bool = data['optional']
        self.options: List[str] = data['options']

class Application:

    def __init__(
        self,
        state: ConnectionState,
        *,
        team: Team,
        data: ApplicationPayload
    ) -> None:
        self._state: ConnectionState = state
        self.team: Team = team
        self._update(data)

    def _update(self, data: ApplicationPayload):
        self.id: str = data['id']
        self.type: str = data['type']
        self._submitted_by: User = data['submittedBy']
        self.answers: Answers = data['answers']
        self.status: AppStatus = data['status']
        self._created_at: str = data['createdAt']

    async def update_status(self, status = Literal['accepted','rejected']):
        await self._state.http.update_application_status(teamId=self.team.id, applicationId=self.id, status=status)
