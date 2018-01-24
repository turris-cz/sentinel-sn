#!/bin/bash
xterm -geometry 93x20+100+200 -hold -e ./client.py  \
	--resource "sock_cli,connect,REQ,127.0.0.1,9000" \
	--resource "sock_cli,connect,REQ,127.0.0.1,9001" &
#xterm -geometry 93x20+100+500 -hold -e ./client2.py "sock_cli,connect,REQ,127.0.0.1,9000" "sock_cli2,connect,REQ,127.0.0.1,9000" &
xterm -geometry 93x20+100+800 -hold -e ./client.py  \
	--resource "sock_cli,connect,REQ,127.0.0.1,9000" &


xterm -geometry 93x31+650+200 -hold -e ./server.py \
	--resource "sock_srv,bind,REP,*,9000" &
xterm -geometry 93x31+1200+200 -hold -e ./server.py \
	--resource "sock_srv,bind,REP,*,9001" &


