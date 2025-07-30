[![Documentation Status](https://readthedocs.org/projects/repo-on-fire/badge/?version=latest)](https://repo-on-fire.readthedocs.io/en/latest/?badge=latest)

# Repo On Fire

Google's [repo][1] tool - but on fire 🔥

## About

`repo-on-fire` aims to be a thin wrapper around Google's `repo` tool. `repo`
already does a decent job when it comes to managing larger projects consisting
of several `git` repositories. `repo-on-fire` (or - `rof`) doesn't re-invent
the wheel here - instead, it wraps around `repo`, adding
some useful functionality on top. Particularly, this means: `rof` aims
to be 100% command line compatible with `repo` - ideally, where ever you can
use `repo`, you can instead use `rof`, taking benefit of that certain _X_ it
adds.

## Features

Currently, on top of allowing you to call through to any of the `repo` commands,
`repo-on-fire` adds the following features on top:

- Automatic workspace caching.
- The `workspace switch` command can be used to switch to a particular branch
  for the entire workspace.


## Installation

You can use the following to install `repo-on-fire`:

### `pip`

`repo-on-fire` is available on PyPI, hence, you can easily install it using
`pip`. It is recommended to use virtual environments for this, so you can run
the following sequence of commands to create a virtual environment and install
the tool in it:

```bash
# Create a virtual environment:
python -m venv ./repo-on-fire

# Install the tool within the just created virtual environment:
./repo-on-fire/bin/pip install repo-on-file

# And finally, run it:
./repo-on-fire/bin/repo-on-fire --help
```

### PDM

The tool is managed using [PDM](https://pdm-project.org/latest/). Hence, install
it and then you can clone the sources of the tool and install all needed
dependencies in a virtual environment:

```bash
# Get the sources:
git clone https://gitlab.com/rpdev/repo-on-fire.git
cd repo-on-fire

# Install dependencies:
pdm install

# Run it:
pdm run repo-on-fire --help
```

## Documentation

If you want to dive deeper into the tool and what it can do, please head over
to the [documentation](http://repo-on-fire.readthedocs.io/en/latest/).


[1]: https://gerrit.googlesource.com/git-repo
