# SN examples

This folder contains example of `SN` class usage. It provides only basic
functionalities. For more details see [usage](../../usage.md).

To run example implementation run:
```
poetry run ./server.py --name server --verbose \
	--resource sock_srv,bind,REP,*,9000
```
```
poetry run ./client.py --name client --verbose \
	--resource sock_cli,connect,REQ,127.0.0.1,9000
```

```
poetry run ./server.py --name server1 --verbose \
	--resource sock_srv,bind,REP,*,9001
```
```
poetry run ./client.py --name client1 --verbose --disable-ipv6 \
	--resource sock_cli,connect,REQ,127.0.0.1,9001
```

```
poetry run ./client2.py --name client2 --verbose --client-id 4242 \
	--resource sock_cli,connect,REQ,127.0.0.1,9000 \
	--resource sock_cli2,connect,REQ,127.0.0.1,9001
```


To watch the logs:
```
tail -f sentinel.log
```
