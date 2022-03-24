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
import logging
import os
import subprocess
from collections import namedtuple
from pathvalidate import sanitize_filename
from tenacity import (retry, stop_after_delay, stop_after_attempt)
from xero.auth import OAuth2Credentials
from xero import Xero
from xero.exceptions import XeroRateLimitExceeded


Entity = namedtuple("Entity", "id data")

# #########################
# TENACITY CUSTOM CALLBACKS
# #########################


# [Re-raising RetryError from retry_error_callback · Issue #296 · jd/tenacity]
# (https://github.com/jd/tenacity/issues/296)
def retry_on_error(retry_state):
    logger = logging.getLogger(__name__)
    logger.exception(
        "Max retries exceeded",
        extra={"stats": retry_state.retry_object.statistics},
    )
    raise retry_state.retry_object.retry_error_cls(retry_state.outcome) \
          from retry_state.outcome.exception()


def retry_if_minute_rate_limit_exceeded(retry_state):
    # We seem to get called even if method did not fail, ignore
    if not retry_state.outcome.failed:
        return False
    return \
        (isinstance(retry_state.outcome.exception(), XeroRateLimitExceeded)
         and
         retry_state.outcome.exception().response.headers.get(
             "X-Rate-Limit-Problem") == 'minute')


def wait_till_api_says_retry(retry_state) -> float:
    default = 60.0
    if isinstance(retry_state.outcome.exception(), XeroRateLimitExceeded):
        default = \
                float(
                    retry_state.outcome.exception().response.headers.get(
                        "Retry-After"))
    # Add a tiny buffer just in case
    return default + 1


def before_sleep_log(retry_state):
    logger = logging.getLogger(__name__)
    logger.warning(f"Xero API rate-limit exceeded for calls per minute, "
                   f"will pause for {retry_state.next_action.sleep}s")
    if isinstance(retry_state.outcome.exception(), XeroRateLimitExceeded):
        headers = retry_state.outcome.exception().response.headers
        logger.warning("API reported the following remaining limits:")
        logger.warning(
            f"  app minute : {headers.get('X-AppMinLimit-Remaining')}")
        logger.warning(
            f"  daily      : {headers.get('X-DayLimit-Remaining')}")


# ########
# FETCHERS
# ########


class BankTransactions:
    def __init__(self, xero):
        self.name = "banktransactions"
        self.fetch = lambda: paged_generator(xero.banktransactions,
                                             "BankTransactionID")


class BankTransfers:
    def __init__(self, xero):
        self.name = "banktransfers"
        self.fetch = lambda: all_generator(xero.banktransfers,
                                           "BankTransferID")


class ManualJournals:
    def __init__(self, xero):
        self.name = "manualjournals"
        self.fetch = lambda: paged_generator(xero.manualjournals,
                                             "ManualJournalID")


class Payments:
    def __init__(self, xero):
        self.name = "payments"
        self.fetch = lambda: paged_generator(xero.payments,
                                             "PaymentID")


class Contacts:
    def __init__(self, xero):
        self.name = "contacts"
        self.fetch = lambda: paged_generator(xero.contacts, "ContactID",
                                             includeArchived=True)


class Journals:
    def __init__(self, xero):
        self.name = "journals"
        self.xero = xero

    @retry(retry=retry_if_minute_rate_limit_exceeded,
           retry_error_callback=retry_on_error,
           stop=stop_after_delay(90) | stop_after_attempt(5),
           before_sleep=before_sleep_log,
           wait=wait_till_api_says_retry)
    def fetch(self):
        more = True
        offset = 0
        while more:
            items = self.xero.journals.filter(offset=offset)
            if len(items) == 0:
                more = False
            else:
                for item in items:
                    # Sort journal lines as their order is not guaranteed by
                    # the API
                    item['JournalLines'] = sorted(
                        item['JournalLines'], key=lambda k: k['JournalLineID'])
                    yield Entity(item['JournalID'], item)
                offset = items[-1]['JournalNumber']


class Invoices:
    def __init__(self, xero):
        self.name = "invoices"
        self.fetch = lambda: paged_generator(xero.invoices, "InvoiceID")


class Accounts:
    def __init__(self, xero):
        self.name = "accounts"
        self.fetch = lambda: all_generator(xero.accounts, "AccountID")


