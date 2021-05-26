#! /bin/env python

# SPDX-FileCopyrightText: 2021 Ian2020, et. al. <https://github.com/Ian2020>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Keep your accounts offline
#
# For full copyright information see the AUTHORS file at the top-level
# directory of this distribution or at
# [AUTHORS](https://github.com/Ian2020/offlinebooks/AUTHORS.md)
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import json
import os
import subprocess
from collections import namedtuple
from pathvalidate import sanitize_filename
from xero.auth import OAuth2Credentials
from xero import Xero


def get_token():
    return eval(subprocess.run(
        ["/usr/bin/secret-tool",
            "lookup",
            "service",
            "com.xero.xoauth",
            "username",
            "offlinebooks:token_set"],
        capture_output=True,
        text=True
        ).stdout.strip())


def get_client_id():
    with open(os.path.join(os.path.expanduser("~"),
                           ".xoauth",
                           "xoauth.json"), "r") as file:
        xoauth = eval(file.read())
    return xoauth['offlinebooks']['ClientId']


def paged_generator(func, id_field, **kwargs):
    more = True
    page_no = 1
    while more:
        items = func.filter(page=page_no, **kwargs)
        if len(items) == 0:
            more = False
        else:
            for item in items:
                yield {"ID": item[id_field], "obj": item}
            page_no += 1


def all_generator(func, id_field):
    items = func.all()
    for item in items:
        yield {"ID": item[id_field], "obj": item}


def journals_generator(xero):
    more = True
    offset = 0
    while more:
        items = xero.journals.filter(offset=offset)
        if len(items) == 0:
            more = False
        else:
            for item in items:
                yield {"ID": item['JournalID'], "obj": item}
            offset = items[-1]['JournalNumber']


def get_repo():
    # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    if "XDG_DATA_HOME" in os.environ:
        data_home = os.environ["XDG_DATA_HOME"]
    else:
        data_home = os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(data_home, "offlinebooks")


def process_attachment(xero, item, filename):
    attachments_dir = f"{filename}_attachments"
    attachmentContainer = xero.invoices.get_attachments(item['ID'])
    for attach in attachmentContainer['Attachments']:
        download = False
        attach_filename = os.path.join(attachments_dir, attach['FileName'])
        if os.path.exists(attach_filename):
            # TODO: This check may not be sufficient if an attachment is
            # updated but the same size as before. We should also check if its
            # unique ID has changed.
            if os.path.getsize(attach_filename) != attach['ContentLength']:
                download = True
        else:
            download = True
        if download:
            os.makedirs(attachments_dir, exist_ok=True)
            with open(attach_filename, "wb") as f:
                # TODO: This does not seem robust, to fetch by filename
                xero.invoices.get_attachment(item['ID'], attach['FileName'], f)


def main():
    client_id = get_client_id()
    token = get_token()

    # Even tho PKCE we set client_secret to avoid bug of exception on refresh
    credentials = OAuth2Credentials(client_id,
                                    token=token,
                                    client_secret="RUBBISH")

    # Don't care if more scopes granted than requested
    # https://stackoverflow.com/a/51643134
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
    if credentials.expired():
        credentials.refresh()

    tenants = credentials.get_tenants()
    xero = Xero(credentials)
    repo = get_repo()

    for tenant in tenants:
        credentials.tenant_id = tenant['tenantId']
        repo_tenantId = os.path.join(repo,
                                     'tenantId',
                                     sanitize_filename(tenant['tenantId']))
        repo_tenantName = os.path.join(repo, 'tenantName')
        os.makedirs(repo_tenantId, exist_ok=True)
        os.makedirs(repo_tenantName, exist_ok=True)

        tenant_sym = os.path.join(repo_tenantName,
                                  sanitize_filename(tenant['tenantName']))
        if not os.path.isdir(tenant_sym):
            os.symlink(repo_tenantId, tenant_sym)

        Getter = namedtuple("Getter", "name generator")
        getters = [
            Getter("contacts",
                   lambda xero: paged_generator(xero.contacts,
                                                "ContactID",
                                                includeArchived=True)),
            Getter("journals", journals_generator),
            Getter("invoices",
                   lambda xero: paged_generator(xero.invoices, "InvoiceID")),
            Getter("accounts",
                   lambda xero: all_generator(xero.accounts, "AccountID")),
            Getter("currencies",
                   lambda xero: all_generator(xero.currencies, "Code")),
            Getter("items",
                   lambda xero: all_generator(xero.items, "ItemID")),
            Getter("organisations",
                   lambda xero: all_generator(xero.organisations,
                                              "OrganisationID")),
            Getter("taxrates",
                   lambda xero: all_generator(xero.taxrates, "Name")),
            Getter("users",
                   lambda xero: all_generator(xero.users, "UserID")),
            Getter("brandingthemes",
                   lambda xero: all_generator(xero.brandingthemes,
                                              "BrandingThemeID")),
                  ]

        for getter in getters:
            dir = os.path.join(repo_tenantId, getter.name)
            os.makedirs(dir, exist_ok=True)

            for item in getter.generator(xero):
                filename = f"{sanitize_filename(item['ID'])}.json"
                item_path = os.path.join(dir, filename)
                with open(item_path, "w") as file:
                    json.dump(item['obj'],
                              file,
                              indent=4,
                              sort_keys=True,
                              default=str)
                if 'HasAttachments' in item['obj'] and \
                   bool(item['obj']['HasAttachments']):
                    process_attachment(xero, item, item_path)


if __name__ == "__main__":
    main()
