.PHONY: help install install-dev install-prod run dev test test-cov lint format type-check clean
.PHONY: migrate migration seed reset-db reindex docker-build docker-up docker-down
.PHONY: collect-static deploy-railway deploy-render

# Variables
PYTHON = python
PIP = pip
FLASK = flask
PYTEST = pytest
BLACK = black
RUFF = ruff
MYPY = mypy

# Default target
help: ## Afficher l'aide
	@echo "Commandes disponibles :"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Installer les dépendances de production
	$(PIP) install -e .

install-dev: ## Installer les dépendances de développement
	$(PIP) install -e .[dev,admin]

install-prod: ## Installer pour la production
	$(PIP) install --no-dev -e .

# Développement
run: ## Lancer le serveur de développement
	$(FLASK) --app app run --debug --host=0.0.0.0 --port=5000

dev: ## Lancer en mode développement avec rechargement automatique
	$(FLASK) --app app run --debug --reload

# Tests
test: ## Exécuter les tests
	$(PYTEST) -v

test-cov: ## Exécuter les tests avec couverture
	$(PYTEST) --cov=app --cov-report=term-missing --cov-report=html

test-unit: ## Tests unitaires uniquement
	$(PYTEST) tests/unit/ -v

test-integration: ## Tests d'intégration uniquement
	$(PYTEST) tests/integration/ -v

test-watch: ## Tests en mode watch
	$(PYTEST) -f

# Qualité de code
lint: ## Linter le code avec ruff
	$(RUFF) check app tests scripts

lint-fix: ## Corriger automatiquement les problèmes de linting
	$(RUFF) check --fix app tests scripts

format: ## Formater le code avec black
	$(BLACK) app tests scripts

format-check: ## Vérifier le formatage sans modifier
	$(BLACK) --check app tests scripts

type-check: ## Vérification de types avec mypy
	$(MYPY) app

check-all: lint format-check type-check ## Toutes les vérifications de qualité

# Base de données
migrate: ## Appliquer les migrations
	$(FLASK) --app app db upgrade

migration: ## Créer une nouvelle migration
	$(FLASK) --app app db migrate -m "$(msg)"

seed: ## Peupler la base avec des données de test
	$(PYTHON) scripts/seed.py

reset-db: ## Réinitialiser complètement la base de données
	rm -f instance/app.db
	$(FLASK) --app app db upgrade
	$(PYTHON) scripts/seed.py

# Recherche
reindex: ## Réindexer le moteur de recherche
	$(PYTHON) scripts/reindex_search.py

# Docker
docker-build: ## Construire l'image Docker
	docker build -t wow-flask .

docker-up: ## Lancer les services Docker
	docker-compose up -d

docker-down: ## Arrêter les services Docker
	docker-compose down

docker-logs: ## Voir les logs Docker
	docker-compose logs -f

docker-shell: ## Shell dans le conteneur
	docker-compose exec web bash

# Production
collect-static: ## Collecter les fichiers statiques (si nécessaire)
	@echo "Collecte des fichiers statiques..."

# Déploiement
deploy-railway: ## Déployer sur Railway
	railway up

deploy-render: ## Instructions de déploiement Render
	@echo "Pour déployer sur Render :"
	@echo "1. Connectez votre repo GitHub à Render"
	@echo "2. Configurez les variables d'environnement"
	@echo "3. Le déploiement se fera automatiquement"

# Nettoyage
clean: ## Nettoyer les fichiers temporaires
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf build/ dist/

clean-all: clean ## Nettoyage complet (inclut les dépendances)
	rm -rf venv/ node_modules/

# Utilitaires
shell: ## Lancer un shell Flask
	$(FLASK) --app app shell

routes: ## Afficher les routes de l'application
	$(FLASK) --app app routes

# Backup et export
backup: ## Créer un backup de la base de données
	$(PYTHON) scripts/backup.py

export: ## Exporter les tutoriels en Markdown
	$(PYTHON) scripts/export_import.py export

import: ## Importer des tutoriels depuis un ZIP
	$(PYTHON) scripts/export_import.py import $(file)

# Performance
profile: ## Profiler l'application
	$(PYTHON) -m cProfile -o profile.stats -m flask --app app run

# Sécurité
audit: ## Audit de sécurité des dépendances
	$(PIP) audit

# Setup initial
setup: install-dev migrate seed ## Configuration initiale complète
	@echo "Configuration initiale terminée !"
	@echo "Lancez 'make run' pour démarrer le serveur"

# Environnement
check-env: ## Vérifier la configuration d'environnement
	@echo "Vérification de l'environnement..."
	@$(PYTHON) -c "from app.config import DevelopmentConfig; print('✓ Configuration OK')"

# CI/CD
ci: lint format-check type-check test ## Pipeline CI/CD complet

# Version info
version: ## Afficher les versions
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Flask: $$($(FLASK) --version)"
	@echo "pip: $$($(PIP) --version)"