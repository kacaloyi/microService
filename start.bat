@echo off 
taskkill -f -t -im celery.exe
taskkill -f -t -im python.exe
start "celery worker"  celery --app=app.celery worker -l INFO
start "python app.py"  python app.py

