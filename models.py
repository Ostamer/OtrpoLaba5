from pydantic import BaseModel
from typing import List, Optional

# Модель для узла пользователя
class UserModel(BaseModel):
    id: int
    name: Optional[str] = ""
    screen_name: Optional[str] = None
    sex: Optional[int] = None
    home_town: Optional[str] = None

# Модель для узла группы
class GroupModel(BaseModel):
    id: int
    name: Optional[str] = ""
    screen_name: Optional[str] = None
    subscribers_count: Optional[int] = 0

# Модель для ответа по узлу и его связям
class NodeRelationships(BaseModel):
    node: UserModel
    follows: List[UserModel] = []
    subscribes: List[GroupModel] = []
