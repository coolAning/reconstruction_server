import os
import subprocess
from werkzeug.datastructures import FileStorage
import logging
import requests
from flask import Blueprint,Response, current_app
from app.utils.core import db
from flask import request
from app.models.model import Video
from app.utils.response import ResMsg
from app.utils.util import route
from app.utils.code import ResponseCode



bp = Blueprint("render", __name__, url_prefix='/render')

logger = logging.getLogger(__name__)

import requests

@route(bp, '/photo', methods=['POST'])
def complete():
    res = ResMsg()
    res.update(code=ResponseCode.SystemError)
    # 获取 POST 请求的 JSON 数据
    data = request.get_json()
    url = current_app.config['ALGORITHM_URL']
    response = requests.post(f'{url}/render', json=data)
    # 检查请求是否成功
    if response.status_code == 200:
        # 如果成功，将返回的 JSON 数据更新到响应中
        res.update(code=ResponseCode.Success, data=response.json())
    else:
        # 如果失败，将错误信息更新到响应中
        res.update(code=ResponseCode.Fail)
    
    return res.data