class Currencies:
    def __init__(self, xero):
        self.name = "currencies"
        self.fetch = lambda: all_generator(xero.currencies, "Code")


class Items:
    def __init__(self, xero):
        self.name = "items"
        self.fetch = lambda: all_generator(xero.items, "ItemID")


class Organisations:
    def __init__(self, xero):
        self.name = "organisations"
        self.fetch = lambda: all_generator(xero.organisations,
                                           "OrganisationID")


class TaxRates:
    def __init__(self, xero):
        self.name = "taxrates"
        self.fetch = lambda: all_generator(xero.taxrates, "Name")


class Users:
    def __init__(self, xero):
        self.name = "users"
        self.fetch = lambda: all_generator(xero.users, "UserID")


class BrandingThemes:
    def __init__(self, xero):
        self.name = "brandingthemes"
        self.fetch = lambda: all_generator(xero.brandingthemes,
                                           "BrandingThemeID")


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


@retry(retry=retry_if_minute_rate_limit_exceeded,
       retry_error_callback=retry_on_error,
       stop=stop_after_delay(90) | stop_after_attempt(5),
       before_sleep=before_sleep_log,
       wait=wait_till_api_says_retry)
def paged_generator(func, id_field, **kwargs):
    more = True
    page_no = 1
    while more:
        items = func.filter(page=page_no, **kwargs)
        if len(items) == 0:
            more = False
        else:
            for item in items:
                yield Entity(item[id_field], item)
            page_no += 1


@retry(retry=retry_if_minute_rate_limit_exceeded,
       retry_error_callback=retry_on_error,
       stop=stop_after_delay(90) | stop_after_attempt(5),
       before_sleep=before_sleep_log,
       wait=wait_till_api_says_retry)
def all_generator(func, id_field):
    items = func.all()
    for item in items:
        yield Entity(item[id_field], item)


def get_repo():
    # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    if "XDG_DATA_HOME" in os.environ:
        data_home = os.environ["XDG_DATA_HOME"]
    else:
        data_home = os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(data_home, "offlinebooks")


@retry(retry=retry_if_minute_rate_limit_exceeded,
       retry_error_callback=retry_on_error,
       stop=stop_after_delay(90) | stop_after_attempt(5),
       before_sleep=before_sleep_log,
       wait=wait_till_api_says_retry)
def process_attachments(xero, entity, entity_attachments_dir):
    attachmentContainer = xero.invoices.get_attachments(entity.id)
    for attach in attachmentContainer['Attachments']:
        download = False
        attach_filename = os.path.join(entity_attachments_dir,
                                       attach['FileName'])
        if os.path.exists(attach_filename):
            # TODO: This check may not be sufficient if an attachment is
            # updated but the same size as before. We should also check if its
            # unique ID has changed.
            if os.path.getsize(attach_filename) != attach['ContentLength']:
                download = True
        else:
            download = True
        if download:
            os.makedirs(entity_attachments_dir, exist_ok=True)
            with open(attach_filename, "wb") as f:
                # TODO: This does not seem robust, to fetch by filename
                xero.invoices.get_attachment(entity.id, attach['FileName'], f)


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

        fetchers = [BankTransactions(xero),
                    BankTransfers(xero),
                    ManualJournals(xero),
                    Payments(xero),
                    Contacts(xero),
                    Journals(xero),
                    Invoices(xero),
                    Accounts(xero),
                    Currencies(xero),
                    Items(xero),
                    Organisations(xero),
                    TaxRates(xero),
                    Users(xero),
                    BrandingThemes(xero),
                    ]

        for fetcher in fetchers:
            save_dir = os.path.join(repo_tenantId, fetcher.name)
            os.makedirs(save_dir, exist_ok=True)

            for entity in fetcher.fetch():
                safe_entity_id = sanitize_filename(entity.id)
                entity_path = os.path.join(
                                    save_dir, f"{safe_entity_id}.json")
                entity_attachments_dir = os.path.join(
                                    save_dir, f"{safe_entity_id}_attachments")
                with open(entity_path, "w") as file:
                    json.dump(entity.data,
                              file,
                              indent=4,
                              sort_keys=True,
                              default=str)
                if 'HasAttachments' in entity.data and \
                   bool(entity.data['HasAttachments']):
                    process_attachments(xero, entity, entity_attachments_dir)


if __name__ == "__main__":
    main()
