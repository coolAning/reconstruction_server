import logging
import logging.config
import yaml
import os
from flask import Flask, Blueprint
from app.models.model import User
from app.utils.core import JSONEncoder, db
from app.api.router import router
from flask_cors import *
from app.celery import celery_app
def create_app(config_name, config_path=None):
    app = Flask(__name__)
    
    # 读取配置文件
    if not config_path:
        pwd = os.getcwd()
        config_path = os.path.join(pwd, 'config/config.yaml')
    if not config_name:
        config_name = 'PRODUCTION'

    # 读取配置文件
    conf = read_yaml(config_name, config_path)
    app.config.update(conf)
    
    # 更新Celery配置信息
    celery_conf = "redis://{}:{}/{}".format(app.config['REDIS_HOST'], app.config['REDIS_PORT'], app.config['REDIS_DB'])
    celery_app.conf.update({"broker_url": celery_conf, "result_backend": celery_conf})
    # 保存 Celery 实例的引用
    app.celery_app = celery_app
    

    # 注册接口
    register_api(app=app, routers=router)

    # 返回json格式转换
    app.json_encoder = JSONEncoder

    # 注册数据库连接
    db.app = app
    db.init_app(app)
     # 创建数据库表格
    with app.app_context():
        db.create_all()
            # 检查是否存在用户
        if not User.query.first():
            # 添加默认用户记录
            default_user = User(account='admin', password='C4CA4238A0B923820DCC509A6F75849B')
            db.session.add(default_user)
            db.session.commit()
        
    # 日志文件目录
    if not os.path.exists(app.config['LOGGING_PATH']):
        os.mkdir(app.config['LOGGING_PATH'])

    # 日志设置
    with open(app.config['LOGGING_CONFIG_PATH'], 'r', encoding='utf-8') as f:
        dict_conf = yaml.safe_load(f.read())
    logging.config.dictConfig(dict_conf)

    # 读取msg配置
    with open(app.config['RESPONSE_MESSAGE'], 'r', encoding='utf-8') as f:
        msg = yaml.safe_load(f.read())
        app.config.update(msg)
    #允许跨域
    CORS(app, supports_credentials=True)
    return app


def read_yaml(config_name, config_path):
    """
    config_name:需要读取的配置内容
    config_path:配置文件路径
    """
    if config_name and config_path:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f.read())
        if config_name in conf.keys():
            return conf[config_name.upper()]
        else:
            raise KeyError('未找到对应的配置信息')
    else:
        raise ValueError('请输入正确的配置名称或配置文件路径')


def register_api(app, routers):
    for router_api in routers:
        if isinstance(router_api, Blueprint):
            app.register_blueprint(router_api)
        else:
            try:
                endpoint = router_api.__name__
                view_func = router_api.as_view(endpoint)
                # 如果没有服务名,默认 类名小写
                if hasattr(router_api, "service_name"):
                    url = '/{}/'.format(router_api.service_name.lower())
                else:
                    url = '/{}/'.format(router_api.__name__.lower())
                if 'GET' in router_api.__methods__:
                    app.add_url_rule(url, defaults={'key': None}, view_func=view_func, methods=['GET', ])
                    app.add_url_rule('{}<string:key>'.format(url), view_func=view_func, methods=['GET', ])
                if 'POST' in router_api.__methods__:
                    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
                if 'PUT' in router_api.__methods__:
                    app.add_url_rule('{}<string:key>'.format(url), view_func=view_func, methods=['PUT', ])
                if 'DELETE' in router_api.__methods__:
                    app.add_url_rule('{}<string:key>'.format(url), view_func=view_func, methods=['DELETE', ])
            except Exception as e:
                raise ValueError(e)
