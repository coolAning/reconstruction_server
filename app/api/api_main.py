import os
import subprocess
from werkzeug.datastructures import FileStorage
import logging
import requests
from flask import Blueprint,Response

from flask import request
from app.celery import process_file
from app.utils.response import ResMsg
from app.utils.util import route
from app.utils.code import ResponseCode



bp = Blueprint("main", __name__, url_prefix='/main')

logger = logging.getLogger(__name__)

@route(bp, '/test', methods=["POST"])
def upload():
    res = ResMsg()
    process_file.delay('1_cup')
    res.update(code=ResponseCode.Success)
    return res.data