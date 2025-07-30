<!--
SPDX-FileCopyrightText: 2025 Free Software Foundation Europe e.V. <mp-explore@fsfe.org>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# MP Explore CLI

Part of the [MP Explore](https://git.fsfe.org/mp-explore/mp-explore) project.

MP Explore CLI allows you to easily run MP Explore Workflows from the CLI.

## Where to get it

You can get it through the [Python Package Index (PyPI)](https://pypi.org/project/mp_explore_core/):

```sh
$ pip3 install mp_explore_cli
```

## How to use it

Assuming you have a workflow at `workflow.toml`

```sh
$ python3 -m mp_explore_cli -w workflow.toml -l DEBUG
```