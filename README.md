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

# offlinebooks

Keep your accounts offline.

Offlinebooks is a cmdline tool that downloads your Xero® financial accounts for
local backup. It is beta quality software and only Linux (GNOME desktop) is
supported at present. Use with caution.

## Table of Contents

* [Install](#install)
* [Background](#background)
* [Usage](#usage)
* [Known Issues](#known-issues)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [Licensing](#licensing)

## Install

Prerequisites:

* Linux (GNOME desktop)
* Python 3
* [Xoauth](https://github.com/XeroAPI/xoauth)

Install the latest version via pip:

```bash
pip install offlinebooks
```

This will install a cmdline tool `offlinebooks`. For usage see below.

## Background

I just wanted a simple way to pull my data from the Xero® API and save it locally
for backup.

We save each item as JSON in its own file, named by its unique ID (where
available) in a simple dir tree structure. This allows for easy processing with
other tools and is also suitable for source control.

Data is saved separately for each tenant (organisation) under their tenant id
and under their human-readable tenant name as a symlink for convenience:

```text
$XDG_DATA_HOME/offlinebooks/
├── tenantName
│   ├── Demo Company (UK) -> $XDG_DATA_HOME/offlinebooks/tenantId/b3b892ur-02i8-4842-8bx2-85696h032kz2
│   └── ...
└── tenantId
    ├── b3b892ur-02i8-4842-8bx2-85696h032kz2
    │   ├── accounts
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   └── ...
    │   ├── brandingthemes
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   └── ...
    │   ├── contacts
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   └── ...
    │   ├── currencies
    │   │   ├── GBP.json
    │   │   └── ...
    │   ├── invoices
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   └── ...
    │   ├── items
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   └── ...
    │   ├── journals
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   └── ...
    │   ├── organisations
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   └── ...
    │   ├── taxrates
    │   │   ├── 15% (VAT on Capital Purchases).json
    │   │   └── ...
    │   └── users
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   └── ...
    └── ...
```

Data covered so far:

* Contacts
* Journals
* Invoices
* Accounts
* Currencies
* Items
* Organisations, EXCEPT:
  * Organisation actions
  * CIS Settings (UK)
* Users
* Branding theme

## Usage

The first time around you will need to add offlinebooks as a PKCE app to your Xero
account and grant it permissions:

* Thanks to
  [JWealthall](https://github.com/JWealthall) you can simply follow his excellent
  [PKCE How To for Xero OAuth2
  API](https://github.com/JWealthall/XeroOAuth2ApiPkceHowTo) with the following
  changes:
  * Use `offlinebooks` as both the 'App name' in Xero and the clientname when
    running `xoauth setup`.
  * For company or application URL you can put whatever you like or can I suggest
    the [offlinebooks project page on PyPI](https://pypi.org/project/offlinebooks/)
  * When it gets to adding scopes we need `openid` to authorise the app and
    `offline_access` to refresh our token on expiry. Beyond that
    we just need read permissions for each item we download. DO NOT ADD ANY
    WRITE PERMISSIONS, they are not needed. The following should suffice:

```bash
xoauth setup add-scope offlinebooks \
  openid \
  offline_access \
  accounting.transactions.read \
  accounting.contacts.read \
  accounting.journals.read \
  accounting.settings.read \
  files.read \
  accounting.reports.read \
  accounting.attachments.read
```

* Once you've completed the How To then you are ready to run offlinebooks:

```bash
offlinebooks
```

If it completes without error you'll find a new dir at
`$XDG_DATA_HOME/offlinebooks` (probably `~/.local/share/offlinebooks`)
containing the downloaded data for you to explore (see above).

## Troubleshooting

* `No such file or directory: '~/.xoauth/xoauth.json'` - have you run
  xoauth as detailed above?

## Known Issues

* Intermittent exception 'oauthlib.oauth2.rfc6749.errors.InvalidGrantError' -
  not sure what causes this. If you do a `xoauth connect` then run again it
  should work.
* We depend on `secret-tool` to retrieve the token which `xoauth` has saved,
  this is GNOME-specific.
* We do not yet download anything outside of the Accounting API, that leaves
  these APIs untouched:
  * Payroll
  * Assets
  * Files
  * Projects
  * Bank Feeds
  * Xero HQ
  * Practice Manager
  * WorkflowMax
* Within the Accounting API we do not yet save the following:
  * Bank statements
  * Bank transactions
  * Branch transfers
  * Batch Payments
  * Budgets
  * Contact Groups
  * Credit Notes
  * Employees
  * History and Notes
  * Invoice Reminders
  * Linked Transactions
  * Manual Journals
  * Payment Services
  * Payments
  * Prepayments
  * Purchase Orders
  * Quotes
  * Repeating Invoices
  * Reports
  * Tracking Categories
  * Types

## Roadmap

In vague priority order:

* Fetch attachments
* Download remaining data not yet supported from Accounting API above.
* Allow user to limit tenant(s). Introduce config file in XDG friendly location
* We should report at the end on API usage if requested: 'Each API response you
  receive will include the X-DayLimit-Remaining, X-MinLimit-Remaining and
  X-AppMinLimit-Remaining headers telling you the number of remaining against
  each limit.'
* Limit API calls to ensure we stay within limits, the important ones per tenant:
  * 60 calls a minute
  * 5 concurrent calls
* Fetch in parallel
* Allow user to specify repo path
* We assume journals start at 1, i.e. setting offset=0 which means querying
  JournalNumber>0. Is this definite?

## Contributing

It's great that you're interested in contributing. Please ask questions by
raising an issue, be sure to get in touch before raising PRs to avoid wasted
work. For full details see [CONTRIBUTING.md](CONTRIBUTING.md)

## Licensing

We declare our licensing by following the REUSE specification - copies of
applicable licenses are stored in the LICENSES directory. Here is a summary:

* All source code is licensed under AGPL-3.0-or-later.
* Anything else that is not executable, including the text when extracted from
  code, is licensed under CC-BY-SA-4.0.

For more accurate information, check individual files.

Offlinebooks is free software: you can redistribute it and/or modify it under the
terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
