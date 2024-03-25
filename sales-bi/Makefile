all:
	@docker compose build
	@docker compose up -d

	@until nc -z localhost 8088; do sleep 1; done

	@echo "Initializing Superset..."
	@./superset/init/init.sh > /dev/null

	@echo ""
	@echo "Superset is running at http://localhost:8088, login with admin/admin"

clean:
	@docker compose down
	@docker volume prune -f
	@docker image prune -f