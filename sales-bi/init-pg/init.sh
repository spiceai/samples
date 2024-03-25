#!/bin/bash

# Wait for PostgreSQL to start
until psql -c '\l'; do
  echo "Waiting for PostgreSQL to start..."
  sleep 1
done

psql -f /docker-entrypoint-initdb.d/cleaned_sales_data.sql