#!/bin/sh

SESSION="snbenchmark"

# Kill old session if awaiable
if tmux ls | grep -q "$SESSION"; then
	tmux kill-session -t "$SESSION"
fi

# Start session
tmux new-session -d -s "$SESSION"
tmux new-window -t "$SESSION":0

tmux split-window -v -p 80
tmux select-pane -t 2
tmux split-window -v -p 66
tmux select-pane -t 3
tmux split-window -v -p 50

tmux select-pane -t 1
tmux split-window -h
#
## Run all necessary commands
tmux select-pane -t 0
tmux send-keys "tail -f sentinel.log" C-m
tmux select-pane -t 1
tmux send-keys "workon sentinel" C-m
tmux send-keys "./feeder.py --resource 'feeder,connect,PUSH,127.0.0.1,8801' -v" C-m
tmux select-pane -t 2
tmux send-keys "workon sentinel" C-m
tmux send-keys "./drain.py --resource 'drain,bind,PULL,*,8802' -v" C-m
tmux select-pane -t 3
tmux send-keys "workon sentinel" C-m
tmux send-keys "./box.py --resource 'in,bind,PULL,*,8801' --resource 'out,connect,PUSH,127.0.0.1,8802' --resource 'mon,connect,PUSH,127.0.0.1,8803' -v" C-m
tmux select-pane -t 4
tmux send-keys "workon sentinel" C-m
tmux send-keys "./monitoring.py --resource 'mon,bind,PULL,*,8803' -v" C-m

# Attach the session
tmux attach-session -t "$SESSION"

if [ "$1" = "keep" ]; then
	exit
fi

tmux kill-session -t "$SESSION"
