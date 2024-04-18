# Define the default make action
.PHONY: all
all: build_books_list_fetcher build_books_details_fetcher up

# Build the Docker image for books_list_fetcher
.PHONY: build_books_list_fetcher
build_books_list_fetcher:
	docker build -t books_list_fetcher_image ./books_list_fetcher

# Build the Docker image for books_details_fetcher
.PHONY: build_books_details_fetcher
build_books_details_fetcher:
	docker build -t books_details_fetcher_image ./books_details_fetcher

# Start the services defined in the docker-compose.yml file
.PHONY: up
up:
	docker compose up -d --force-recreate

# Stop and remove the containers defined in the docker-compose.yml file
.PHONY: down
down:
	docker compose down
