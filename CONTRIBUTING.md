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

# Contributing

Feedback and contribution are welcome!

## Table of Contents

* [General Information](#general-information)
* [Contributions](#contributions)
* [Attributing](#attribution)

## General Information

Please provide ideas via issues or pull requests to our GitLab repository:
[https://github.com/Ian2020/offlinebooks](https://github.com/Ian2020/offlinebooks).

Our documentation consists of the following files in the repository:

* AUTHORS.md
* CHANGELOG.md
* CODE_OF_CONDUCT.md
* CONTRIBUTING.md (this file)
* GOVERNANCE.md
* README.md
* LICENSES directory

## Contributions

Please note that this project is released with a Contributor Code of Conduct. By
participating in this project you agree to abide by its terms. We use the
[Contributor Convenant version
2.0](https://www.contributor-covenant.org/version/2/0/code_of_conduct.html) a
copy of which is available in the repository: CODE_OF_CONDUCT.md. This code is
the same as used by the Linux kernel and many other projects.

### Building

You'll need to install the prerequisites as stated in the README section
'Install'. On top of that there are some prerequisites for building the code:

* We use [ninja](ninja-build.org/) as our build tool, it's available as
  package `ninja-build` on most distros.
* Python [build](https://pypi.org/project/build/) is needed to build our Python
  package: `pip install build`.
* We use the [REUSE tool](https://github.com/fsfe/reuse-tool) to check licensing
  is compliant. This is available either through pip or some distros have it
  available as package `reuse`.

Once you've checked out the code run the following from the new source dir:

* Run `./configure` to create your own build settings file `build_config.ninja`.
  You can change the build dir by adding a line `builddir=DIR`, where DIR is
  where you want build artifacts to end up. The default dir is `build`.
* Run `ninja` to build the project.

To install offlinebooks from your source directory run: `pip install .`, this
installs from source and does not require any building. You should then be able
to run your new version with `offlinebooks`.

### Adding a new Entity

To add a new entity we need the following details from the [API
docs](https://developer.xero.com/documentation/api):

* You'll need the name of its Xero identifier field. For example for Contacts
  this is `ContactID`. This is used for the filename which will store the
  entities.
* Is it paged? This may show up as a `page` parameter for the entity. If so use
  the `paged_generator` lambda, if not use `all_generator`.
* Are there any additional parameters to set to retrieve all data? For example
  for Contacts you need to pass the optional parameter `includeArchived=true` to
  get archived contacts. Pass this to the generator lambda as extra args.
* Don't worry if it has attachments or not - we will grab them if they are
  found automatically.

Once armed with this info it should be obvious how to add a new entity into the
code if you look at the existing ones. For an example of how its done see
[this commit](https://github.com/Ian2020/offlinebooks/commit/1eec3f391f5c5edfbfdf781ba281822a09dabcfd).

### Releasing

* Update [CHANGELOG.md](CHANGELOG.md) and set [setup.cfg](setup.cfg) version
  number.
* Commit all outstanding changes with a commit msg prepended with the VERSION.
  Then tag `git tag -a VERSION`. In the description copy changes from the
  CHANGELOG being careful to remove markdown headings as these are interpreted
  as comments by git. See existing tags for guidance. Remember to git push
  changes and tags.
* Run `ninja pypi_upload`, ensuring `twine_repo=pypi` to upload to PyPI.

### Developer Certificate of Origin (DCO)

All contributions must agree to the Developer Certificate of Origin (DCO) to
certify that you wrote or otherwise have the right to submit code or
documentation to the project. We use the same DCO as many other projects: the
[Developer Certificate of Origin version
1.1](https://developercertificate.org/):

> Developer Certificate of Origin
> Version 1.1
>
> Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
> 1 Letterman Drive
> Suite D4700
> San Francisco, CA, 94129
>
> Everyone is permitted to copy and distribute verbatim copies of this
> license document, but changing it is not allowed.
>
>
> Developer's Certificate of Origin 1.1
>
> By making a contribution to this project, I certify that:
>
> (a) The contribution was created in whole or in part by me and I
>     have the right to submit it under the open source license
>     indicated in the file; or
>
> (b) The contribution is based upon previous work that, to the best
>     of my knowledge, is covered under an appropriate open source
>     license and I have the right under that license to submit that
>     work with modifications, whether created in whole or in part
>     by me, under the same open source license (unless I am
>     permitted to submit under a different license), as indicated
>     in the file; or
>
> (c) The contribution was provided directly to me by some other
>     person who certified (a), (b) or (c) and I have not modified
>     it.
>
> (d) I understand and agree that this project and the contribution
>     are public and that a record of the contribution (including all
>     personal information I submit with it, including my sign-off) is
>     maintained indefinitely and may be redistributed consistent with
>     this project or the open source license(s) involved.

Simply submitting a contribution implies this agreement however for larger
contributions please include a "Signed-off-by" tag in every patch (this tag is a
conventional way to confirm that you agree to the DCO). You can do this with git
commit --signoff (the -s flag is a synonym for --signoff).

Another way to do this is to write the following at the end of the commit
message, on a line by itself separated by a blank line from the body of the
commit:

```text
Signed-off-by: YOUR NAME <YOUR.EMAIL@EXAMPLE.COM>
```

You can signoff by default in this project by creating a file (say
"git-template") that contains some blank lines and the signed-off-by text above;
then configure git to use that as a commit template. For example:

```text
git config commit.template ~/cii-best-practices-badge/git-template
```

It's not practical to fix old contributions in git, so if one is forgotten, do
not try to fix them. We presume that if someone sometimes used a DCO, a commit
without a DCO is an accident and the DCO still applies.

### License

All (new) contributed material must be released under the AGPLv3 or later. A copy
of the license is included in the repository, see the LICENSES directory. All
new contributed material that is not executable, including all text when not
executed, is also released under the [Creative Commons Attribution ShareAlike
4.0 International (CC BY-SA
4.0)](https://creativecommons.org/licenses/by-sa/4.0/) license.

### Code Changes

* When reusing components they MUST have a license compatible with the license of
  this software.
* Test coverage is required except in case of trivial changes

## Attribution

Parts of this text are based on the contribution guide of the Core
Infrastructure Initiative's
[Best Practices Badge
Project](https://github.com/coreinfrastructure/best-practices-badge/blob/master/CONTRIBUTING.md),
licensed under the [Creative Commons Attribution 3.0 International (CC BY 3.0)
license or later.](https://creativecommons.org/licenses/by/3.0/):

Specifically the following sections were copied and adapted: the introduction,
'General information', 'Developer Certificate of Origin (DCO)', 'License',
'Vulnerability Reporting' and 'Code Changes'.
