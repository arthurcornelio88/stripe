# ========= GLOBAL CONFIG =========

export PYTHONPATH := $(shell pwd)
ENV ?= DEV
JSON_DIR ?= data/imported_stripe_data


.DEFAULT_GOAL := help

# ========= ENV SETUP ==========

dev-env: ## Charge l'environnement depuis le fichier .env.<ENV>
	chmod +x scripts/dev_env.sh
	./scripts/dev_env.sh

# ========= TEST COMMAND ===========

pytest: ## Lance les tests unitaires
	@echo "🧪 Lancement des tests unitaires (ENV=$(ENV))..."
	ENV=$(ENV) pytest tests/

test-connection: ## Teste la connexion DB en ENV courant
	ENV=$(ENV) python scripts/test_connection.py

# ========= INIT COMMANDS ==========

init-all: ## Initialise DB + migrations
	$(MAKE) init-db
	$(MAKE) init-migration

init-db: ## Initialise PostgreSQL local (DEV) ou distant (PROD)
ifeq ($(ENV),DEV)
	docker-compose --env-file .env.dev up -d
	@echo "⏳ Waiting for Postgres..."
	@sleep 3
	@until pg_isready -h localhost -p 5434 > /dev/null; do echo "⏳ Waiting for Postgres at localhost:5434..."; sleep 1; done
	@echo "✅ Postgres is ready!"
else
	@echo "✅ ENV=PROD → skipping local DB startup"
endif
	@echo "🧱 Initializing tables"
	@python scripts/init_db.py

init-migration: ## Crée la migration initiale si aucune n'existe
	$(MAKE) dev-env
ifeq ($(ENV),DEV)
	@if [ ! -d alembic/versions ] || [ -z "$$(ls -A alembic/versions)" ]; then \
		echo "🧱 No migration found. Creating initial migration..."; \
		mkdir -p alembic/versions; \
		alembic revision --autogenerate -m "initial stripe schema"; \
		alembic upgrade head; \
	else \
		echo "✅ Migrations already exist. Skipping init-migration."; \
	fi
else
	@echo "ℹ️ Skipping migration init in ENV=$(ENV)"
endif

# ========= MIGRATION COMMANDS ==========

migrate: ## Crée et applique une migration avec message `m=...`
	$(MAKE) dev-env
	alembic revision --autogenerate -m "$(m)"
	alembic upgrade head

upgrade-db: ## Applique toutes les migrations
	$(MAKE) dev-env
	alembic upgrade head

# ========= RESET COMMANDS ==========

reset-all: ## Réinitialise complètement la DB + migrations
	$(MAKE) reset-db
	$(MAKE) reset-migration

reset-db: ## Supprime les volumes et recrée les bases (DEV uniquement)
ifeq ($(ENV),DEV)
	docker-compose down -v
	$(MAKE) init-db
else
	@echo "❌ Refus de reset en ENV=PROD"
	@exit 1
endif

reset-migration: ## Supprime et régénère les migrations
	rm -rf alembic/versions/*
	mkdir -p alembic/versions
	$(MAKE) migrate m="reset migration"

# ========= STRIPE WORKFLOW ==========

populate: ## ⚠️ Remplit Stripe (seulement en ENV=DEV)
ifeq ($(ENV),DEV)
	@echo "🚀 Populating Stripe sandbox with test fixtures..."
	@python scripts/populate.py --fixture fixtures/stripe_batch_fixture.json
else
	@echo "❌ populate interdit en ENV=$(ENV). Utilisez ENV=DEV."
	@exit 1
endif

populate-force: ## Forcer le remplissage Stripe (DEV uniquement)
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

# ========= GCP BUCKET COMMANDS ==========
tf_bucket:
	@echo "🔐 Vérification des credentials..."
	@if [ ! -f infra/gcp/gcp_service_account.json ]; then \
		echo "❌ Fichier manquant : infra/gcp/gcp_service_account.json"; \
		exit 1; \
	fi; \
	export GOOGLE_APPLICATION_CREDENTIALS=infra/gcp/gcp_service_account.json; \
	echo "🔎 Vérification de l'existence du bucket GCS..."; \
	if gcloud storage buckets describe "stripe-oltp-bucket-prod" --project="stripe-b2-gcp" > /dev/null 2>&1; then \
		echo "✅ Le bucket 'stripe-oltp-bucket-prod' existe déjà. Skip Terraform apply."; \
	else \
		echo "🚀 Le bucket n'existe pas, lancement du provisioning Terraform..."; \
		terraform -chdir=infra/gcp init; \
		terraform -chdir=infra/gcp plan; \
		terraform -chdir=infra/gcp apply -auto-approve; \
		echo "✅ Bucket GCS créé avec succès !"; \
	fi


dump:
	@echo "💾 Dumping PostgreSQL database to JSON..."
	python scripts/dump_all_tables.py

push_to_cloud:
	@echo "🚀 Uploading local data folders to GCS bucket..."
	python scripts/push_to_gcs.py


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

all: init-all ## Initialise, teste, et peuple les données (en DEV uniquement)
ifeq ($(ENV),DEV)
	@$(MAKE) test-connection ENV=DEV
	@$(MAKE) pytest
	@$(MAKE) populate-all
else
	@echo "✅ ENV=PROD → executing safe ingestion flow"
	@$(MAKE) test-connection ENV=PROD

	@echo "☁️ Provisioning GCS bucket with Terraform..."
	@$(MAKE) tf_bucket

	@if [ "$(INGEST_SOURCE)" = "api" ]; then \
		echo "📡 Ingesting from Stripe API..."; \
		$(MAKE) ingest-all ENV=PROD SOURCE=api; \
	elif [ "$(INGEST_SOURCE)" = "json" ]; then \
		echo "📁 Ingesting from JSON directory: $(JSON_DIR)"; \
		$(MAKE) ingest-all ENV=PROD SOURCE=json JSON_DIR=$(JSON_DIR); \
	else \
		echo "❌ Please specify INGEST_SOURCE=api or json"; \
		exit 1; \
	fi

	@echo "💾 Dumping DB to JSON..."
	@$(MAKE) dump

	@echo "☁️ Uploading local dumps to GCS..."
	@$(MAKE) push_to_cloud

endif




# ========= HELP ==========

help: ## Affiche cette aide
	@echo "🔧 Utilisation : make <commande> [ENV=DEV|PROD]"
	@echo ""
	@echo "📘 Commandes disponibles :"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
