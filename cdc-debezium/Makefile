.PHONY: all
all:
	@docker compose up -d

.PHONY: clean
clean:
	@docker compose down
	@docker volume prune -f
	@docker image prune -f

.PHONY: register-connector
register-connector:
	@curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @register-connector.json
