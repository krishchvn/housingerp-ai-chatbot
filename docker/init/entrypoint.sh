#!/bin/bash
# Starts SQL Server, waits until ready, then runs init SQL scripts.
# This runs automatically on first container start.

set -e

SA_PASSWORD="${SA_PASSWORD:-HousingERP@123}"
INIT_DIR="/docker-entrypoint-initdb"

echo "Starting SQL Server..."
/opt/mssql/bin/sqlservr &
SQL_PID=$!

echo "Waiting for SQL Server to be ready..."
for i in $(seq 1 30); do
    /opt/mssql-tools18/bin/sqlcmd \
        -S localhost -U sa -P "$SA_PASSWORD" \
        -Q "SELECT 1" \
        -C -l 1 > /dev/null 2>&1 && break
    echo "  Attempt $i/30 — not ready yet, waiting 2s..."
    sleep 2
done

echo "SQL Server is ready. Running init scripts..."

for f in $(ls "$INIT_DIR"/*.sql | sort); do
    echo "  Running $f..."
    /opt/mssql-tools18/bin/sqlcmd \
        -S localhost -U sa -P "$SA_PASSWORD" \
        -i "$f" -C
done

echo "All init scripts complete."

# Keep SQL Server running
wait $SQL_PID
