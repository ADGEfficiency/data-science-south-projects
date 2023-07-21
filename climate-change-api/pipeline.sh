#!/usr/bin/env bash
python src/download.py
sqlite3 data/database.db < schema.sql
python src/process.py
