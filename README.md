# QueryGuard - *A guard against unruly sql*

![Logo](https://raw.githubusercontent.com/dataNdeadlifts/QueryGuard/beta/docs/images/logo.jpg)

[![Test](https://github.com/dataNdeadlifts/QueryGuard/actions/workflows/test.yml/badge.svg)](https://github.com/dataNdeadlifts/QueryGuard/actions/workflows/test.yml)
[![codecov](https://codecov.io/github/dataNdeadlifts/QueryGuard/graph/badge.svg?token=3TL6N3BMM4)](https://codecov.io/github/dataNdeadlifts/QueryGuard)
![PyPI - Version](https://img.shields.io/pypi/v/QueryGuard)

---

**Documentation**: [http://queryguard.readthedocs.io/](http://queryguard.readthedocs.io/)

**Source Code**: [https://github.com/dataNdeadlifts/QueryGuard](https://github.com/dataNdeadlifts/QueryGuard)

---

QueryGuard is a command line tool for analyzing SQL queries for best practices
and adherance to security policies.

It functions very similarly to static analysis tools for other programing languages
such as flake8, ruff, and ESLint but for your database queries.

## Requirements

Python 3.9+

## Installation

```console
pip install QueryGuard
```

## Example

### Check all sql files in a folder

![Simple Violation](https://raw.githubusercontent.com/dataNdeadlifts/QueryGuard/beta/docs/images/simple_violation.png)

### Ignore a specific rule

![Ignore Violation](https://raw.githubusercontent.com/dataNdeadlifts/QueryGuard/beta/docs/images/ignore_violation.png)

## License

This project is licensed under the terms of the Apache 2.0 license.
