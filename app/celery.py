import subprocess
from celery import Celery
from flask import current_app

celery_app = Celery(__name__)

# @celery_app.task
# def flask_app_context():
#     """
#     celery使用Flask上下文
#     :return:
#     """
#     with current_app.app_context():
#         return str(current_app.config)


@celery_app.task
def process_video(video_path , out_path):
    # 这里是你的长时间运行的任务
    command = ["python", "colmap2nerf.py", "--video_in", video_path, "--video_fps", "2", "--run_colmap", "--aabb_scale", "32", "--out", out_path, "--overwrite"]
    subprocess.run(command,cwd=current_app.config['ROOT_PATH'])
    
    
