# Overview

## Description

QueryGuard analyzes sql queries for adherance to best practices and security policies.

## Use Cases

- During development to help adhere to common best practices.
- During CI/CD to enforce security or best practice policies.

## Install

Python version 3.9+ is required. It can then be installed using pip.

```bash
pip install QueryGuard
```

## Getting Started

QueryGuard functions very similarly to common static analysis (i.e. linting) tools
 for other programming languages such as flake8, ruff, eslint but for database queries.
 You point it to a file or folder containing sql queries and it will evaluate
 each file against a set of rules.

You can run the tool using it's full name queryguard or qg as a shorthand alias.

![Simple Violation](images/simple_violation.png)

For more detailed usage see the getting started guide.

## Development Status

QueryGuard is currently considered in beta. It should be functional and
reliable but there are likely to be frequent breaking changes to the public schema.
