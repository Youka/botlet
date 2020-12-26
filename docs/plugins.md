# Plugins
Bot functionality depends on internal plugins which activate and behave by configuration files and environment variables.

These plugins are available:

* [Logging](./logging.md)
* [Heartbeat](./heartbeat.md)
* [Discord](./discord.md)
* [Slack](./slack.md)
* [Git](./git.md)
* [Anime birthdays](./anime_birthdays.md)

## Commands
Some plugins offer commands input, f.e. by chat messages starting with `$`. Command `help` requests usage information from compatible plugins.

## Development
New plugins are easy to develop:
* In module `botlet.plugins`:
  * Choose an `Abstract*Plugin` class to inherit from later
  * _(Optional)_ Add `*EventData` classes to transport information of your plugin to others
* Create or edit module `botlet.plugins.<PLUGIN_CATEGORY>`:
  * Create your plugin class `<PLUGIN_NAME>Plugin` and inherit from chosen `Abstract*Plugin`
    * Implement `__init__` for initialization (calling `super`)
    * _(Optional)_ Implement `close` for cleanup (calling `super`)
    * Implement `apply_event` to process incoming events
    * Use `_publish_event_data` to publish events to other plugins
    * _(On threaded plugin)_ Care for `_stopped` flag to suspend infinite loops
  * Register your plugin by function `register_plugins(workers: List[AbstractPlugin], publish_event: Callable[[Event], None], config: Dict[str,Dict[str,str]], _env: Dict[str, str])`
    * Use incoming configuration, environment and event publish callback to create an instance
    * Add this instance to event processing workers

Don't neglect to write documentation and tests (maybe an example too).  
Simple implementations to learn are plugin **LoggingPlugin** for events input and **HeartbeatPlugin** for events output.
