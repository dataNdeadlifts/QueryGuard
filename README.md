

---

**Documentation**:

**Source Code**: <a href="https://github.com/dataNdeadlifts/QueryGuard" target="_blank">https://github.com/dataNdeadlifts/QueryGuard</a>

---

QueryGuard is a command line tool for analyzing SQL queries for best practices and adherance to security policies.

It functions very similarly to static analysis tools for other programing languages such as flake8, ruff, and ESLint but for your database queries.


## Requirements

Python 3.8+


## Installation

<div class="termy">

```console
$ pip install "QueryGuard"
---> 100%
Successfully installed QueryGuard
```

</div>


## Example

### Check all sql files in a folder

<div class="termy">

```console
$ qg ./sql
Processing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File                         ┃ Status    ┃ Violations                ┃ Statements                       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ sql\multiple_violations.sql  │ Failed ❌ │                           │                                  │
│                              │           │ NoCreateLogin (S001)      │ CREATE LOGIN [test_login] WITH … │
│                              │           │ NoCreateServerRole (S004) │                                  │
│                              │           │                           │ GO                               │
│                              │           │                           │ CREATE SERVER ROLE test_role;    │
├──────────────────────────────┼───────────┼───────────────────────────┼──────────────────────────────────┤
│ sql\no_violations.sql        │ Passed ✅ │                           │                                  │
└──────────────────────────────┴───────────┴───────────────────────────┴──────────────────────────────────┘

```

</div>

### Ignore a specific rule

<div class="termy">

```console
$ qg .\sql\multiple_violations.sql --ignore S001
Processing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File                        ┃ Status    ┃ Violations                ┃ Statements                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ sql\multiple_violations.sql │ Failed ❌ │                           │                               │
│                             │           │ NoCreateServerRole (S004) │                               │
│                             │           │                           │ GO                            │
│                             │           │                           │ CREATE SERVER ROLE test_role; │
└─────────────────────────────┴───────────┴───────────────────────────┴───────────────────────────────┘

```


## License

This project is licensed under the terms of the Apache 2.0 license.
