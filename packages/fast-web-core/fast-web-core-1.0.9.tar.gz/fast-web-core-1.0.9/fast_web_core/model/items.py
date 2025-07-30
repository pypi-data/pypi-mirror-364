from typing import Optional

from pydantic import BaseModel, Field

from ..lib import time as time_lib


class BaseData(BaseModel):
    """
    通用基础数据模型
    """
    # mongodb主键
    _id: str = None
    # 插入时间
    genTime: int = Field(
        default_factory=time_lib.current_timestamp10
    )


class AuthUser(BaseData):
    """
    用户鉴权模型
    """
    # 用户id
    id: Optional[int] = None
    # 是否超级管理员,[1=是,0=否]
    is_super_admin: Optional[int] = 0
    # 用户编号
    user_id: Optional[str] = None
    # 用户账号
    account: Optional[str] = None
    # 用户昵称
    nickname: Optional[str] = None
    # 团队主键,团队编号
    team_id: Optional[str] = None
    # 是否团队管理员,[1=是,0=否]
    is_team_admin: Optional[int] = 0
    # 最后一次登录token
    token: Optional[str] = None
    # 团队名称
    team_name: Optional[str] = None
    # 团队简称
    team_nick_name: Optional[str] = None
    # 团队状态:[1=正常,0=禁用]
    team_status: Optional[int] = 1

    def to_log(self):
        return f'{self.nickname}({self.account})'


class AuthApp(BaseData):
    # 应用id
    app_id: Optional[str] = None
    # 应用名称
    app_name: Optional[str] = None
    # 团队主键,团队编号
    team_id: Optional[str] = None
    # 团队名称
    team_name: Optional[str] = None
