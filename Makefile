up:
	docker compose -f docker-compose.yml up -d --build

down:
	docker compose -f docker-compose.yml down

test:
	@echo "Tests are not configured yet"

lint:
	@echo "Lint is not configured yet"