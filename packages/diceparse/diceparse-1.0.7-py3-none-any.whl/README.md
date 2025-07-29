# Rolling Dice

## Requirements

- Python version 3.11 or greater
- The [`uv` dependency manager](https://docs.astral.sh/uv/) to handle dependency installation and virtual environment creation

To get everything setup:

```console
$ uv venv
$ uv sync
```

## Documentation

You can view the documentation by either going to the [online website](https://dice.jamesthebard.net) or by running it locally on your computer with the following commands.  It will be accessible at [`http://127.0.0.1:8000`](http://127.0.0.1:8000).

```shell
$ uv sync --group docs
$ source .venv/bin/activate
$ mkdocs serve
```

```
INFO    -  Building documentation...
INFO    -  Cleaning site directory
INFO    -  Documentation built in 0.14 seconds
INFO    -  [11:41:03] Watching paths for changes: 'docs', 'mkdocs.yml'
INFO    -  [11:41:03] Serving on http://127.0.0.1:8000/
```