import os
import subprocess
from celery import Celery
from flask import current_app
import shutil
import requests
from app.models.model import Video
from app.utils.core import db
celery_app = Celery(__name__)

# @celery_app.task
# def flask_app_context():
#     """
#     celery使用Flask上下文
#     :return:
#     """
#     with current_app.app_context():
#         return str(current_app.config)


@celery_app.task(bind=True)
def process_video(self , video_path , out_path,user_id,filename,n_steps):
    # 这里是你的长时间运行的任务
    command = ["python", "colmap2nerf.py", "--video_in", video_path, "--video_fps", "2", "--run_colmap", "--aabb_scale", "32", "--out", out_path, "--overwrite"]
    # 创建一个子进程来运行命令，并获取子进程的输出
    process = subprocess.Popen(command, cwd=current_app.config['ROOT_PATH'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    while True:
        # 读取一行输出
        output = process.stdout.readline()
        if output:
            # 更新任务状态
            self.update_state(state='PROGRESS', meta={'current': output})
            
        # 如果子进程已经结束，那么退出循环
        if process.poll() is not None:
            break

    rc = process.poll()

    # 更新任务状态为 'SUCCESS'
    self.update_state(state='SUCCESS', meta={'current': 'Task completed'})
    
    # 更新数据库
    video = Video.query.filter_by(user_id=user_id,name=filename).first()
    
    if video:
        video.status = 1
        video.task_id = None
        db.session.commit()
        
    os.remove(video_path)
        
    process_file.delay(filename,user_id,n_steps)
    
    return rc

@celery_app.task
def process_file(fullfilename, user_id, n_steps,filepath="./video"):
    
    filename = fullfilename.split('.')[0]
    
    # 创建 zip 文件
    zip_path = os.path.join(filepath, filename)
    shutil.make_archive(zip_path, 'zip' ,os.path.join(filepath, filename))
    
    # 删除原文件夹
    dir_path = os.path.join(filepath, filename)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    
    # 发送 zip 文件给后端
    zip_file_path = f'{zip_path}.zip'
    if os.path.exists(zip_file_path):
        with open(zip_file_path, 'rb') as f:
            try:
                url = current_app.config['ALGORITHM_URL']
                response = requests.post(f'{url}/upload', files={'file': f} ,data={'n_steps': n_steps})
                response.raise_for_status()  # 抛出 HTTP 错误，如果有的话
                data = response.json()  # 获取 JSON 数据
                task_id = data.get('task_id')
                # 将 task_id 存储到数据库中
                video = Video.query.filter_by(user_id=user_id,name=fullfilename).first()
                if video:
                    video.task_id = task_id
                    db.session.commit()
            except requests.exceptions.RequestException as e:
                print(f'Failed to send file: {e}')
    
    # 删除 zip 文件
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
        
        