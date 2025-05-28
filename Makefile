# Makefile

test:
	PYTHONPATH=$(pwd) pytest tests/ -v -s

reset-db:
	docker-compose down -v && docker-compose up -d
