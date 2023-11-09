from celery import Celery

celery_app = Celery('celery', broker='redis://localhost', include=['webplayer.metadata'])
