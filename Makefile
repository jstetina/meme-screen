.PHONY: help build up down logs shell test config clean

COMPOSE=podman-compose

help:
	@echo "Available targets:"
	@echo "  make config             - Copy and edit config.env"
	@echo "  make build              - Build Podman image"
	@echo "  make up                 - Start container"
	@echo "  make down               - Stop container"
	@echo "  make logs               - View container logs"
	@echo "  make shell              - Open shell in container"
	@echo "  make test               - Run tests in container"
	@echo "  make clean              - Clean up containers and images"

config:
	@if [ ! -f config.env ]; then \
		cp config.env.example config.env; \
		echo "[DONE] Created config.env - edit it with your settings"; \
	else \
		echo "[INFO] config.env already exists"; \
	fi

build: config
	$(COMPOSE) build

up: build
	./start.sh

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f meme-screen

shell:
	$(COMPOSE) exec meme-screen /bin/bash

test: build
	$(COMPOSE) run --rm meme-screen python -c "from meme_screen import MemeScreen; print('[PASS] Application imports successfully')"

clean:
	$(COMPOSE) down -v
	podman rmi localhost/meme-screen:latest 2>/dev/null || true
