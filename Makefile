export PYTHONPATH := $(shell pwd)
ENV ?= DEV

.DEFAULT_GOAL := help

## === ENV SETUP ===

dev-env: ## Prépare l’environnement de développement
	chmod +x scripts/dev_env.sh
	./scripts/dev_env.sh

## === INIT COMMANDS ===

init-all: ## Initialise DB + migrations
	$(MAKE) init-db
	$(MAKE) init-migration

init-db: ## Démarre PostgreSQL et crée les BDD nécessaires
	docker-compose up -d
	@echo "⏳ Waiting for Postgres..."
	@sleep 3
	@until pg_isready -h localhost -p 5434 > /dev/null; do echo "⏳ Waiting for Postgres at localhost:5434..."; sleep 1; done
	@echo "✅ Postgres is ready!"
	@echo "🧱 Creating test database if needed"
	@docker exec -it stripe_db psql -U stripe_user -d postgres -c "CREATE DATABASE stripe_test;" || echo "✔️ stripe_test already exists."
	@echo "🧱 Initializing tables in both databases"
	@python scripts/init_db.py
	@docker exec -it stripe_db psql -U stripe_user -d stripe_db -c "\dt"
	@docker exec -it stripe_db psql -U stripe_user -d stripe_test -c "\dt"
	@echo "✅ Tables verified in both databases"

init-migration: ## Crée la migration initiale si aucune n'existe
	$(MAKE) dev-env
	@if [ ! -d alembic/versions ] || [ -z "$$(ls -A alembic/versions)" ]; then \
		echo "🧱 No migration found. Creating initial migration..."; \
		mkdir -p alembic/versions; \
		alembic revision --autogenerate -m "initial stripe schema"; \
		alembic upgrade head; \
	else \
		echo "✅ Migrations already exist. Skipping init-migration."; \
	fi

## === MIGRATION COMMANDS ===

migrate: ## Crée et applique une migration avec message `m=...`
	$(MAKE) dev-env
	alembic revision --autogenerate -m "$(m)"
	alembic upgrade head

upgrade-db: ## Applique toutes les migrations
	$(MAKE) dev-env
	alembic upgrade head

## === RESET COMMANDS ===

reset-all: ## Réinitialise complètement la DB + migrations
	$(MAKE) reset-db
	$(MAKE) reset-migration

reset-db: ## Supprime les volumes et recrée les bases
	docker-compose down -v
	$(MAKE) init-db

reset-migration: ## Supprime et régénère les migrations
	rm -rf alembic/versions/*
	mkdir -p alembic/versions
	$(MAKE) migrate m="reset migration"

## === STRIPE WORKFLOW ===

populate: ## ⚠️ Remplit Stripe (seulement en ENV=DEV)
ifeq ($(ENV),DEV)
	@echo "🚀 Populating Stripe sandbox with test fixtures..."
	@python scripts/populate.py --fixture fixtures/stripe_batch_fixture.json
else
	@echo "❌ populate interdit en ENV=$(ENV). Utilisez ENV=DEV."
	@exit 1
endif

populate-force: ## Forcer le remplissage Stripe (ENV=DEV uniquement)
ifeq ($(ENV),DEV)
	@echo "🚀 Force-populating Stripe sandbox with test fixtures..."
	@python scripts/populate.py --force --fixture fixtures/stripe_batch_fixture.json
else
	@echo "❌ populate-force interdit en ENV=$(ENV). Utilisez ENV=DEV."
	@exit 1
endif

fetch: ## Télécharge les données depuis Stripe vers JSON
	@echo "📥 Fetching Stripe data into JSON files..."
	@chmod +x scripts/fetch_stripe_data.sh
	@chmod +x scripts/fetch_payment_methods.sh
	@./scripts/fetch_stripe_data.sh
	@./scripts/fetch_payment_methods.sh

ingest-%: ## Ingest une table spécifique via --source=
	@echo "📥 Ingesting table '$*' using --source=$(SOURCE)"
	@python scripts/ingest/ingest_$*.py --source $(SOURCE) $(if $(FILE),--file $(FILE))

check-db-integrity: ## Vérifie l'intégrité de la base
	@echo "🔍 Checking database integrity..."
	@python scripts/check_db_integrity.py

ingest-all: ## Ingest toutes les tables via --source
	@echo "📦 Ingesting ALL tables from --source=$(SOURCE)"
	@python scripts/ingest/ingest_all.py --source $(SOURCE) $(if $(JSON_DIR),--json-dir $(JSON_DIR))
	@python scripts/check_db_integrity.py

populate-all: ## ⚠️ Populate + Fetch + Ingest-All (DEV uniquement)
ifeq ($(ENV),DEV)
	@$(MAKE) populate
	@$(MAKE) fetch
	@$(MAKE) ingest-all SOURCE=json JSON_DIR=data/imported_stripe_data
else
	@echo "❌ populate-all interdit en ENV=$(ENV). Utilisez ENV=DEV."
	@exit 1
endif

clean: ## Supprime les données locales importées
	@echo "🧹 Nettoyage des données locales..."
	@rm -rf data/imported_stripe_data/*

all: init-all populate-all ## Initialise et peuple complètement le projet (DEV)

## === HELP COMMAND ===

help: ## Affiche cette aide
	@echo "🔧 Utilisation : make <commande> [ENV=DEV|PROD]"
	@echo ""
	@echo "📘 Commandes disponibles :"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
