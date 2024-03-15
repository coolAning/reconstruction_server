from celery import Celery
from flask import Flask, current_app, jsonify
from celery.result import AsyncResult

import logging

from flask import Blueprint

from app.models.model import Captcha, User
from app.utils.core import db
from flask import request
from app.utils.response import ResMsg
from app.utils.util import route
from app.utils.code import ResponseCode



bp = Blueprint("celery", __name__, url_prefix='/celery')

logger = logging.getLogger(__name__)

@route(bp, '/check', methods=["POST"])
def login():
    celery_app = current_app.celery_app
    res = ResMsg()
    res.update(code=ResponseCode.AccountOrPassWordErr)
    task_id = request.json.get("task_id")
    # 使用任务 ID 创建一个 AsyncResult 对象
    task = AsyncResult(task_id, app=celery_app)
    # 获取任务的状态和结果
    status = task.status
    result = task.result
    res.update(code=ResponseCode.Success, data={"status": status, "result": result})
    return res.data