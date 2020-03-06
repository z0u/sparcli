# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- stdout and stderr are captured and replayed so the charts don't get corrupted. Ported capturing code from [pytest](https://github.com/pytest-dev/pytest).


## [0.1.3] - 2020-03-01

Initial release.

### Added
- Compacting variables that can have any number of values added to them.
- A text-based terminal sparkline renderer.
- Non-blocking multithreading with deque.
