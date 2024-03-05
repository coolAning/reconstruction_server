import base64
import datetime
import decimal
import uuid
from werkzeug.datastructures import FileStorage
from flask.json import JSONEncoder as BaseJSONEncoder
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class JSONEncoder(BaseJSONEncoder):

    def default(self, o):
        """
        如有其他的需求可直接在下面添加
        :param o:
        :return:
        """
        if isinstance(o, datetime.datetime):
            # 格式化时间
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, datetime.date):
            # 格式化日期
            return o.strftime('%Y-%m-%d')
        if isinstance(o, decimal.Decimal):
            # 格式化高精度数字
            return str(o)
        if isinstance(o, uuid.UUID):
            # 格式化uuid
            return str(o)
        if isinstance(o, bytes):
            # 格式化字节数据
            return o.decode("utf-8")
        if isinstance(o, FileStorage):
            # 将图片转换成base64编码格式
            with o.stream as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return super(JSONEncoder, self).default(o)
