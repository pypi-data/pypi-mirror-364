# Changelog Tools

This project provides tools to manage changelog files, according to the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

<!-- more -->

<div class="grid cards" markdown>

- :material-license: __FreeBSD__ License
- :fontawesome-brands-python: __Python__ >= 3.8 is required
- :fontawesome-solid-link: [https://pypi.org/](https://pypi.org/project/changelog-tools/)
- :fontawesome-solid-at: __Author__ : [Sigilence Technologies](https://pypi.org/user/Sigilence/)

</div>

## Tools

### Usage

```shell
python3 -m changelog_tools <command> [options]
python3 -m changelog_tools --help  # Display usage information and a list of the provided commands.
```

### Available commands

#### **get**

Check and display the latest version of a changelog file, which is by default the CHANGELOG.md file in the current directory.

```shell
python3 -m changelog_tools get
```

**<CHANGELOG_PATH>** (optional)

Specifies a changelog path. If given path is a directory, the tool defaults a CHANGELOG.md file in that directory.

```shell
python3 -m changelog_tools get data/CHANGELOG.md
```

#### **summarize**

To get a list of changes between two versions, run the script:

```shell
python3 -m changelog_tools summarize --old <old_version> --new <new_version> <changelog_path>
```

**--old** (optional)
Specifies a version from which to start looking for changes. This version corresponds to the lowest/oldest of the file.
If not provided, the tool defaults to the initial version. If provided version does not exist in the file, it'll raise an error.

**--new** (optional)
Specifies a version to end looking for changes. This version corresponds to the highest/latest version of the file.
If not provided, the tool defaults to the latest version. If provided version does not exist in the file, it'll raise an error.

**--include_unreleased** (optional)
Set by default to False. It is used to include unreleased items to the output, if needed.

**<CHANGELOG_PATH>** (optional)

Specifies a changelog path. If given path is a directory, the tool defaults a CHANGELOG.md file in that directory.

##### Example of what you'll get

Summary with different sections sorted by alphabetical order.

```
# Changelog summary

Here are all the changes between 0.0.1 and 0.0.3:

### Added

- v1.1 Brazilian Portuguese translation.
- v1.1 German Translation.
- v1.1 Spanish translation.

### Changed

- Use frontmatter title & description in each language version template.
- Replace broken OpenGraph image with an appropriately-sized Keep a Changelog image that will render properly (although in English for all languages).
```
