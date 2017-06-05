#!/usr/bin/env bash
sudo fuser 5000/tcp -k
python server.py
