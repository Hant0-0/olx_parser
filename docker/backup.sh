#!/bin/bash

export TZ="Europe/Kiev"
BACKUP_DIR=/app/dumps/

DATA &(cat .env | xargs)

DATE=$(date +\%Y-\%m-\%d_\%H-\%M-\%S)

BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

export PG_PASSWORD=$POSTGRES_PASSWORD

pg_dump -U $POSTGRES_USER -h $POSTGRES_HOST -p $POSTGRES_PORT $POSTGRES_DB > $BACKUP_FILE 2>> $LOG_FILE

echo "Backup created: $BACKUP_FILE"