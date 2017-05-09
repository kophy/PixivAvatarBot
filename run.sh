#!/usr/bin/env sh

redis-cli flushall
rm data/*
mkdir data
python src/bot.py
