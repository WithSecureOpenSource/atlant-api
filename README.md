# F-Secure Atlant API Examples

## Python Examples

Python examples are available in `python` directory. The directory contains a
python package that provides a number of utilities that demonstrate how the
various F-Secure Atlant APIs can be used to configure the product and scan
files. The included example utilities are:

- `atlant-token`: Tool for fetching access tokens from F-Secure Atlant's
  internal authorization server.
- `atlant-get`: Tool for getting setting values using configuration API.
- `atlant-set`: Tool for changing setting values using configuration API.
- `atlant-scan`: Tool for scanning files using scanning API.

### Running the Python Examples

On a typical Linux system, the simplest way to try out the example utilities is
to install them in a [virtual environment](https://docs.python.org/3/library/venv.html).

This can be achieved by running them the following commands in project's root
directory:

``` shell
python3 -m venv env
source env/bin/activate
cd python
./setup.py develop
```

Now the commands should be available in the current shell's path.

## Go Examples

In `go/scanner`, there is an example Go command line client capable of scanning
files using F-Secure Atlant's scanning API. To compile the client, simply run:

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
utility build on top of Node.js.
