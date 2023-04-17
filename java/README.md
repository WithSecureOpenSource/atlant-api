# Using Atlant from Java

The [scanner](scanner) directory houses an example command-line client for
scanning files using WithSecure Atlant written in the Java programming language.

## Compilation

The client and its dependencies can be compiled into a single jar file using
[Gradle](https://gradle.org):

``` shell
cd java/scanner
./gradlew shadowJar
```

## Usage

The client can be invoked as:

``` shell
java -jar build/libs/scanner-all.jar AUTH-URL SCAN-URL CLIENT-ID CLIENT-SECRET FILE
```

Here `AUTH-URL` is Atlant authorization server address and `SCAN-URL` is a
scanning server address. See WithSecure Atlant user guide for information on how
to setup Atlant.

Note that the scanner is currently not compatible with Atlant container.
