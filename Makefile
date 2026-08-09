# PayQuant (PQN) local build & test workflow
#
#   make build        build node+miner Docker images and the compose stack
#   make test         run ecosystem unit tests + compose validation
#   make mock-scale   validate scalable compose config (dry run)
#   make all          build + test
#   make clean        remove build output & stop containers

.PHONY: build node miner test mock-scale all clean up down

NODE_IMG := payquant-node:local
MINER_IMG := payquant-miner:local

build: node miner
	@echo ">> Building compose stack"
	docker compose build

node:
	@echo ">> Building $(NODE_IMG)"
	docker build -t $(NODE_IMG) -f Dockerfile.node .

miner:
	@echo ">> Building $(MINER_IMG)"
	docker build -t $(MINER_IMG) -f Dockerfile .

test:
	@echo ">> Running ecosystem test suite"
	python scripts/local_test_suite.py
	@echo ">> Validating docker-compose configuration"
	docker compose -f docker-compose.yml config --quiet
	docker compose -f docker-compose.yml -f docker-compose.publish.yml config --quiet
	@echo "ALL TESTS PASSED"

mock-scale:
	@echo ">> Scale config check (node=2, miner=2)"
	docker compose -f docker-compose.yml config --quiet
	@echo "Config OK for --scale node=2 --scale miner=2"

all: build test

up:
	docker compose -f docker-compose.yml -f docker-compose.publish.yml up -d

down:
	docker compose -f docker-compose.yml down

clean:
	docker compose down --volumes --remove-orphans 2>/dev/null || true
	rm -rf build build_dist release_dist