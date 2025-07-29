# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- n/a

# 1.0.6 - 2025-07-22

### Changed

- The fastpurge client's `backoff_max` and `backoff_jitter` parameters are now
  configurable via the `FAST_PURGE_RETRY_BACKOFF_MAX` and `FAST_PURGE_RETRY_JITTER`
  environment variables.

# 1.0.5 - 2024-03-22

### Changed

- Improved handling and logging of retries for requests

## 1.0.4 - 2022-12-07

### Changed

- Use `time.monotonic` from the standard library on python 3.3 or newer and fall
  back to `monotonic` module only on older python versions.

## 1.0.3 - 2021-10-07

### Fixed

- When constructing a `FastPurgeClient` with an `auth` dict, the given dict is no
  longer modified. Previously, dict contents would be modified destructively,
  preventing reuse of the object for more than one client.

### Changed

- Executors are now named for improved metrics/debuggability.

## 1.0.2 - 2019-03-20

### Fixed

- Fixed a wrong example in documentation

### Changed

- Added some additional metadata to PyPI distribution
- Minor improvements to structure of docs

## 1.0.1 - 2019-02-20

### Fixed

- Added missing files (changelog, license) to PyPI distribution

## 1.0.0 - 2019-02-07

### Added

- Initial release
