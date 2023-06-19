# Setup

Python 3.8.8 is used in this project

Step 1
	Clone the repo

Step 2
	This step will only work on deployment server so if on developemnt sercer(without Nvidia gpu), skip this step.
	
	Make a folder called `models` in the root of the the project and place the `best_model-xlnet-base-cased` folder inside it.
	You can get the `best_model-xlnet-base-cased` from the Box folder.

Step 3
	Install dependencies
	if on deployment server (need a Nvidia GPU)
    	`pip install -r requirements.py`
    if on development server (tested on mac)
    	`pip install -r requirements_dev.txt`

Step 2
    `cd src`

Step 3
	if deployment
	    `gunicorn Social_API.wsgi:application -b:59000 --worker-class gevent` # --daemon
	else:
		In this case the NLP model is not used
		`python manage.py runserver` 

If want to run recommendation server:
	Step 4
	    (if rabbitmq-server  is not running)
	    `~/software/rabbitmq_server-3.10.6/sbin/rabbitmq-server  start`

	Step 5
    	`celery --app=Social_API worker -l INFO --concurrency=1 -B`

