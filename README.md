# Botlet
Communication and commands bot.

## Requirements
* [Python >=3.7](https://www.python.org/) as code interpreter for all important tasks
* _(Optional)_ [git](https://git-scm.com/) for `git` plugin
* _(Optional)_ [Docker](https://www.docker.com/) for container building & running

## Usage

### Preparation
* Use **virtual environment**:
  * Install: `python -m venv .venv`
  * Activate (_Windows_): `.venv\Scripts\activate.bat`
  * Activate (_Linux_): `source .venv/bin/activate`
* Install **dependencies**: `pip install -r requirements.txt -r requirements-dev.txt`

### Code quality
* Run **code linting**: `pylint botlet`
* Run **unit tests**: `coverage run`
* Report **test coverage**: `coverage report`  
  _(For other output formats, replace `report` by `html`|`json`|`xml`)_

### Deploy
* Show **code documentation**: `pdoc -o html/ botlet`
* Manage **distribution**:
  * Source archive: `python setup.py sdist`
  * Install locally: `pip install .`

### Run
* Start **application**:
  * From source: `python -m botlet`
  * From installation: `botlet`
* Create **docker container**:
  * Build image: `docker build -t botlet .`
  * Run container: `docker run -it --name botlet-lives botlet`  
    _(Containers can run with customized [environment variables](https://docs.docker.com/engine/reference/run/#env-environment-variables) and [configuration files in volumes](https://docs.docker.com/engine/reference/run/#volume-shared-filesystems))_

## Configuration
* Call command line with `-h` for a help text
* See configuration file formats in `botlet.config` package (_config.ini_ & _logging.ini_)
* Environment variables serve as parameters (f.e. secrets for server access)

For more, see [plugins](./docs/plugins.md).

## IDE support
* [VSCode](https://code.visualstudio.com/) with plugins:
  * [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
  * [EditorConfig for VS Code](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)
  * [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
* [PyCharm](https://www.jetbrains.com/pycharm/)

## Contributing
You can help with bug reports or feature ideas by opening issues.  
Code contributions should be submitted as merge requests.  
Please keep the quality up by checking your changes, using mentioned tools and following conventions.

## TODO

### Features
* IO by http/rest (alternative to chat)
* Webhook listener ([HTTP server](https://docs.python.org/3/library/http.server.html#http.server.ThreadingHTTPServer)):
  * [Gitlab](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html#webhook-endpoint-tips)
  * [Jenkins](https://plugins.jenkins.io/outbound-webhook/)

### Infrastructure
* Gitlab CI
