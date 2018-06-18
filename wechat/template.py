# -*- coding: utf-8 -*-
import json

import requests
from redis import StrictRedis
from tornado.web import RequestHandler


redis = StrictRedis.from_url('redis//localhost:6379')


def get_access_token():
    payload = {
        'grant_type': 'client_credential',
        'appid': 'appid',
        'secret': 'secret'
    }

    req = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=payload, timeout=3, verify=False)
    access_token = req.json().get('access_token')
    redis.set('ACCESS_TOKEN', access_token)


class FormHandler(RequestHandler):

    def post(self):
        req_data = self.request.body
        req_data = json.loads(req_data)
        form_id = req_data.get('form_id')
        template_push(form_id)  # 使用消息进行模板推送


def template_push(form_id):
    data = {
        "touser": 'openid',
        "template_id": 'template_id',
        "page": 'pages/index/index',
        "form_id": form_id,
        "data": {
            'keyword1': {
                'value': 'value1'
            }
        },
        "emphasis_keyword": ''
    }
    access_token = redis.get('ACCESS_TOKEN')
    push_url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={}'.format(access_token)
    requests.post(push_url, json=data, timeout=3, verify=False)
