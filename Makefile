export PYTHONPATH := $(shell pwd)

## === ENV SETUP ===

dev-env:
	chmod +x scripts/dev_env.sh
	./scripts/dev_env.sh


## === INIT COMMANDS ===

init-all:
	make init-db
	make init-migration

init-db:
	docker-compose up -d
	@echo "⏳ Waiting for Postgres..."
	@sleep 3
	@until pg_isready -h localhost -p 5434 > /dev/null; do echo "⏳ Waiting for Postgres at localhost:5434..."; sleep 1; done
	@echo "✅ Postgres is ready!"
	@echo "🧱 Creating test database if needed"
	@docker exec -it stripe_db psql -U stripe_user -d postgres -c "CREATE DATABASE stripe_test;" || echo "✔️ stripe_test already exists."
	@echo "🧱 Initializing tables in both databases"
	@python scripts/init_db.py
	@echo "🔍 Verifying tables in 'stripe_db':"
	@docker exec -it stripe_db psql -U stripe_user -d stripe_db -c "\dt"
	@echo "✅ Tables verified in container for stripe_db"
	@echo "🔍 Verifying tables in 'stripe_test':"
	@docker exec -it stripe_db psql -U stripe_user -d stripe_test -c "\dt"
	@echo "✅ Tables verified in container for stripe_test"

init-migration:
	make dev-env
	@if [ ! -d alembic/versions ] || [ -z "$$(ls -A alembic/versions)" ]; then \
		echo "🧱 No migration found. Creating initial migration..."; \
		mkdir -p alembic/versions; \
		alembic revision --autogenerate -m "initial stripe schema"; \
		alembic upgrade head; \
	else \
		echo "✅ Migrations already exist. Skipping init-migration."; \
	fi

## === MIGRATION COMMANDS ===

migrate:
	make dev-env
	alembic revision --autogenerate -m "$(m)"
	alembic upgrade head

upgrade-db:
	make dev-env
	alembic upgrade head


## === RESET COMMANDS ===

reset-all:
	make reset-db
	make reset-migration

reset-db:
	docker-compose down -v
	make init-db

reset-migration:
	rm -rf alembic/versions/*
	mkdir -p alembic/versions
	make migrate m="reset migration"
