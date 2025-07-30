

from .types.role import Role as RolePayload
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from .state import ConnectionState
    from .team import Team

__all__ = ['Role']

class Role:

    __slots__ = (
        '_state',
        'team',
        'id',
        'name',
        '_icon_url',
        '_color',
        '_color2',
        'permissions',
        'priority',
        '_created_at',
        '_updated_at',
        '_is_displayed_separately',
        '_is_self_assignable',
        '_icon_emoji_id',
        'mentionable',
        '_bot_scope'
    )

    def __init__(
        self,
        state: ConnectionState,
        *,
        team: Team,
        data: RolePayload
    ) -> None:
        self._state: ConnectionState = state
        self.team: Team = team
        self._update(data)

    def _update(self, data: RolePayload):
        self.id: str = data['id']
        #self.team
        self.name: str = data['name']

        self._icon_url: Optional[str] = data.get('iconUrl')
        self._color: str = data['color']
        self._color2: Optional[str] = data.get('color2')
        self.permissions: int = data.get('permissions', 0)
        self.priority: int = data.get('priority', 0)
        self._created_at: str = data['createdAt']
        self._updated_at: Optional[str] = data.get('updatedAt')
        self._is_displayed_separately: bool = data.get('isDisplayedSeparately', True)
        self._is_self_assignable: bool = data.get('isSelfAssignable', False)
        self._icon_emoji_id: Optional[str] = data.get('iconEmojiId')
        self.mentionable: bool = data.get('mentionable', True)
        self._bot_scope: Dict[str,str] = data.get('botScope',{})

    def to_dict(self):
        return {
            "id": self.id,
            "teamId": self.team.id,
            "name": self.name,
            "iconUrl": self._icon_url,
            "color": self._color,
            "color2": self._color2,
            "permissions": self.permissions,
            "priority": self.priority,
            "createdAt": self._created_at,
            "updatedAt": self._updated_at,
            "isDisplayedSeparately": self._is_displayed_separately,
            "isSelfAssignable": self._is_self_assignable,
            "iconEmojiId": self._icon_emoji_id,
            "mentionable": self.mentionable,
            "botScope": self._bot_scope
        }

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name} permissions={self.permissions} teamId={self.team.id}>"
