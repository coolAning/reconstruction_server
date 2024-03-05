from datetime import datetime

from sqlalchemy import Integer
from app.utils.core import db


class User(db.Model):
    """
    用户表
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    account = db.Column(db.String(20), nullable=True)  # 用户账号
    password = db.Column(db.String(20), nullable=True)  # 用户密码
    
class test(db.Model):
    """
    test
    """
    __tablename__ = 'test'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    test = db.Column(db.String(20), nullable=True)  # test
