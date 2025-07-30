




from typing import Dict, Optional, TypedDict


class Role(TypedDict):
    id: str
    teamId: str
    name: str
    iconUrl: Optional[str]
    color: str
    color2: Optional[str]
    permissions: int
    priority: int
    createdAt: str
    updatedAt: Optional[str]
    isDisplayedSeparately: bool
    isSelfAssignable: bool
    iconEmojiId: Optional[str]
    mentionable: bool
    botScope: Optional[Dict[str,str]]
