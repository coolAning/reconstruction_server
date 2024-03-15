# 数据库创建
from app.factory import create_app
from app.utils.core import db
app = create_app(config_name="DEVELOPMENT")
app.app_context().push()
db.create_all()


# celery 启动
celery -A run:celery_app worker --pool=solo -l info
