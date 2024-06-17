.PHONY: all
all:
	# @git clone https://github.com/spiceai/spiceai.git || true
	@docker compose build
	@docker compose up -d

.PHONY: clean
clean:
	@docker compose down
	@docker volume prune -f
	@docker image prune -f