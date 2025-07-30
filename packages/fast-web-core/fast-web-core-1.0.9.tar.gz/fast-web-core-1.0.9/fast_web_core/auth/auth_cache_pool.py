# -*- coding: utf-8 -*-
import json
import logging
from typing import List, Set, Optional, Dict
from ..lib import cfg
from ..client.redis_client import Redis
from ..model.items import AuthUser, AuthApp

logger = logging.getLogger(__name__)
rds = Redis(redis_uri=cfg.get('AUTH_REDIS_URL', None), redis_db=cfg.get('AUTH_REDIS_DB', None)).client
default_expire = 43200


def get_cached_app(access_token: str) -> Optional[AuthApp]:
    rs = rds.get(f'fast:access:share:token_{access_token}')
    if rs:
        js_user = json.loads(rs)
        # 容错
        if isinstance(js_user, str):
            js_user = json.loads(js_user)
        # 特征验证（user对象需要有id字段）
        if js_user and js_user.get('team_id', None):
            auth_app = AuthApp(**js_user)
            return auth_app

    return None


def get_cached_user(access_token: str) -> Optional[AuthUser]:
    rs = rds.get(f'fast:access:share:user_{access_token}')
    if rs:
        js_user = json.loads(rs)
        # 容错
        if isinstance(js_user, str):
            js_user = json.loads(js_user)
        # 特征验证（user对象需要有id字段）
        if js_user and js_user.get('id', None) is not None:
            user = AuthUser(**js_user)
            return user

    return None


def get_cached_access_dict(access_token: str) -> Optional[Dict]:
    rs = rds.get(f'fast:access:share:user_{access_token}')
    if rs:
        item = json.loads(rs)
        # 容错
        if isinstance(item, str):
            item = json.loads(item)
        return item

    return None


def has_access(access_token: str) -> bool:
    return rds.exists(f'fast:access:share:token_{access_token}') or rds.exists(f'fast:access:share:user_{access_token}')


def has_app_access(access_token: str) -> bool:
    return rds.exists(f"fast:access:share:token_{access_token}")


def save_cached_permission(access_token: str, permissions: Set[str], expire: int = None):
    if permissions:
        key = f'fast:share:permissions:{access_token}'
        for per in permissions:
            rds.sadd(key, per)
        _expire = expire or default_expire
        rds.expire(key, _expire)


def has_permission(access_token: str, permission: str) -> bool:
    # 后者兼容Java版本异常
    _key = f'fast:access:permission:token_{access_token}'
    is_member = rds.sismember(_key, permission)
    if not is_member:
        _permission = f'"{permission}"'
        is_member = rds.sismember(_key, _permission)

    if not is_member:
        return False
    # 如果有这个接口权限，校验权限状态是否是1
    key_pattern = f"fast:access:*{permission}:{access_token}"
    keys = rds.keys(key_pattern)
    permission_is_open = False
    for key in keys:
        permission_status = rds.get(key)
        if permission_status == "1":
            permission_is_open = True
    return permission_is_open
    # return rds.sismember(_key, f'{permission}') or rds.sismember(_key, f'"{permission}"')


def get_cached_permission(access_token: str) -> List[str]:
    return rds.smembers(f'fast:share:permissions:{access_token}')


def clean_cache(access_token: str):
    rds.delete(f'fast:access:share:user_{access_token}')
    rds.delete(f'fast:share:permissions:{access_token}')
