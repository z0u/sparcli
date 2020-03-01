# Sparcli

Sparcli is a library for visualising metrics on the command line.

Use this library to see the shape of data during execution of data pipelines, simulators and other long-running programs. Each metric is displayed as a sparkline that updates as the data changes. Sparcli is thread-safe and non-blocking.

[![Build](https://github.com/z0u/sparcli/workflows/Build/badge.svg)](https://github.com/z0u/sparcli/actions?query=workflow%3ABuild)
[![Publish](https://github.com/z0u/sparcli/workflows/Publish/badge.svg)](https://github.com/z0u/sparcli/actions?query=workflow%3APublish)
[![Canary build](https://github.com/z0u/sparcli/workflows/Canary%20build/badge.svg)](https://github.com/z0u/sparcli/actions?query=workflow%3A%22Canary+build%22)


## Usage

Sparcli is [available on pypi](https://pypi.org/project/sparcli/):

```sh
pip install sparcli
```

You can wrap an iterable that produces scalars:

```python
import sparcli

for y in sparcli.gen(ys, name="y"):
    do_something(y)
```

You can publish metrics using a context manager:

```python
with sparcli.ctx() as ctx:
    for a, b in do_something_else():
        ctx.record(a=a, b=b)
```

You can also manage the context manually. Just don't forget to close it:

```python
class MyMetricsPlugin:
    def start(self):
        self.ctx = sparcli.context()

    def step(self, metrics: Dict[str, Real]):
        self.ctx.record(**metrics)

    def stop(self):
        self.ctx.close()

some_library.register_plugin(MyMetricsPlugin())
```


## Development

```sh
pip install --user poetry
poetry install
make
poetry run python demo.py
```

If you're on a system without GNU Make, you can use py-make instead:

```sh
pip install --user py-make
alias make='pymake'
```
