# Usage

## Show Help

`qg --help`

## Configuration

Configuration options can be declared one of three ways. In order of preference.

- At the command line
- As an environment variable
- In a configuration file

### File

QueryGuard configuration can be stored in several different locations depending
on your needs. It can also be specified using the --settings option at the
command line.

File Names:

- queryguard.toml
- .queryguard.toml
- .pyproject.toml

File Locations:

- current directory
- .config directory relative to the current directory
- the parent directory
- a .config directory relative to the parent directory
- the home directory
- a .config directory relative to the home directory

### Environment Variables

QueryGuard looks for environment variables with a prefix of `QUERYGUARD_`
followed by the setting name.For example to ignore rule id S001 you could
set the `QUERYGUARD_IGNORE` environment variable to `S001`.

### Options

A list of the available options.

#### settings

Specify the configuration file to use. Particularly useful when enforcing
rules centrally in a CI process without relying on the projects configuration.

**Example:** Specify a configuration file during execution.
`qg . --settings /etc/queryguard_configuration.toml`

 ---

#### select

Specify a list of enabled rules to use for evaluation.

**Default:** `["S"]`

Example: Only evaluate rule id's S001 and S002 at the command line.

`qg . --select S001, S002`

**Example:** Evaluate all rules in the security group (i.e. S).

`qg . --select S`

**Example:** Only evaluate rule id's S001 and S002 in an environment variable.

`QUERYGUARD_SELECT=S001,S002 qg .`

**Example:** Only evaluate rule id's S001 and S002 in a configuration file.

```toml
[tool.queryguard]
select = ["S001", "S002"]
```

---

#### ignore

Specify a list of enabled rules to ignore for evaluation.

**Default:** `[]`

Example: Skip evaluation of rule id's S001 and S002 at the command line.

`qg . --ignore S001, S002`

**Example:** Skip evaluation of all rules in the security group (i.e. S).

`qg . --ignore S`

**Example:** Skip evaluation of rule id's S001 and S002 in an environment variable.

`QUERYGUARD_IGNORE=S001,S002 qg .`

**Example:** Skip evaluation of rule id's S001 and S002 in a configuration file.

```toml
[tool.queryguard]
ignore = ["S001", "S002"]
```
