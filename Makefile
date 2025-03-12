devserver:
	pip install -r app/requirements.txt
	pip install -r examples/requirements.txt
	cd app/frontend && npm run build
	FLASK_APP=app.app FLASK_ENV=development CONFIG_FILE_PATH=example_config.yaml PYTHONPATH=$PYTHONPATH:../examples flask run

.PHONY: devserver

generate-example-data:
	python examples/generate_data_access_log.py
	python examples/generate_data_kafka.py

.PHONY: generate-example-data

serve:
	CONFIG_FILE_PATH=example_config.yaml gunicorn -b 0.0.0.0:5000 app.app:app

.PHONY: serve

build-docker:
	docker build -t script-runner .

.PHONY: build-docker

run-docker:
	docker run --network devservices --rm -p 5000:5000 script-runner

.PHONY: run-docker