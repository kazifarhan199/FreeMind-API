# Setup

Python 3.8.8 is used in this project

Step 1
    `pip install -r requirements.py`

Step 2
    `cd src`

Step 3
    `gunicorn Social_API.wsgi:application -b:59000 &`

Step 4
    `celery --app=Social_API worker -l INFO --concurrency=1 &`

Step 5
    (if rabbitmq-server  is not running)
    `~/software/rabbitmq_server-3.10.6/sbin/rabbitmq-server  start`
