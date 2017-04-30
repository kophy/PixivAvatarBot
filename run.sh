#!/usr/bin/env sh

redis-cli flushall
rm data/*
python src/bot.py
