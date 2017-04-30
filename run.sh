#!/usr/bin/env sh

redis-cli flushall
sudo rm data/*
sudo python src/bot.py
