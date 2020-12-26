@echo off

:: Call botlet with local configuration + logging properties, extend environment by invalid discord credentials and ignore stdout stream
botlet -c "%~dp0config.ini" -l "%~dp0logging.ini" -e DISCORD_TOKEN fake_token -e DISCORD_CHANNEL_ID -1 1>NUL