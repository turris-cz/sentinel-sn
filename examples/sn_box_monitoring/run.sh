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
tmux send-keys "./feeder.py --name 'feeder' --resource 'out,connect,PUSH,127.0.0.1,8801' --resource 'mon,connect,PUSH,127.0.0.1,8803' -v" C-m
tmux select-pane -t 2
tmux send-keys "workon sentinel" C-m
tmux send-keys "./drain.py --name 'drain' --resource 'in,bind,PULL,*,8802' --resource 'mon,connect,PUSH,127.0.0.1,8803' -v" C-m
tmux select-pane -t 3
tmux send-keys "workon sentinel" C-m
tmux send-keys "./box.py --name 'box' --resource 'in,bind,PULL,*,8801' --resource 'out,connect,PUSH,127.0.0.1,8802' --resource 'mon,connect,PUSH,127.0.0.1,8803' -v" C-m
tmux select-pane -t 4
tmux send-keys "workon sentinel" C-m
# the box is monitoring itself
tmux send-keys "./monitoring.py --name 'monitoring' --resource 'in,bind,PULL,*,8803' --resource 'mon,connect,PUSH,127.0.0.1,8803' -v" C-m

# Attach the session
tmux attach-session -t "$SESSION"

if [ "$1" = "keep" ]; then
	exit
fi

tmux kill-session -t "$SESSION"
