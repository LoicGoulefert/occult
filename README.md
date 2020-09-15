# occult

[`vpype`](https://github.com/abey79/vpype) plug-in to remove occulted lines from SVG files.


## Examples

`vpype line 0 0 5 5 rect 2 2 1 1 show`

![example1]("img/example1.png")


`vpype line 0 0 5 5 rect 2 2 1 1 occult show`

![example2]("img/example2.png")



## Installation

See the [installation instructions](https://github.com/abey79/vpype/blob/master/INSTALL.md) for information on how
to install `vpype`.


### Existing `vpype` installation

Use this method if you have an existing `vpype` installation (typically in an existing virtual environment) and you
want to make this plug-in available. You must activate your virtual environment beforehand.

```bash
$ pip install git+https://github.com/abey79/occult.git#egg=occult
```

Check that your install is successful:

```
$ vpype --help
Usage: vpype [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -v, --verbose
  -I, --include PATH  Load commands from a command file.
  --help              Show this message and exit.

Commands:
[...]
  Plugins:
    occult
[...]
```

### Stand-alone installation

Use this method if you need to edit this project. First, clone the project:

```bash
$ git clone https://github.com/abey79/occult.git
$ cd occult
```

Create a virtual environment:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip
```

Install `occult` and its dependencies (including `vpype`):

```bash
$ pip install -e .
```

Check that your install is successful:

```
$ vpype --help
Usage: vpype [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -v, --verbose
  -I, --include PATH  Load commands from a command file.
  --help              Show this message and exit.

Commands:
[...]
  Plugins:
    occult
[...]
```


## Documentation

The complete plug-in documentation is available directly in the CLI help:

```bash
$ vpype occult --help
```


## License

See the [LICENSE](LICENSE) file for details.