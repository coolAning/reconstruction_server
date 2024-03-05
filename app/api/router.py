from app.api.api_user import bp as user
from app.api.api_main import bp as main
router = [
    user,  # 用户接口
    main,  # 主要功能接口
]
