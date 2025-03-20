devserver:
	pip install -r requirements.txt
	pip install -r examples/requirements.txt
	cd app/frontend && npm run build
	FLASK_APP=app.app FLASK_ENV=development CONFIG_FILE_PATH=example_config_combined.yaml PYTHONPATH=$PYTHONPATH:../examples flask run

.PHONY: devserver

devserver-main:
	pip install -r requirements.txt
	cd app/frontend && npm run build
	FLASK_APP=app.app FLASK_ENV=development CONFIG_FILE_PATH=example_config_main.yaml PYTHONPATH=$PYTHONPATH:../examples flask run --port 5001

.PHONY: devserver-main

devserver-region:
	pip install -r requirements.txt
	pip install -r examples/requirements.txt
	FLASK_APP=app.app FLASK_ENV=development CONFIG_FILE_PATH=example_config_s4s.yaml PYTHONPATH=$PYTHONPATH:../examples flask run --port 5002
.PHONY: devserver-region

generate-example-data:
	python examples/generate_data_access_log.py
	python examples/generate_data_kafka.py

.PHONY: generate-example-data

serve:
	CONFIG_FILE_PATH=example_config_combined.yaml gunicorn -b 0.0.0.0:5000 app.app:app

.PHONY: serve

build-docker:
	docker build -t script-runner-combined .

.PHONY: build-docker

run-docker:
	docker run --network devservices --rm -p 5000:5000 script-runner-combined

.PHONY: run-docker
