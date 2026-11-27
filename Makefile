
up:
	docker compose -f docker-compose.yml up -d --build

down:
	docker compose -f docker-compose.yml down

migrate:
	docker compose -f docker-compose.yml exec -T db psql -U digest_user -d gaming_digest < database/migrations/002_postgresql_schema.sql
	docker compose -f docker-compose.yml exec -T db psql -U digest_user -d gaming_digest < database/migrations/003_seed_demo_data.sql

test:
	@echo "Tests are not configured yet"

lint:
	@echo "Lint is not configured yet"