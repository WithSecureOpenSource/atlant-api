# F-Secure Atlant API Examples

This repository contains examples for interacting with F-Secure Atlant API.
F-Secure Atlant is a platform for building applications that are able to scan
and detect malicious files.

Atlant provides a REST API for scanning files and managing the product
configuration. Applications and services can use the API resources to analyze
content using always up-to-date heuristics and statistical techniques.

## Python Examples

Python examples are available in `python` directory. The directory contains a
Python package that provides a number of utilities that demonstrate how the
F-Secure Atlant APIs can be used to configure the product and scan files. The
included example utilities are:

- `atlant-token`: Tool for fetching access tokens from F-Secure Atlant's
  internal authorization server
- `atlant-get`: Tool for getting setting values using configuration API
- `atlant-set`: Tool for changing setting values using configuration API
- `atlant-scan`: Tool for scanning files using scanning API
- `atlant-web`: Example web app for scanning files
- `atlant-icap`: Tool for using the ICAP interface
- `atlant-dirscan`: Tool for scanning directories for harmful content

### Running the Python Examples

On a typical Linux system, the simplest way to try out the example utilities is
to install them in a [virtual environment](https://docs.python.org/3/library/venv.html).

This can be achieved by running the following commands in project's root
directory:

``` shell
python3 -m venv env
source env/bin/activate
cd python
./setup.py develop
```

Now the example utilities should be available in current shell's path.

#### Scanning Directories with atlant-dirscan

`atlant-dirscan` Utility can be used for scanning directories for harmful
content. Scan results are written to a CSV file.

```
usage: atlant-dirscan [-h] config dir output

Scan directory for harmful files.

positional arguments:
  config      Configuration file path.
  dir         Directory to scan.
  output      Output file path.

optional arguments:
  -h, --help  show this help message and exit
```

`atlant-dirscan` requires that a path to a configuration file is supplied on the
command line. The configuration file should have the following format:

```
{
    "authorization_address": "authorization.example.com:8081",
    "scanner_address": "scanner.example.com:8082",
    "client_id": "...",
    "client_secret": "...",
    "security_cloud": false,
    "allow_upstream_application_files": true,
    "allow_upstream_data_files": false
}
```

## Java Examples

In `java/scanner`, there is an example command line based file scanning client
written in Java 11. The client along with its dependencies can be built into a
single JAR-file using [Gradle](https://gradle.org):

``` shell
cd java/scanner
./gradlew shadowJar
```

The client can be invoked as:

``` shell
java -jar build/libs/scanner-all.jar AUTH-URL SCAN-URL CLIENT-ID CLIENT-SECRET FILE
```

Here `AUTH-URL` is Atlant authorization server address and `SCAN-URL` is a
scanning server address. See F-Secure Atlant user guide for information on how
to setup Atlant.

## Go Examples

In `go/scanner`, there is an example Go command line client capable of scanning
files using F-Secure Atlant file scanning API. The client can be built with:

``` shell
cd go/scanner
go build
```

The client can be invoked as:

``` shell
atlant-scanner AUTH-URL SCAN-URL CLIENT-ID CLIENT-SECRET FILE
```


## JavaScript Examples

In `javascript/scanner`, there is an example command line based file scanning
client build on top of Node.js. The client can be invoked as:

``` shell
atlant-scanner AUTH-URL SCAN-URL CLIENT-ID CLIENT-SECRET FILE
```

