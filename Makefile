.DEFAULT_GOAL := help
STACK_DIRS = 00-base-stack \
             10-met-stack \
             20-main-stack \
             21-git-stack \
             30-dev-stack \
             31-ops-stack \
             32-prj-stack \
             33-mon-stack


.PHONY: all
all: up ## Default target

.PHONY: up
up: ## Up all stacks in order
	docker network create shared
	@for dir in $(STACK_DIRS); do \
		echo "Starting $$dir..."; \
		docker compose --env-file .env -f $$dir/docker-compose.yml up -d; \
	done

down: ## Down all stacks in reverse order
	@for dir in $(shell echo "$(STACK_DIRS)" | tr ' ' '\n' | tac); do \
		echo "Stopping $$dir..."; \
		docker compose --env-file .env -f $$dir/docker-compose.yml down; \
	done
	docker network rm shared

.PHONY: status
status: ## Show status of all stacks
	@for dir in $(STACK_DIRS); do \
		echo "\nStatus for $$dir:"; \
		docker compose -f $$dir/docker-compose.yml ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"; \
	done

.PHONY: restart
restart: down up ## Restart all stacks

.PHONY: clean
clean: ## Clean all stacks (down + remove volumes)
	@for dir in $(shell echo "$(STACK_DIRS)" | tr ' ' '\n' | tac); do \
		echo "Cleaning $$dir..."; \
		docker compose --env-file .env -f $$dir/docker-compose.yml down -v; \
	done

.PHONY: dist-clean
dist-clean: ## ## Clean all stacks on system (down + remove volumes)
	docker system prune --all --force --volumes

.PHONY: help
help: ## Print help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
