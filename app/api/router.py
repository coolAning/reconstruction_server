from app.api.api_user import bp as user
from app.api.api_main import bp as main
from app.api.api_camera import bp as camera
from app.api.api_celery import bp as celery
from app.api.api_render import bp as render
router = [
    user,  # 用户接口
    main,  # 主要功能接口
    camera, # 相机接口
    celery, # celery接口
    render, # 渲染接口
]
