.PHONY: help setup build deploy logs shell clean

QUADLET_DIR = $(HOME)/.config/containers/systemd

help:
	@echo "  make setup    - One-time host setup (run once after first clone)"
	@echo "  make build    - Build container image"
	@echo "  make deploy   - Install Quadlet and start service"
	@echo "  make logs     - Stream service logs"
	@echo "  make shell    - Open shell in running container"
	@echo "  make clean    - Stop and remove service and image"

setup:
	sudo apt-get install -y xserver-xorg-legacy
	printf 'allowed_users=anybody\nneeds_root_rights=yes\n' | sudo tee /etc/X11/Xwrapper.config
	loginctl enable-linger $(USER)

build:
	podman build -t localhost/meme-screen:latest .

deploy: build
	mkdir -p $(QUADLET_DIR)
	cp quadlet/meme-screen.container quadlet/meme-screen-sync.container $(QUADLET_DIR)/
	systemctl --user daemon-reload
	systemctl --user start meme-screen meme-screen-sync

logs:
	journalctl --user -fu meme-screen

logs-sync:
	journalctl --user -fu meme-screen-sync

shell:
	podman exec -it meme-screen /bin/bash

clean:
	-systemctl --user stop meme-screen meme-screen-sync
	-rm -f $(QUADLET_DIR)/meme-screen.container $(QUADLET_DIR)/meme-screen-sync.container
	-systemctl --user daemon-reload
	-podman rmi localhost/meme-screen:latest

