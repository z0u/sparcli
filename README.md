# Sparcli

Sparcli is a library for visualising metrics on the command line.

Use this library to see the shape of data during execution of data pipelines, simulators and other long-running programs. Each metric is displayed as a sparkline that updates as the data changes. Sparcli is thread-safe and non-blocking.

![Build](https://github.com/z0u/sparcli/workflows/Build/badge.svg)
![Publish](https://github.com/z0u/sparcli/workflows/Publish/badge.svg)
![Canary build](https://github.com/z0u/sparcli/workflows/Canary%20build/badge.svg)


## Usage

Sparcli is [available on pypi](https://pypi.org/project/sparcli/):

```sh
pip install sparcli
```

You can wrap an iterable that produces scalars:

```python
import sparcli, time

for y in sparcli.gen(ys, name="y"):
    do_something(y)
```

You can produce metrics using a context manager:

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

    def callback(self, metrics: Dict[str, Real]):
        self.ctx.record(**metrics)

    def stop(self):
        self.ctx.close()

some_library.register_plugin(MyPlugin())
```


## Development

```sh
pip install --user py-make poetry
poetry install
pymake all
```

```sh
poetry run python demo.py
```
