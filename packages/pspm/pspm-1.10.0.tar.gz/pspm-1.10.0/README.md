# pspm

pspm is Python's Simplest Package Manager.

<div align="center">

![logo-pspm](https://i.imgur.com/1K0qcRW.png)

[![Docs](https://img.shields.io/badge/docs-mkdocs-blue?style=for-the-badge)](https://pspm.jahn16.com/)
[![PyPI - Version](https://img.shields.io/pypi/v/pspm?logo=python&style=for-the-badge)](https://pypi.org/project/pspm/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=for-the-badge)](https://github.com/astral-sh/ruff)
</div>

## Installation

I recommend using [pipx](https://pipx.pypa.io/stable/) to install pspm.

```bash
pipx install pspm[uv]
```

> [!NOTE]
> This will install `pspm` along with `uv`. You may want to [install uv separately](https://docs.astral.sh/uv/getting-started/installation/) and run `pipx install pspm` instead.


## Quickstart

### Initialize project

```bash
spm init
```

### Install packages

```bash
spm add fastapi
```

For more details read the [docs](https://pspm.jahn16.com/)

## License

Licensed under the [GNU GPLv3](LICENSE) license.
