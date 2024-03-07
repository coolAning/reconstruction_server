from functools import wraps

from flask import jsonify, render_template
from app.utils.response import ResMsg
from flask_mail import Message
from threading import Thread
from flask import current_app
from flask_mail import Mail  # Import the mail object from Flask-Mail


def route(bp, *args, **kwargs):
    """
    路由设置,统一返回格式
    :param bp: 蓝图
    :param args:
    :param kwargs:
    :return:
    """
    kwargs.setdefault('strict_slashes', False)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            rv = f(*args, **kwargs)
            # 响应函数返回整数和浮点型
            if isinstance(rv, (int, float)):
                res = ResMsg()
                res.update(data=rv)
                return jsonify(res.data)
            # 响应函数返回元组
            elif isinstance(rv, tuple):
                # 判断是否为多个参数
                if len(rv) >= 3:
                    return jsonify(rv[0]), rv[1], rv[2]
                else:
                    return jsonify(rv[0]), rv[1]
            # 响应函数返回字典
            elif isinstance(rv, dict):
                return jsonify(rv)
            # 响应函数返回字节
            elif isinstance(rv, bytes):
                rv = rv.decode('utf-8')
                return jsonify(rv)
            else:
                return rv
                # return jsonify(rv)

        return wrapper

    return decorator


def view_route(f):
    """
    路由设置,统一返回格式
    :param f:
    :return:
    """

    def decorator(*args, **kwargs):
        rv = f(*args, **kwargs)
        if isinstance(rv, (int, float)):
            res = ResMsg()
            res.update(data=rv)
            return jsonify(res.data)
        elif isinstance(rv, tuple):
            if len(rv) >= 3:
                return jsonify(rv[0]), rv[1], rv[2]
            else:
                return jsonify(rv[0]), rv[1]
        elif isinstance(rv, dict):
            return jsonify(rv)
        elif isinstance(rv, bytes):
            rv = rv.decode('utf-8')
            return jsonify(rv)
        else:
            return jsonify(rv)

    return decorator


def send_msg(to, title, captcha, **kwargs):
    app = current_app._get_current_object()  # 获取当前Flask应用对象
    msg = Message(title, sender='三维重建<neu_aning@163.com>', recipients=to)
    msg.body = '你的验证码是: {}'.format(captcha)
    thr = Thread(target=send_sync_msg, args=[app, msg])
    thr.start()
    return thr


def send_sync_msg(app, msg):
    with app.app_context():
        mail = Mail(app)
        mail.send(msg)

