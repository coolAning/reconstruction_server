import os
import subprocess
from werkzeug.datastructures import FileStorage
import logging
import requests
from flask import Blueprint,Response, current_app
from app.utils.core import db
from flask import request
from app.models.model import Video
from app.utils.response import ResMsg
from app.utils.util import route
from app.utils.code import ResponseCode
from werkzeug.utils import secure_filename
from app.celery import process_video



bp = Blueprint("camera", __name__, url_prefix='/camera')

logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@route(bp, '/file', methods=['POST'])
def upload_file():
    res = ResMsg()
    res.update(code=ResponseCode.InvalidParameter)
    
     # 从表单中获取 user_id
    user_id = request.form.get('user_id', type=int)
    n_steps = request.form.get('n_steps', type=int)
    if 'file' not in request.files:
        res.update(code=ResponseCode.InvalidParameter)
    else:
        file = request.files['file']
        if file.filename == '':
            res.update(code=ResponseCode.NoSelectedFile)
        else:
            if file and allowed_file(file.filename):
                filename = secure_filename(str(user_id) +'_'+ file.filename)
                path = filename.rsplit('.', 1)[0]
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], path , filename)
                video = Video.query.filter_by(user_id=user_id,name=filename).first()                
                if os.path.exists(filepath) or video:
                    res.update(code=ResponseCode.FileNameDuplicate)
                else:
                    # 检查目录是否存在
                    dirpath = os.path.dirname(filepath)
                    if not os.path.exists(dirpath):
                        # 如果目录不存在，创建目录
                        os.makedirs(dirpath)
                    file.save(filepath)
                    out_path = os.path.join(current_app.config['UPLOAD_FOLDER'], path,'transforms.json')
                    # 使用colmap处理视频数据
                    result = process_video.delay(filepath,out_path,user_id,filename,n_steps)
                    video = Video(user_id=user_id, name=filename, status=0 ,task_id=result.id)
                    db.session.add(video)
                    db.session.commit()
                    res.update(code=ResponseCode.Success, data={"task_id": result.id})
     
            else:
                res.update(code=ResponseCode.InvalidFileType)
   
    return res.data


@route(bp, '/complete', methods=['POST'])
def complete():
    res = ResMsg()
    res.update(code=ResponseCode.SystemError)
    task_id = request.json.get("task_id")
    video = Video.query.filter_by(task_id=task_id).first()
    if video:
        video.status = 2
        video.task_id = None
        db.session.commit()
        res.update(code=ResponseCode.Success)
    return res.data

