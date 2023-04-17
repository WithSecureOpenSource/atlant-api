# WithSecure Atlant Integration Guide

This repository contains tutorials and examples that demonstrate how to
seamlessly integrate with WithSecure Atlant. Atlant is a powerful self-hosted
service designed to scan files for malicious content, detect spam, and classify
URLs. With Atlant, you can access these capabilities through a simple and
intuitive REST API or integrate with existing ICAP-based solutions.

Whether you're new to Atlant or an experienced user, this repository provides
comprehensive guidance on how to make the most of its features. Our tutorials
and examples are designed to be easy to follow, with clear instructions and
practical examples that you can adapt to your needs.

## Getting Started with Atlant Using cURL

[This tutorial](curl/README.md) explains how to get started with Atlant using
cURL. It shows how to install and configure Atlant and how to perform common
scanning tasks using the command-line `curl` utility.

## Getting Started with Atlant Using Python

[Python directory](python) houses a collection of Python libraries and
applications that showcase using Atlant's diverse capabilities from Python.

The [`atlant`](python/atlant) module provides a client library for interacting
with Atlant's REST API. The library enables Python code to scan files and other
types of content using Atlant, and also offers configuration management
capabilities. In addition to the library, the module includes a command-line
tool with the same name and similar functionality. See [module-level
documentation](python/atlant/README.md) for more information about the library
and the associated command-line tool.

The [`asyncio-icap-client`](python/asyncio-icap-client) module is a
general-purpose ICAP client library for Python built on top of
[`asyncio`](https://docs.python.org/3/library/asyncio.html). This module is not
tied to Atlant, but can be used for interacting with any ICAP server.

The [`demo-web-app`](python/demo-web-app) directory contains a sample web
application that internally employs Atlant to scan files. The application is
distributed as a set of containers that can be easily deployed using [Docker
compose](https://docs.docker.com/compose/).

## Examples in Other Languages

While the Python libraries and tools are the most comprehensive ones, we have
also included additional examples in other languages for demonstration purposes:

- [Examples in Java](java)
- [Examples in JavaScript](javascript)
- [Examples in Go](go)
