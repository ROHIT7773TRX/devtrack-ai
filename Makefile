# ============================================================
# DevTrack AI - Local Development & Operations Makefile
# ============================================================

.PHONY: help install test compose-up compose-down tf-init tf-plan k8s-apply

help:
	@echo "DevTrack AI Management Commands:"
	@echo "  make install      - Install backend dependencies"
	@echo "  make test         - Run pytest unit and integration test suite"
	@echo "  make compose-up   - Start local multi-container stack (Postgres + Backend + Frontend)"
	@echo "  make compose-down - Stop local multi-container stack"
	@echo "  make tf-plan      - Preview Terraform AWS infrastructure changes"
	@echo "  make k8s-apply    - Apply Kubernetes manifests"

install:
	pip install -r app/backend/requirements.txt

test:
	python -m pytest tests/ -v

compose-up:
	docker compose -f docker/docker-compose.yml up --build -d

compose-down:
	docker compose -f docker/docker-compose.yml down

tf-plan:
	cd terraform && terraform init && terraform plan

k8s-apply:
	kubectl apply -f kubernetes/
