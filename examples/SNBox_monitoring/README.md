# Monitoring example

This folder contains some very naive boxes which are monitored throught
monitorong socket. There is a special `monitoring` box fetching data from
the monitoring socket. Note that in this example the `monitoring` box also
monitors itself - it pushes statistics to monitoring socket and pull from it
at the same time. For more details see [usage](../../usage.md).

To run the boxes:

```
poetry run ./monitoring.py --name monitoring --verbose \
	--resource in,bind,PULL,*,8803 \
	--resource mon,connect,PUSH,127.0.0.1,8803
```
```
poetry run ./drain.py --name drain --verbose \
	--resource in,bind,PULL,*,8802 \
	--resource mon,connect,PUSH,127.0.0.1,8803
```
```
poetry run ./box.py --name box --verbose \
	--resource in,bind,PULL,*,8801 \
	--resource out,connect,PUSH,127.0.0.1,8802 \
	--resource mon,connect,PUSH,127.0.0.1,8803
```
```
poetry run ./feeder.py --name feeder --verbose \
	--resource out,connect,PUSH,127.0.0.1,8801 \
	--resource mon,connect,PUSH,127.0.0.1,8803
```

To watch the logs:
```
tail -f sentinel.log
```


