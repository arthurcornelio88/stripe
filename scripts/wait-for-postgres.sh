#!/bin/bash
set -e

HOST="${POSTGRES_HOST:-localhost}"
PORT="${POSTGRES_PORT:-5434}"

echo "⏳ Waiting for Postgres at $HOST:$PORT..."
until pg_isready -h "$HOST" -p "$PORT" > /dev/null 2>&1; do
  sleep 1
done

echo "✅ Postgres is ready!"
