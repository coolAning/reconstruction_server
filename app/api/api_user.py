import logging

from flask import Blueprint

from app.models.model import User
from app.utils.core import db
from flask import request
from app.utils.response import ResMsg
from app.utils.util import route
from app.utils.code import ResponseCode

bp = Blueprint("user", __name__, url_prefix='/user')

logger = logging.getLogger(__name__)

@route(bp, '/login', methods=["POST"])
def login():
    res = ResMsg()
    res.update(code=ResponseCode.AccountOrPassWordErr)
    user = db.session.query(User).filter(User.account == request.json.get("account")).first()
    if user:
        if user.password == request.json.get("password"):
            res.update(code=ResponseCode.Success)
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
    