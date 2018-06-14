# SN - Sentinel networking library

This package implements a bunch of features that are common for all Sentinel
boxes:

- ZMQ networking
- Common configuration framework
- Logging in standardized way (necessary to handle log messages by TM - Turris
  Monitoring)
- Message queue for handling messages in safe and good-performing way

## Usage

There are 2 types of possible usage of this library:

1. `sn.SN` class - raw usage
2. `SNBox` class and it's non-abstract implementations `SNGeneratorBox`,
   `SNPipelineBox`, `SNTerminationBox` and `SNMultipleOutputPipelineBox`

### Which one is the best for me?

#### SNBox

`SNBox` provides safe implementation for straightforward box behavior like
`out-only`, `in-out` or `in-only` type of processing.

It handles all unexpected Exceptions from the box and tries to recover from this
types of error. Every box is restated by `systemd` but it could be slow and it
could unnecessarily drop messages from queues. `SNBox` safes every box from this
suffer.

It aims to be a programmer-friendly and provides naive and straightforward API.

Use `SNBox` for every box in pipeline.

#### sn.SN

On the other hand, `sn.SN` provides only the basic gateway for common
configuration. All additional features are used independently.

Use `sn.SN` for every box that is part of Sentinel Network but has non-trivial
requirements for communication pattern.


#### Examples

`SNBox` is used across all pipeline boxes and almost all boxes of DynFW.

`sn.SN` is used for `smash` (2 event loops can't work together) or DynFW
`publisher` (encryption at public socket).

## SNBox

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

### Usage

```python
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

if __name__ == "__main__":
    MyBox("by_box_name").run()
```

#### Setup

Optional. Box could allocate here some resources that will be needed. All
resources must be returned as a dictionary. Otherwise will be thrown
`SetupError` exception.

All resource initialized by `setup()` will be available in
`self.ctx.RESOURCE_NAME`.

Box should not use `self` for its data.

#### Teardown

Optional. Box is able to make safe cleanup in this function. All resources are
available in `self.ctx.RESOURCE_NAME`.

#### Process

Mandatory. Box obtains every message in 2 variables: `msg_type` (string with
message type identification - see Sentinel documentation for details) and
`payload` - Python dictionary containing the whole message.

`process` returns:
- `None` - there is no reasonable answer for message
- a `tuple` of `msg_type` and `payload` determines outgoing message

#### Before first request

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


#### Specialities

##### `SNGeneratorBox`

`process` do not accept `msg_type` and `payload` and `process` must be a
generator - uses `yield` keyword.

##### `SNTerminationBox`

Non-`None` return value is treated as a error.

##### `SNMultipleOutputPipelineBox`

Return value is a `list` of tuples:

```python
        return [
            ("sentinel/type/one", payload1),
            ("sentinel/type/two", payload2),
        ]
```

The same behavior is expected in `before_first_request` function.

#### Available resources

`self` provides some common resources for box:
- `self.name` - name of the box provided to the constructor
- `self.logger` - initialized and configured logger
- `self.args` - parsed command line arguments
- `self.ctx` - user data from `setup()` function

Box should not use any other `self` data.

#### Examples

Basic examples are provided in `dev/` directory.

## sn.SN

```python
def main():
    ctx = sn.SN(zmq.Context.instance())

    socket_in, socket_out = ctx.get_socket("in", "out")

    while True:
        msg = socket_in.recv_multipart()
        msg_type, payload = sn.parse_msg(msg)

        payload["new_data"] = add_some_interesting_field()

        msg = sn.encode_msg(msg_type, payload)
        socket_out.send_multipart(msg)


if __name__ == "__main__":
    main()
```

This example says it all. Nothing more is provided.


### `get_socket`

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

Expected usage in `sn.SN` script:

```python
import logging
import sn
logger = logging.getLogger("component_name")
logger.info("I'm running!")
```

In `SNBox` is everything prepared in `self.logger`.

Your logger will inherit INFO level from root logger.

There is shared command line argument `-v` or `--verbose` that turns on DEBUG
level for file handler.

Please, do not change logging format for syslog handler. It will be parsed by
TM. File handler is prefixed by current time, for better debugging.

## Argument parser

Some scripts may need additional arguments.

Use this approach:
1. Get common SN argparser
2. Add needed arguments

```python

import sn

def my_argparser():
    parser = sn.get_arg_parser()
    parser.add_argument('--my-cool-feature',
                        action='store_true',
                        help='Enable by cool feature'
                       )

    return parser

```
3. Add new enriched argparser to `sn.SN`/`SNBox`

```python
ctx = sn.SN(zmq.Context.instance(), argparser=my_argparser())
```

or

```python
MyBox("by_box_name", argparser=my_argparser()).run()
```
4. Get parsed arguments as:
```python
ctx.args.ARGUMENT_NAME
```

or

```python
self.args.ARGUMENT_NAME
```
