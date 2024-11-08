.PHONY: all
all:
	@docker compose up -d

.PHONY: clean
clean:
	@docker compose down -v
	rm -r .spice || true
	rm -r certs || true

.PHONY: register-connector
register-connector:
	@curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @../register-connector.json
