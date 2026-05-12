#!/usr/bin/env bash
set -euo pipefail

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

echo "Deployment applied. Waiting for pod to be ready..."
kubectl -n blog wait --for=condition=ready pod -l app=blog --timeout=60s

echo "Running migrations and creating superuser..."
kubectl -n blog exec deploy/blog -- uv run manage.py migrate
kubectl -n blog exec deploy/blog -- uv run manage.py createsuperuser --noinput

echo "Done. Access admin at https://blog.evillab.tech/admin"
