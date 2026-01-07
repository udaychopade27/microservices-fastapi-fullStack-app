#!/usr/bin/env bash

# List of compose files
COMPOSE_FILES="-f docker-compose.yml \
  -f docker-compose-frontend.yml \
  -f docker-compose-db.yml \
  -f docker-compose-services.yml \
  -f docker-compose-dev.yml"

# Wrapper for docker compose
dc() {
  docker-compose $COMPOSE_FILES "$@"
}

usage() {
  echo "Usage: $0 {build-nocache|build|up|restart}"
  exit 1
}

run_action() {
  case "$1" in
    build-nocache)
      echo "Running build --no-cache..."
      dc build --no-cache
      ;;
    build)
      echo "Running build with cache..."
      dc build
      ;;
    up)
      echo "Running up -d..."
      dc up -d
      ;;
    restart)
      echo "Restarting services..."
      dc restart
      ;;
    down)
      echo "Removing services...."
      dc down
      ;;
    *)
      usage
      ;;
  esac
}

# 1) If arg is passed: non-interactive
if [ -n "$1" ]; then
  run_action "$1"
  exit $?
fi

# 2) Interactive menu
echo "Select action:"
echo "1) build-nocache (build --no-cache)"
echo "2) build (with cache)"
echo "3) up (up -d)"
echo "4) restart"
echo "5) down"
read -rp "Enter choice [1-5]: " choice

case "$choice" in
  1) action="build-nocache" ;;
  2) action="build" ;;
  3) action="up" ;;
  4) action="restart" ;;
  5) action="down";;
  *) echo "Invalid choice"; exit 1 ;;
esac

run_action "$action"
