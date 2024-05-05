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
from app.celery import capture_frames_from_rtmp, process_video



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
    video_name = request.form.get('video_name', type=str)
    aabb = request.form.get('aabb', type=int)
    
    if 'file' not in request.files:
        res.update(code=ResponseCode.InvalidParameter)
    else:
        file = request.files['file']
        if file.filename == '':
            res.update(code=ResponseCode.NoSelectedFile)
        else:
            if file and allowed_file(file.filename):
                filename = secure_filename(str(user_id) +'_'+ video_name + '.mp4')
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
                    result = process_video.delay(filepath,out_path,user_id,filename,n_steps,aabb)
                    video = Video(user_id=user_id, name=filename, status=0 ,task_id=result.id,train_steps=n_steps,aabb=aabb)
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
    # 暂时采取发送渲染请求的方法
    url = current_app.config['ALGORITHM_URL']+ '/render'
    
    data = {'origin': True,'filename':video.name.split('.')[0],'picture_quality': 1}
    requests.post(url, json=data)
    return res.data

@route(bp, '/getModelList', methods=['POST'])
def get_model_list():
    res = ResMsg()
    res.update(code=ResponseCode.SystemError)
    user_id = request.json.get("user_id")
    videos = Video.query.filter_by(user_id=user_id).all()
    data = []
    url = current_app.config['ALGORITHM_URL']+ '/render'
    
    
    for video in videos:
        if video.status == 2:
            postData = {'origin': True,'filename':video.name.split('.')[0]}
            response = requests.post(url, json=postData)
            data.append({"url":response.json().get("url"),"name":video.name.split('.')[0].split('_',1)[1]})
        else:
            data.append({"url":current_app.config['ALGORITHM_URL']+'/static/occupancy.png',"name":video.name.split('.')[0].split('_',1)[1]})
    res.update(code=ResponseCode.Success,data=data)
    return res.data

@route(bp, '/delete', methods=['POST'])
def delete():
    res = ResMsg()
    res.update(code=ResponseCode.SystemError)
    try:
        user_id = request.json.get("user_id")
        video_name_list = request.json.get("video_name_list")
        for video_name in video_name_list:
            video_name = str(user_id) +'_'+ video_name + '.mp4'
            video = Video.query.filter_by(user_id=user_id,name=video_name).first()
            if video:
                # 删除算法端截图数据
                url = current_app.config['ALGORITHM_URL']+ '/delete'
                postData = {'filename':video_name.split('.')[0]}
                response = requests.post(url, json=postData)
                if response.status_code == 200:
                    db.session.delete(video)
                    db.session.commit()
                    res.update(code=ResponseCode.Success)
    except Exception as e:
        res.update(code=ResponseCode.Fail, data={"error": str(e)})
    return res.data


@route(bp, '/setDroneVideo', methods=['POST'])
def setDroneVideo():
    res = ResMsg()
    res.update(code=ResponseCode.SystemError)
    try:
        user_id = request.json.get("user_id")
        name = request.json.get("name")
        video_name = str(user_id) +'_'+ name
        n_steps = request.json.get("n_steps")
        aabb = request.json.get("aabb")
        video = Video.query.filter_by(user_id=user_id,name=video_name).first()    
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], video_name , "images") 
        if os.path.exists(filepath) or video:
            res.update(code=ResponseCode.FileNameDuplicate)
        else:
            video = Video(user_id=user_id, name=video_name, status=0 ,task_id=None,train_steps=n_steps,aabb=aabb)
            #  接收rtmp流截取图片
            dirpath = os.path.dirname(filepath)
            if not os.path.exists(dirpath):
                # 如果目录不存在，创建目录
                os.makedirs(dirpath)
            out_path = os.path.join(current_app.config['UPLOAD_FOLDER'], video_name,'transforms.json')
            url = "rtmp://127.0.0.1:6666/live" + "/" + video_name
            result = capture_frames_from_rtmp.delay(url,user_id,video_name,n_steps,out_path,aabb)
            video.task_id = result.id
            db.session.add(video)
            db.session.commit()
            res.update(code=ResponseCode.Success)

            
    except Exception as e:
        res.update(code=ResponseCode.Fail, data={"error": str(e)})
    return res.data
