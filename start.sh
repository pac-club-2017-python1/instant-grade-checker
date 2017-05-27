#!/usr/bin/env bash
shadowsocks -c shadowsocks.json -d start
python server.py