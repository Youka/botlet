# Heartbeat
Publishes one **status event** in configured interval.

## Configuration

```ini
[plugin.heartbeat]
inverval = <INTERVAL>
message = <MESSAGE>
```

`<INTERVAL>` is the number of seconds between each published event.  
`<MESSAGE>` is the text of published events.
