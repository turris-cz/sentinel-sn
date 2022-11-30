# SNBox examples

This folder contains examples of non-abstract implementations of `SNBox` - 
`SNGeneratorBox`, `SNPipelineBox`, `SNTerminationBox` and
`SNMultipleOutputPipelineBox`. These are the most abstract boxes doing a lot
of stuff in the background and needing only core functionality - the message
processing to be implemented. For more details see [usage](../../usage.md).

To run the boxes in your terminals:
```
poetry run ./in_only.py --name in_only --verbose \
	--resource in,bind,PULL,*,8803
```
```
poetry run ./in_multiple_out.py --name in_multiple_out --verbose \
	--resource in,bind,PULL,*,8802 \
	--resource out,connect,PUSH,localhost,8803
```
```
poetry run ./in_out.py --name in_out --verbose \
	--resource in,bind,PULL,*,8801 \
	--resource out,connect,PUSH,localhost,8802
```
```
poetry run ./out_only.py --name out_only --verbose \
	--resource out,connect,PUSH,localhost,8801

```

To watch the logs:
```
tail -f sentinel.log
```
