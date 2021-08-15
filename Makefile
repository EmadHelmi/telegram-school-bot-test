.DEFAULT_GOAL := default
DOCKERRUN = docker run --rm -v `pwd`/school_bot:/code/school_bot --network host --env-file deploy/school_bot.env school-bot-code bash -c
MANAGE = python3 manage.py

# If the first argument is "manage"...
ifeq (manage,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "manage"
  MANAGE_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(MANAGE_ARGS):;@:)
endif

collect-pip-requirements: ## Save all pip requirements in deploy/requirements.txt
	pip freeze > deploy/requirements.txt
up-dep: ## Up dependencies (ex: database, redis, ...) using docker-compose up
	docker-compose -f deploy/dep-docker-compose.yml up -d
down-dep: ## Down dependencies using docker-compose down
	docker-compose -f deploy/dep-docker-compose.yml down
build-core: ## Build docker base/core image
	docker build -t school-bot/core -f deploy/core .
build: ## Build code. If you have changed any Python requirements, it should called again
	docker build -f deploy/Dockerfile --target builder -t school-bot-code:latest .
default: ## Default target build everything and will up dependencies
	make down-dep && make build-core && make build && make up-dep && make manage create_tables
.PHONY: manage
manage : ## manage.py alternative. Use `make -- manage <your-command>` instead of `python3 manage.py <your-commnad>`
	${DOCKERRUN} "${MANAGE} $(MANAGE_ARGS)"

help: ## Show make file help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
