@echo off

:: Create & run temporary docker container with injected configuration and extend environment by invalid slack credentials
docker run -it --rm -v "%~dp0config.ini":/usr/src/app/botlet/config/config.ini -e "BOTLET_DOCKER_SLACK_TOKEN=fake_token" -e "BOTLET_DOCKER_SLACK_CHANNEL_ID=xxx" --name botlet-example botlet