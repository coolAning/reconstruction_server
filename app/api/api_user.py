from datetime import datetime
import logging

from flask import Blueprint

from app.models.model import Captcha, User
from app.utils.core import db
from flask import request
from app.utils.response import ResMsg
from app.utils.util import route, send_msg
from app.utils.code import ResponseCode
import random

bp = Blueprint("user", __name__, url_prefix='/user')

logger = logging.getLogger(__name__)

@route(bp, '/login', methods=["POST"])
def login():
    res = ResMsg()
    res.update(code=ResponseCode.AccountOrPassWordErr)
    user = db.session.query(User).filter(User.account == request.json.get("account")).first()
    if user:
        if user.password == request.json.get("password"):
            res.update(code=ResponseCode.Success,data={"userId":user.id})
    return res.data

@route(bp, '/changePassword', methods=["POST"])
def changePassword():
    res = ResMsg()
    res.update(code=ResponseCode.Fail)
    account = request.json.get("account")
    new_password = request.json.get("new_password")
    old_password = request.json.get("old_password")
    user = db.session.query(User).filter(User.account == account).first()
    if user:
        if user.password == old_password:
            user.password = new_password
            db.session.commit()
            res.update(code=ResponseCode.Success)
        else:
            res.update(code=ResponseCode.PasswordError)
    return res.data

@route(bp, '/register', methods=["POST"])
def register():
    res = ResMsg()
    res.update(code=ResponseCode.Fail)
    account = request.json.get("account")
    password = request.json.get("password")
    user_check = db.session.query(User).filter(User.account == account).first()
    if user_check:
        res.update(code=ResponseCode.AccountDuplicate)
    else:
        user=User(account=account,password=password)
        db.session.add(user)
        db.session.commit()
        res.update(code=ResponseCode.Success)
    return res.data

@route(bp, '/captcha', methods=["POST"])
def captcha():
    res = ResMsg()
    res.update(code=ResponseCode.Fail)
    account = request.json.get("account")
    user = db.session.query(User).filter(User.account == account).first()
    if user:
        captcha_code = random.randint(100000, 999999)
        captcha_check = db.session.query(Captcha).filter(Captcha.account == account).first()
        if captcha_check:
            time= captcha_check.time
            if (datetime.now() - time).seconds < 60:
                res.update(code=ResponseCode.CaptchaSendTooFrequent)
                return res.data
            elif (datetime.now() - time).seconds > 60:
                captcha_check.code = captcha_code
                captcha_check.time = datetime.now()
                db.session.commit()
        else:
            captcha = Captcha(account=account,code=captcha_code)
            db.session.add(captcha)
            db.session.commit()
        # 发送验证码
        to = [account]
        title = '【三维重建】忘记密码'
        send_msg(to=to, title=title ,captcha=captcha_code)
        
        res.update(code=ResponseCode.Success)
    else:
        res.update(code=ResponseCode.AccountNotFound)
    
    return res.data

@route(bp, '/forgetPassword', methods=["POST"])
def forgetPassword():
    res = ResMsg()
    res.update(code=ResponseCode.Fail)
    account = request.json.get("account")
    new_password = request.json.get("new_password")
    captcha = request.json.get("captcha")
    user = db.session.query(User).filter(User.account == account).first()
    captcha_check = db.session.query(Captcha).filter(Captcha.account == account).first()
    if captcha_check:
        if (datetime.now() - captcha_check.time).seconds > 300:
            res.update(code=ResponseCode.InvalidOrExpired)
        else:
            if captcha_check.code == captcha:
                user.password = new_password
                db.session.delete(captcha_check)
                db.session.commit()
                res.update(code=ResponseCode.Success)
            else:
                res.update(code=ResponseCode.CaptchaError)
    else:
        res.update(code=ResponseCode.CaptchaError)
    return res.data
    