# Usage

There are 2 types of possible usage of this library:

1. `turris_sentinel_network.network.SN` class - raw usage
2. `turris_sentinel_network.msgloop.SNBox` class and it's non-abstract
implementations `SNGeneratorBox`, `SNPipelineBox`, `SNTerminationBox`
and `SNMultipleOutputPipelineBox`.

## Which one is the best for me?

### SNBox

`SNBox` provides safe implementation for straightforward box behavior like
`out-only`, `in-out` or `in-only` type of processing.

It handles all unexpected Exceptions from the box and tries to recover from this
types of error. Every box is restated by `systemd` but it could be slow and it
could unnecessarily drop messages from queues. `SNBox` safes every box from this
suffer.

It aims to be a programmer-friendly and provides naive and straightforward API.

Use `SNBox` for every box in pipeline.

### SN

On the other hand, `SN` provides only the basic gateway for common
configuration. All additional features are used independently.

Use `SN` for every box that is part of Sentinel Network but has non-trivial
requirements for communication pattern.


### Examples

`SNBox` is used across all pipeline boxes and almost all boxes of DynFW.

`SN` is used for `smash` (2 event loops can't work together) or DynFW
`publisher` (encryption at public socket).

# SNBox

Every box is implemented as a class that inherits from one of these non-abstract
`SNBox` implementations:

- `SNGeneratorBox` - `out-only` behavior - box generates messages from another
  source - e.g. feeders for DynFW
- `SNPipelineBox` - `in-out` behavior - box takes one message from network,
  makes some changes in message or adds some data and sends message to the next
  box - e.g. `geoip`
- `SNTerminationBox` - `in-only` behavior - box takes message from network and
  stores it into DB for example
- `SNMultipleOutputPipelineBox` - box is pretty similar to `SNPipelineBox` but
  is expected unlimited number of outgoing messages - e.g. DynFW
  `rules_collector`

## Usage

```python
from turris_sentinel_network.msgloop import SNPipelineBox

class MyBox(SNPipelineBox):
    def setup(self):
        return {
            "my_resource": init_my_resource(),
        }

    def teardown(self):
        self.ctx.my_resource.destroy()

    def process(self, msg_type, payload):
        if msg_type == "msg/i/should/care/about":
            payload["new_data"] = add_some_interesting_field()

            return msg_type, payload

MyBox().run()
```

### Setup

Optional. Box could allocate here some resources that will be needed. All
resources must be returned as a dictionary. Otherwise will be thrown
`SetupError` exception.

All resource initialized by `setup()` will be available in
`self.ctx.RESOURCE_NAME`.

Box should not use `self` for its data.

### Teardown

Optional. Box is able to make safe cleanup in this function. All resources are
available in `self.ctx.RESOURCE_NAME`.

### Process

Mandatory. Box obtains every message in 2 variables: `msg_type` (string with
message type identification - see Sentinel documentation for details) and
`payload` - Python dictionary containing the whole message.

`process` returns:
- `None` - there is no reasonable answer for message
- a `tuple` of `msg_type` and `payload` determines outgoing message

### Before first request

Optional. There is one more function:

```python
    def before_first_request(self):
        payload = get_some_data()  # Dictionary!

        return "sentinel/my/type", payload
```

This function is executed after full initialization of the box and before start
of the message loop itself. Returns `None` or tuple `(msg_type, payload)` as in
case of `process()`.

Currently, used only for DynFW `rules_collector`.


## Specialities

### `SNGeneratorBox`

`process` do not accept `msg_type` and `payload` and `process` must be a
generator - uses `yield` keyword.

### `SNTerminationBox`

Non-`None` return value is treated as a error.

### `SNMultipleOutputPipelineBox`

Return value is a `list` of tuples:

```python
        return [
            ("sentinel/type/one", payload1),
            ("sentinel/type/two", payload2),
        ]
```

The same behavior is expected in `before_first_request` function.

## Available resources

`self` provides some common resources for box:
- `self.name` - name of the box provided by CLI parameter
- `self.logger` - initialized and configured logger
- `self.args` - parsed command line arguments
- `self.ctx` - user data from `setup()` function

Box should not use any other `self` data.

## Monitoring

Each SNBox has implemented internal monitoring. It sends standard SN messages in regular intervals to monitoring socket if resource
called `mon` is defined. Otherwise it logs messages with `debug` severity through defined `self.logger`.

Each 5 seconds messsage with topic `sentinel/monitoring/heartbeat` with payload `{'box': 'box_name', 'id': 'box_id', 'ts': 1655112907}` is sent.

Each 10 seconds message with topic `sentinel/monitoring/stats` with payload `{'box': 'box_name', 'id': 'box_id', 'metrics': {'msg_recv': 12, 'msg_sent': 0}, 'ts': 1655112904}` is sent.

Where:
- `box` key contains name of the box passed to SNBox constructor
- `id` key contains content of environment variable `SENTINEL_ID` or box name in case the environment variable is not set.
- `ts` key contains time of message creation is seconds since epoch - Unix time
- `metrics` key contains nested dict where:
    - `msg_recv` key contains count of received messages since last monitoring message with topic `sentinel/monitoring/stats` was sent
    - `msg_sent` key contains count of sent messages since last monitoring message with topic `sentinel/monitoring/stats` was sent

For example of monitoring setup see `examples/SNBox_monitoring` directory.

## Examples

Basic examples are provided in `examples/` directory.


# SN

```python
from turris_snetinel_network.network import SN
from turris_sentinel_network.messages import encode_msg, parse_msg

def main():
    ctx = SN(zmq.Context.instance())

    socket_in, socket_out = ctx.get_socket("in", "out")

    while True:
        msg = socket_in.recv_multipart()
        msg_type, payload = parse_msg(msg)

        payload["new_data"] = add_some_interesting_field()

        msg = encode_msg(msg_type, payload)
        socket_out.send_multipart(msg)


if __name__ == "__main__":
    main()
```

This example says it all. Nothing more is provided.


## `get_socket`

Socket (or resource in internal terminology) could be requested as:
```python
socket_in, socket_out = ctx.get_socket("in", "out")
```

or:

```python
socket_in = ctx.get_socket("in")
socket_out = ctx.get_socket("out")
```

for simple resource gathering.

There is an option to force socket type:

```python
socket_in = ctx.get_socket(("in", "PULL"))
```

## Logging

There are 2 preconfigured handlers:
- syslog - INFO and higher severity
- file under rotation - DEBUG and higher severity

Expected usage in `SN` script:

```python
import logging
import turris_sentinel_network
logger = logging.getLogger("component_name")
logger.info("I'm running!")
```

In `SNBox` is everything prepared in `self.logger`.

Your logger will inherit INFO level from root logger.

There is shared command line argument `-v` or `--verbose` that turns on DEBUG
level for file handler.

Please, do not change logging format for syslog handler. It will be parsed by
TM. File handler is prefixed by current time, for better debugging.

# Argument parser

Some scripts/boxes may need additional arguments.

Use this approach:
1. Get common SN argparser
2. Add needed arguments

```python

from turris_sentinel_network.argparser import get_arg_parser

def my_argparser():
    parser = get_arg_parser()
    parser.add_argument('--my-cool-feature',
                        action='store_true',
                        help='Enable my cool feature'
                       )

    return parser
```

3. Add new enriched argparser to `SN`/`SNBox`

```python
ctx = SN(zmq.Context.instance(), argparser=my_argparser())
```

or

```python
MyBox(argparser=my_argparser()).run()
```

4. Get parsed arguments as:

```python
ctx.args.ARGUMENT_NAME
```

or

```python
self.args.ARGUMENT_NAME
```
