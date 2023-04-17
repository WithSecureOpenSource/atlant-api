# Atlant Client Library for Python

`atlant` is a Python module for interacting with WithSecure Atlant. It can be
used to scan files and manage Atlant instance's configuration. In addtion, the
module includes a command-line tool with similar functionality.

## Getting Started

The following steps can be used to install the module in a new virtual
environment.

```sh
# Create virtual environment for installing the module
python -m venv env
# Activate virtual environment
source env/bin/activate
# Install the module in editable mode
pip install -e .
```

## Using `atlant` Command-Line Tool

This section covers how to use the included `atlant` command-line tool. The
program contains multiple sub-commands for performing different tasks. Below is
a list of available sub-commands and their usage.

`atlant get-access-token [--scopes SCOPE...]`

`get-access-token` sub-command can be used to retrieve an OAuth access token
from Atlant. Using this command requires that Atlant has been configured to use
OAuth based authentication (this is always the case for non-container versions
of Atlant). Desired scopes for the access token can be specified using the
`--scopes` option.

`atlant config get [SETTING...]`
`atlant config set [SETTING...] VALUE`

`config get` and `config set` sub-commands can be used to get and set
configuration values, respectively. For the `config set` sub command, `VALUE`
should be specified in JSON format.

`atlant scan-file [--scan-archives BOOL] [--max-nested INT] [--max-scan-time INT] [--stop-on-first BOOL] [--allow-metadata-upstreaming BOOL] FILE`

`scan-file` sub-command can be used to scan files. `FILE` should be a path to
the file to be scanned, or `-` if content to be scanned should be read from
standard input.

Below is a description of the available options:

| Option | Description |
| --- | --- |
| `--scan-archives BOOL` | Controls if archives should be extracted during scanning. |
| `--max-nested INT` | If archive scanning is enabled, controls how many levels of nested archives to extract. |
| `--max-scan-time INT` | Sets time limit for scanning. |
| `--stop-on-first BOOL` | Controls if scanning should be stopped when the first mallicious file is found. |
| `--allow-metadata-upstreaming BOOL` | Controls if Atlant is allowed to upstream metadata about the file. |

`atlant scan-dir [--recursive] DIR`

`scan-dir` sub-command can be used to scan entire directories. If `--recursive`
if specifed files also within subdirectories are scanned.

`atlant classify-url URL`

`classify-url` sub-command can be used to classify URLs based on their content.

## Configuration

`atlant` command-line tool requires a configuration file to be present. The
configuration file specifies URLs for Atlant instance along with information
about the authentication method that should be used.

`atlant` tool looks for the configuration in the following locations:

1. `~/.atlant.ini`
2. `$XDG_CONFIG_HOME/atlant/atlant.ini`. If `XDG_CONFIG_HOME` is not set
   `~/.config` will be used as the default value.
3. `atlant/atlant.ini` inside each of the directories specified in
   `$XDG_CONFIG_DIRS` if it is set.
3. `/etc/xdg/atlant/atlant.ini`

Alternatively, configuration file path can be specified on the command-line
`--config` option.

## Configuration File Format

`atlant` command-line -ool uses an INI formatted configuration file. Below is an
example of what this configuration file can look like:

```ini
[atlant]
scanning_url = https://atlant.example.com:8080
management_url = https://atlant.example.com:8081

[authentication]
type = oauth
client_id = 6bca905ca4c1602a372e600c6f17d188
client_secret = 51ba319c3a979ac170c3895e796d5d380a06f51101bef2a400ad4170378d35c3
authorization_url = https://atlant.example.com:8082
```

The configuration file must contain an `atlant` section. The following options
can be specified in this section:

| Option | Description |
| --- | --- |
| `scanning_url` | Atlant's scanning service URL. **Required** |
| `management_url` | Atlant's management service URl. Required for `config` sub-command. This is not applicable to Atlant container. |
| `certificate_path` | Path to certificate bundle. |
| `log_level` | Log level. One of `critical`, `error`, `warning`, `info`, `debug`. |

If Atlant has been configured to use authentication, an `authentication` section
must be present. Depending on the mode of authentication that Atlant has been
configured to use, this section can take one of the two possible forms.

If Atlant has been configured to use OAuth based authentication (this is the
mode of authentication that is always used in the case of non-container versions
of Atlant), the following options can be specified in the `authentication`
section:

| Option | Description |
| --- | --- |
| `type` | Always `oauth` if OAuth authentication is used. **Required** |
| `client_id` | Client secret. **Required** |
| `client_secret` | Client secret. **Required** |
| `authorization_url` | Atlant's authorization service URL. **Required** |
| `audience` | Clients audience. One of `f-secure-atlant`, `policy-manager`. The value for this parameter depends on how the client was created. If the client was created with `atlantctl` utility. The value `f-secure-atlant` should be used. This is the default. If the client was created with Policy Manager Console, the value of `policy-manager` should be used. |

If Atlant has been configured to use API key based authentication (this
authentication method can currently only be used with Atlant container), the
following options can be specified in the `authentication` section:

| Option | Description |
| --- | --- |
| `type` | Always `api-key` if API key authentication is used. **Required** |
| `api_key` | API key used for authentication. **Required** |
