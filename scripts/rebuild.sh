#!/bin/bash

# Define the image tag you're interested in
IMAGE_TAG="top-reactions-bot"

# Find the container ID using the image tag, if there's exactly one running instance
CONTAINER_ID=$(docker ps --filter "ancestor=$IMAGE_TAG" --format "{{.ID}}")

# Function to stop and remove Docker container
function stop_and_remove_container {
    if [ ! -z "$CONTAINER_ID" ]; then
        echo "Stopping container: $CONTAINER_ID"
        docker stop $CONTAINER_ID
        echo "Removing container: $CONTAINER_ID"
        docker rm $CONTAINER_ID
    else
        echo "No running container found for image tag $IMAGE_TAG"
    fi
}

# Function to build Docker image
function build_image {
    echo "Building Docker image: $IMAGE_TAG"
    docker build -t $IMAGE_TAG .
}

# Function to run Docker container
function run_container {
    echo "Running Docker container: $IMAGE_TAG"
    docker run -d --env-file .env --restart unless-stopped $IMAGE_TAG
}

# Execute the functions
stop_and_remove_container
build_image
run_container

echo "Update complete."
