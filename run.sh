#!/usr/bin/env sh

redis-cli flushall
mkdir data
sudo rm data/*
sudo python src/bot.py
