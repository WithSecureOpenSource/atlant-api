# Using Atlant from Go

The [scanner](scanner) directory houses an example command-line client for
scanning files using WithSecure Atlant written in the Go programming language.

## Compilation

Use the following commands to compile `atlant-scanner`:

``` shell
cd go/scanner
go build
```

## Usage

`atlant-scanner` can be invoked as:

``` shell
atlant-scanner AUTH-URL SCAN-URL CLIENT-ID CLIENT-SECRET FILE
```

Note that `atlant-scanner` is currently not compatible with Atlant container.
