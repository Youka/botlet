# Based on debian with python3 just-in-time compiler
# <https://hub.docker.com/_/pypy/>
FROM pypy:3

# Install application
WORKDIR /usr/src/app
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get install git

# Configure container interfaces
EXPOSE 80/tcp
STOPSIGNAL SIGINT

# Run application
ENTRYPOINT [ "pypy3", "-m", "botlet" ]