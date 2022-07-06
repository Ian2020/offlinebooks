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

Offlinebooks is a cmdline tool that downloads your Xero financial accounts for
local backup. It is beta quality software and only Linux (GNOME desktop) is
supported at present. Use with caution. The code repository is
at [offlinebooks](https://github.com/Ian2020/offlinebooks).

We are not associated with the Xero organisation and this software is
unsupported. See [Licensing](#licensing) for more details.

## Table of Contents

* [Install](#install)
* [Background](#background)
* [Usage](#usage)
* [Known Issues](#known-issues)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [Licensing](#licensing)
* [Attribution](#attribution)

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

I just wanted a simple way to pull my data from the Xero API and save it locally
for backup.

We save each entity as JSON in its own file, named by its unique ID (where
available) in a simple dir tree structure. This allows for easy processing with
other tools and is also suitable for source control. If an entity has attachments
those are saved next to the entity under a dir named `[entity ID]_attachments`

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
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7_attachments
    │   │   │   └── ...
    │   │   └── ...
    │   ├── brandingthemes
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   └── ...
    │   ├── contacts
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7_attachments
    │   │   │   └── ...
    │   │   └── ...
    │   ├── currencies
    │   │   ├── GBP.json
    │   │   └── ...
    │   ├── invoices
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7.json
    │   │   ├── a6r01id3-690x-7edt-8pd2-c873245y38v7_attachments
    │   │   │   └── ...
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

* Accounts
* Bank Transactions
* Bank Transfers
* Branding theme
* Contacts
* Currencies
* Invoices
* Items
* Journals
* Manual Journals
* Organisations, EXCEPT:
  * Organisation actions
  * CIS Settings (UK)
* Payments
* Users

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
    we just need read permissions for each entity we download. DO NOT ADD ANY
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

If it hits the Xero API minute rate-limit it'll pause for a time interval (as
supplied by the API) before continuing the run. You'll see some output to
indicate this, for example:

```text
Xero API rate-limit exceeded for calls per minute, will pause for 43.0s
API reported the following remaining limits:
  app minute : 9911
  daily      : 2718
```

## Troubleshooting

* `No such file or directory: '~/.xoauth/xoauth.json'` - have you run
  xoauth as detailed above?

## Known Issues

* Possibly fixed since v0.0.8: still get API rate-limits exceeded sometimes:

```bash
Xero API rate-limit exceeded for calls per minute, will pause for 14.0s
API reported the following remaining limits:
  app minute : 9984
  daily      : 4794
Traceback (most recent call last):
  File "/home/user/.local/bin/offlinebooks", line 8, in <module>
    sys.exit(main())
  File "/home/user/.local/lib/python3.9/site-packages/offlinebooks/main.py", line 329, in main
    for entity in fetcher.fetch():
  File "/home/user/.local/lib/python3.9/site-packages/offlinebooks/main.py", line 237, in all_generator
    items = func.all()
  File "/home/user/.local/lib/python3.9/site-packages/xero/basemanager.py", line 264, in wrapper
    raise XeroRateLimitExceeded(response, payload)
xero.exceptions.XeroRateLimitExceeded: please wait before retrying the xero api,the limit exceeded is: minute
```

  This is hard to reproduce. I have added (24th Mar '22) an extra second to our
  wait time in case of rounding issues though I have seen this exception occur
  before we decide to wait. Also added extra logging in case we are reaching
  our retry stop limit without realising.

* Intermittent exception 'oauthlib.oauth2.rfc6749.errors.InvalidGrantError' -
  not sure what causes this. If you do a `xoauth connect` then run again it
  should work.
* A long delay then a failure with exception
  `xero.exceptions.XeroExceptionUnknown: None` whilst calling func.filter with
  paging. If you `xoauth connect` then run again it works.
* We depend on `secret-tool` to retrieve the token which `xoauth` has saved,
  this is GNOME-specific.
* Attachments are only re-fetched if they differ in size to avoid large
  downloads. There's a small chance that an updated attachment which is the same
  size as the original is not fetched.
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
* Within the Accounting API we do not yet save the following (for some we also
  show in parenthesis where these are found in the Xero web GUI):
  * Batch Payments
  * Budgets
  * Contact Groups
  * Credit Notes
  * Employees
  * History and Notes
  * Invoice Reminders
  * Linked Transactions
  * Payment Services
  * Prepayments
  * Purchase Orders
  * Quotes
  * Repeating Invoices (Business-Invoices-Repeating)
  * Reports (Accounting-Reports)
  * Tracking Categories (Accounting-Advanced-Tracking Categories)

## Roadmap

In vague priority order:

* Download remaining data not yet supported from Accounting API above.
  * How are VAT returns covered by the API?
* Allow user to limit tenant(s). Introduce config file in XDG friendly location
* Allow user to specify repo path also
* We should report at the end on API usage if requested: 'Each API response you
  receive will include the X-DayLimit-Remaining, X-MinLimit-Remaining and
  X-AppMinLimit-Remaining headers telling you the number of remaining against
  each limit.' This can be got from the final response we receive.
* Fetch in parallel
* We assume journals start at 1, i.e. setting offset=0 which means querying
  JournalNumber>0. Is this definite?
* Our use of tenacity and handling API limits:
  * We repeat the retry decorator on every function containing an API call.
    Better to remove this duplication.
  * It would be better not to reach into the response and get headers,
    perhaps pyxero's XeroRateLimitExceeded exception could hold the data
    instead.

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

## Attribution

"Xero" is a trademark of Xero Limited.
