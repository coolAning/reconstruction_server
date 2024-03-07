from datetime import datetime

from sqlalchemy import Integer
from app.utils.core import db


class User(db.Model):
    """
    用户表
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    account = db.Column(db.String(20), nullable=False)  # 用户账号
    password = db.Column(db.String(20), nullable=False)  # 用户密码
    
class Captcha(db.Model):
    """
    邮箱验证码表
    """
    __tablename__ = 'captcha'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    account = db.Column(db.String(20), nullable=False)  # 用户账号
    code = db.Column(db.String(20), nullable=False)  # 验证码
    time = db.Column(db.DateTime, default=datetime.now)  # 发送时间
    
class test(db.Model):
    """
    test
    """
    __tablename__ = 'test'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    test = db.Column(db.String(20), nullable=True)  # test
