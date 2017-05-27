#!/usr/bin/env bash
ssserver -c shadowsocks.json -d start
python server.py