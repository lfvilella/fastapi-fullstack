all:
	@echo "Hello $(LOGNAME), nothing to do by default"
	@echo "Try 'make help'"

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: delete-container ## Build the container
	@docker-compose up --build -d

test: start ## Run tests
	@docker-compose exec backend pytest

restart: ## Restart the container
	@docker-compose restart backend

cmd: start ## Access bash
	@docker-compose exec backend /bin/bash

up: start ## Start Fastapi dev server
	@docker-compose exec backend uvicorn backend.app.api:app --host 0.0.0.0 --reload

start:
	@docker-compose start

down: ## Stop container
	@docker-compose stop || true

delete-container: down
	@docker-compose down || true

remove: delete-container ## Delete containers and images

.DEFAULT_GOAL := help