IMAGE := elerevil/blog
TAG := latest

.PHONY: build push deploy lint format check

build:
	podman build -t $(IMAGE):$(TAG) .

push: build
	podman push $(IMAGE):$(TAG)

lint:
	uv run ruff check .

format:
	uv run ruff format .

check:
	uv run manage.py makemigrations --check --dry-run

server:
	uv run manage.py runserver

collectstatic:
	uv run manage.py collectstatic --noinput

migrate:
	uv run manage.py migrate

migrations:
	uv run manage.py makemigrations

deploy: push
	@echo "Image pushed. Run on Hetzner:"
	@echo "  kubectl set image deploy/blog blog=$(IMAGE):$(TAG) -n blog"
	@echo "  kubectl rollout status deploy/blog -n blog"
