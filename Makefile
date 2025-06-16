devserver:
	pip install -r requirements.txt
	cd script_runner/frontend && npm install && npm run build
	FLASK_APP=examples.app FLASK_ENV=development CONFIG_FILE_PATH=example_config_combined.yaml flask run

.PHONY: devserver

devserver-main:
	pip install -r requirements.txt
	cd script_runner/frontend && npm install && npm run build
	FLASK_APP=script_runner.app FLASK_ENV=development CONFIG_FILE_PATH=example_config_main.yaml PYTHONPATH=$PYTHONPATH:../examples flask run --port 5001

.PHONY: devserver-main

devserver-region:
	pip install -r requirements.txt
	FLASK_APP=script_runner.app FLASK_ENV=development CONFIG_FILE_PATH=example_config_local.yaml PYTHONPATH=$PYTHONPATH:../examples flask run --port 5002
.PHONY: devserver-region

serve:
	CONFIG_FILE_PATH=example_config_combined.yaml gunicorn -b 0.0.0.0:5000 examples.app:app

.PHONY: serve

build-docker:
	docker build -t script-runner-combined .

.PHONY: build-docker

run-docker:
	docker run --network devservices --rm -p 5000:5000 script-runner-combined

.PHONY: run-docker
