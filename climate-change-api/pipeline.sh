#!/usr/bin/env bash
sqlite3 data/database.db < schema.sql
python src/download.py
python src/process.py
