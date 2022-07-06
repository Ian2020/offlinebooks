<!--
SPDX-FileCopyrightText: 2021 Ian2020, et. al. <https://github.com/Ian2020>

SPDX-License-Identifier: CC-BY-SA-4.0

Keep your accounts offline

For full copyright information see the AUTHORS file at the top-level
directory of this distribution or at
[AUTHORS](https://github.com/Ian2020/offlinebooks/AUTHORS.md)

This work is licensed under the Creative Commons Attribution 4.0 International
License. You should have received a copy of the license along with this work.
If not, visit http://creativecommons.org/licenses/by/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.8](https://github.com/ian2020/offlinebooks/releases/tag/v0.0.8) - 2022-07-06

### Fixed

* Possible fix for intermittent XeroRateLimitExceeded exceptions.
  * Tenacity does not work with generators, we have to apply it to functions
    that call the generators:
    ["Retry" from tenacity module doesn't work with a generator](https://stackoverflow.com/a/61571713/28170)
  * Tenacity can say in its `retry_state` that a method threw an exception but
    still give it an outcome of 'finished'. We were filtering on 'failed' only
    which meant we were ignoring some API exceptions and letting them bubble
    out. Now we just focus on whether a method had an exception regardless of
    the outcome state.

### Added

* Set changelog and bug tracker URLs in PyPI.

## [0.0.7](https://github.com/ian2020/offlinebooks/releases/tag/v0.0.7) - 2022-03-24

### Added

To try and track down what's causing the occasional XeroRateLimitExceeded
exception we sometimes see the following measures were added:

* Extra logging if we reach the limit of our retries against the API.
* Add a one second buffer to the wait time we're given by the API.

## [0.0.6](https://github.com/ian2020/offlinebooks/releases/tag/v0.0.6) - 2021-12-14

### Fixed

* Now we can cope if Xero API responds that we have breached the calls per minute
  limit. We back off for a time interval as supplied by them and then retry. We
  output this event to the console so users can see the delay.

## [0.0.5](https://github.com/ian2020/offlinebooks/releases/tag/v0.0.5) - 2021-11-10

### Added

* Update dependencies - latest pyxero 0.9.3 fixes some important bugs in
  particular:
  [Release v0.9.3 · freakboy3742/pyxero](https://github.com/freakboy3742/pyxero/releases/tag/v0.9.3)
* Instructions on adding new entities and other minor documentation.

## [0.0.4](https://github.com/ian2020/offlinebooks/releases/tag/v0.0.4) - 2021-07-09

### Added

* Bank transactions, transfers, manual journals and payments now all saved.

### Changed

* Now classified under accounting topic for PyPI.

## [0.0.3](https://github.com/ian2020/offlinebooks/releases/tag/v0.0.3) - 2021-05-27

### Changed

* Journal lines in journals are now sorted by ID before we save them. The API
  brings them back in varying order and this causes nuisance changes in source
  control otherwise.

## [0.0.2](https://github.com/Ian2020/offlinebooks/releases/tag/v0.0.2) - 2021-05-26

### Added

* Attachments are now saved for invoices, contacts and accounts. These will
  appear in a dir `[entity ID]_attachments` alongside the entity they pertain to.

### Changed

* Data is now stored in `~/.local/share/offlinebooks` instead of
  `~/.offlinebooks`. This follows the [XDG Directory
  Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
