# `add`

Adds package(s) to pyproject, installs it and lock version

## Arguments

- `packages`: Packages to install

## Options

- `-g`,`--group`: The group to add dependency to (it will be inserted in the `[project.optional-dependencies.<group>]` pyproject section)

## Examples

Install dependencies to group:

```bash
spm add -g docs mkdocs mkdocs-material
```
