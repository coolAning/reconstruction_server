from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from app.utils.core import db


class User(db.Model):
    """
    用户表
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    account = db.Column(db.String(20), nullable=False)  # 用户账号
    password = db.Column(db.String(20), nullable=False)  # 用户密码
    
class Captcha(db.Model):
    """
    邮箱验证码表
    """
    __tablename__ = 'captcha'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    account = db.Column(db.String(20), ForeignKey('user.account'), nullable=False)  # 用户账号
    code = db.Column(db.String(20), nullable=False)  # 验证码
    time = db.Column(db.DateTime, default=datetime.now)  # 发送时间
class Video(db.Model):
    """
    视频文件表
    """
    __tablename__ = 'video'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)  # 用户id
    name = db.Column(db.String(20), nullable=False)  # 文件名 
    train_steps = db.Column(db.Integer, default=1000)  # 训练步数
    aabb = db.Column(db.Integer, default=32)  # aabb缩放参数
    status = db.Column(db.Integer, default=0)  # 文件状态 0:未处理 1:colmap处理完成  2:nerf处理完成
    task_id = db.Column(db.String(20), nullable=True)  # 任务id