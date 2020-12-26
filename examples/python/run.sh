#!/bin/sh

# Call botlet with local configuration + logging properties, extend environment by invalid discord credentials and ignore stdout stream
botlet -c "$(dirname $0)/config.ini" -l "$(dirname $0)/logging.ini" -e DISCORD_TOKEN fake_token -e DISCORD_CHANNEL_ID -1 1>/dev/null