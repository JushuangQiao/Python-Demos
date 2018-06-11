# -*- coding: utf-8 -*-
import json
import uuid

import requests
from redis import StrictRedis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from tornado.web import RequestHandler

# mysql 相关设置
engine = create_engine('mysql://root:@localhost/wechat')
conn = engine.connect()

Base = declarative_base()
Base.metadata.reflect(engine)
tables = Base.metadata.tables

user_redis = StrictRedis.from_url('redis//localhost:6379')


class LoginHandler(RequestHandler):

    def post(self):
        req_data = json.loads(self.request.body)

        js_code = req_data.get('js_code')

        # 这里是换取用户的信息
        user_info = get_user_info(js_code=js_code)

        openid = user_info['openid']
        session_key = user_info['session_key']
        user_uuid = str(uuid.uuid4())  # 暴露给小程序端的用户标示

        # 用来维护用户的登录态
        User.save_user_session(
            user_uuid=user_uuid,
            openid=openid,
            session_key=session_key
        )
        # 微信小程序不能设置cookie，把用户信息存在了 headers 中
        self.set_header('Authorization', user_uuid)

        # 存储用户信息
        User.save_user_info(open_id=openid)

        self.set_status(204)


def get_user_info(js_code):

    req_params = {
        "appid": 'app_id',  # 小程序的 ID
        "secret": 'secret',  # 小程序的 secret
        "js_code": js_code,
        "grant_type": 'authorization_code'
    }
    req_result = requests.get('https://api.weixin.qq.com/sns/jscode2session',
                              params=req_params, timeout=3, verify=False)
    return req_result.json()


class User(object):

    REDIS_EXPIRES = 7 * 24 * 60 * 60
    table = tables['user']

    @classmethod
    def save_user_session(cls, user_uuid, openid, session_key):
        user_session_value = {
            'openid': openid,
            'session_key': session_key
        }
        user_session_key = 'US:' + user_uuid
        with user_redis.pipeline(transaction=False) as pipe:
            pipe.hmset(user_session_key, user_session_value)
            pipe.expire(user_session_key, cls.REDIS_EXPIRES)
            pipe.execute()

    @classmethod
    def save_user_info(cls, open_id):
        # 存储用户
        sql = cls.table.insert().values(open_id=open_id)
        conn.execute(sql)
