# sysdi
[![nox](https://github.com/level12/sysdi/actions/workflows/nox.yaml/badge.svg)](https://github.com/level12/sysdi/actions/workflows/nox.yaml)
[![pypi](https://img.shields.io/pypi/v/sysdi)](https://pypi.org/project/sysdi/)


Manages systemd units and timers.  See:

* [Example](https://github.com/level12/sysdi/blob/main/src/sysd_example.py): for typical usage
* `class TimedUnit` in [core.py](https://github.com/level12/sysdi/blob/main/src/sysdi/core.py) for
  additional options and commentary.


## Dev

### Copier Template

Project structure and tooling mostly derives from the [Coppy](https://github.com/level12/coppy),
see its documentation for context and additional instructions.

This project can be updated from the upstream repo, see
[Updating a Project](https://github.com/level12/coppy?tab=readme-ov-file#updating-a-project).

### Project Setup

From zero to hero (passing tests that is):

1. Ensure [host dependencies](https://github.com/level12/coppy/wiki/Mise) are installed

2. Start docker service dependencies (if applicable):

   `docker compose up -d`

3. Sync [project](https://docs.astral.sh/uv/concepts/projects/) virtualenv w/ lock file:

   `uv sync`

4. Configure pre-commit:

   `pre-commit install`

5. Run tests:

   `nox`

### Versions

Versions are date based.  A `bump` action exists to help manage versions:

```shell

  # Show current version
  mise bump --show

  # Bump version based on date, tag, and push:
  mise bump

  # See other options
  mise bump -- --help
```
