# Git
Provides information about remote git repositories by command `git`.

## Configuration
```ini
[plugin.git]
<REPO_NAME> = <REPO_URL>
...
```

`<REPO_NAME>` is the command parameter to get information about git repository at url `<REPO_URL>`.

## Client setup
* `git` command line tool gets used internally, so [installation](https://git-scm.com/) is required
* Add SSH keys for access to protected repositories
