---
title: README
author: Jan-Michael Rye
---

# Synopsis

Prometa is a tool to help automate project metadata updates. Currently it can do the following:

* Centralize common data such as author names, email addresses, affiliations and ORCID and HAL identifiers in custom configuration files to ensure their homogeneity.
* Discover [Software Heritage](https://python-gitlab.readthedocs.io/en/stable/index.html) identifiers based on Git remote origin.
* Discover [HAL open science](https://hal.science/) identifiers based on Git remote origin.
* Update [pyproject.toml](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/):
    - author data
    - SPDX license type
    - project URLs based on current Git remote origin (GitLab, HAL, Software Heritage, etc.)
* Generate [codemeta.json](https://codemeta.github.io/user-guide/) files with [CodeMetaPy](https://pypi.org/project/CodeMetaPy/) from pyproject.toml and other supported files. Prometa handles bugs with the current version of CodeMetaPy that prevent it from processing README and license objects.
* Generate [CITATION.cff](https://citation-file-format.github.io/) from the Prometa configuration file and codemeta.json.
* Automatically insert data into README files:
    - Project links (e.g. GitLab, PyPI, HAL, Software Heritage)
    - Command output (e.g. help messages, example configuration files).
    - Citation data from CITATIONS.CFF in different output formats.
* Generate GitLab CI configurations:
    - Register Python packages.
    - Create release jobs when tags are pushed to the main branch.
    - Update tags across various CI jobs.
* Create a [Software Heritage](https://www.softwareheritage.org/) GitLab hook using [python-gitlab](https://python-gitlab.readthedocs.io/en/stable/index.html)

Prometa does not directly modify existing files. Instead, it will create a temporary file with the suggested changes and then launch a user-configurable file merger (vimdiff by default) for the user to manually integrate the suggested changes as desired.

# Links

[insert: links]: #

## GitLab

* [Homepage](https://gitlab.inria.fr/jrye/prometa)
* [Source](https://gitlab.inria.fr/jrye/prometa.git)
* [Issues](https://gitlab.inria.fr/jrye/prometa/issues)
* [Documentation](https://jrye.gitlabpages.inria.fr/prometa)
* [GitLab package registry](https://gitlab.inria.fr/jrye/prometa/-/packages)

## Other Repositories

* [Python Package Index (PyPI)](https://pypi.org/project/Prometa/)
* [Software Heritage](https://archive.softwareheritage.org/browse/origin/?origin_url=https%3A//gitlab.inria.fr/jrye/prometa.git)

[/insert: links]: #

# Configuration

Prometa loads configuration files named `prometa.yaml` or `.prometa.yaml` in the current project directory and any parent thereof. These files will be merged internally to create a single configuration, with files in child directories taking precedence over their parent. This allows the user to keep common settings in a parent directory while allowing more specific settings in the context of a specific project or group of projects. Configuration files may also be placed in standard [XDG configuration directory locations](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html). These will be loaded with the lowest priority.

[insert: command_output:yaml prometa --gen-config -]: #

~~~yaml
# A list of authors. They will appear in various files (e.g. pyproject.toml,
# codemeta.json, CITATIONS.cff).
authors:
    # Given names (required)
  - given-names: John

    # Family names (required)
    family-names: Doe

    # Email (optional)
    email: john.doe@example.com

    # Affiliation (optional)
    affiliation: Example Institute

    # ORCID identifier (optional)
    orcid: XXXX-XXXX-XXXX-XXXX

    # HAL Open Science identifier (optional)
    hal: XXXXXXX

# If true, create missing CITATIONS.cff files.
citations_cff: true

# GitLab settings (optional)
gitlab:
  # Prometa uses python-gitlab to manage GitLab hooks that push code to other
  # open repositories (currently only Software Heritage). python-gitlab requires
  # both a configuration file and the name of the section in the configuration
  # file to use for a given project. For details, see the documentation:
  #
  # https://python-gitlab.readthedocs.io/en/stable/cli-usage.html#cli-configuration
  #
  # python-gitlab configuration file:
  config: path/to/python-gitlab.cfg

  # The section of the python-gitlab configuration file to use when retrieving
  # GitLab project data.
  section: somewhere

  # If true, update the project description.
  update_description: true

  # Set the merge policy (merge, rebase_merge, ff).
  merge_method: ff

  # Configure protect branches. The key is the branch name and the value is
  # either a dict or null. Null values will unprotect the corresponding branch.
  # Dict values contain the following keys to configure how the branch is
  # protected:
  #
  #   merge: who is allowed to merge
  #   push: who is allowed to push and merge
  #   push_force: a boolean indicating if force push is allowed
  #
  # merge and push_and_merge accept either an integer access level or any of the
  # constants defined in gitlab.confg.AccessLevel:
  # https://python-gitlab.readthedocs.io/en/stable/api/gitlab.html#gitlab.const.AccessLevel
  protected_branches:
      main:
          merge: maintainers
          push: maintainers
          push_force: false

  # Configure protected tags. The key is the tag string and the value is the
  # access level or null. Null values will unproctect the tag. Access level
  # values are the same as those for protected branches.
  projected_tags:
      "v*": maintainers

  # If true, update project hooks.
  update_hooks: false

  # Configure various badges for GitLab projects. Enable badges will be created,
  # updated and deleted according to project metadata. For example, PyPI
  # downloads will only be created if a pyproject.toml file exists and the
  # corresponding project exists on PyPI.
  enabled_badges:
      - Pipeline Status
      - License
      - PyPI
      - PyPI Downloads
      - Hatch

  # Map GitLab hosts to their corresponding GitLab Pages URL formats. This map
  # will be used to generate documentation links when a "pages" job is detected
  # in the CI configuration file. The namespace and name parameters correspond
  # to those of the GitLab project.
  pages_urls:
    gitlab.com: "https://{namespace}.gitlab.io/{name}"

  # The regular expression for matching release tags. If given, a CI release job
  # will be created for tags that match this pattern. Omit this or set it to
  # null to disable release jobs.
  release_tag_regex: "^v."

  # Configure tags for GitLab CI jobs. This is a mapping of Python regular
  # expressions to lists of tags. Jobs that match the regular expressions will
  # be tagged with the corresponding tags. If multiple regular expressions match
  # a job then it will accumulate the tags.
  #
  # To apply the same tags to all jobs, use the regular expression ".".
  ci_tags:
      ".":
        - tag1
        - tag2
        - tag3

# By default, Prometa will attempt to detect each project's license using the
# spdx-matcher Python package. In some cases the detection fails (e.g. GPL v2
# and GPL v2-only use the same license text). This option can be set to an SPDX
# license identifier (https://spdx.org/licenses/) to force a particular license
# when the detection fails. If null or an empty strign then it will be ignored.
#
# Note that it will not download a new license file or modify the existing
# license file.
license: null

# The utility to use when merging changes. It must accept two file paths (the
# modified file and the original) and return non-zero exit status to indicate an
# error or abort.
merger: vimdiff


# The README interpolator can insert command output into the README. To prevent
# arbitrary command execution, Prometa will prompt the user to confirm a command
# before it is executed. This prompt can be surpressed for trusted READMEs by
# setting the following to true.
trust_commands: false

~~~

[/insert: command_output:yaml prometa --gen-config -]: #

## README Content Insertion

Content can be inserted into the README.md file using invisible comments of the format:

~~~markdown

[insert: <label>]: #

...

[/insert: <label>]: #
~~~

Both the opening and closing tags must be preceded by empty lines to remain invisible when the Markdown is converted to other formats.

The label will determine which content is inserted and everything between the opening and closing insert comments will be replaced with the content specified by the label. The labels may be indented, in which case the inserted content will also be indented to the same level.

Prometa currently recognizes the following labels:

* `citations <level>`: Convert CITATIONS.cff to different formats from using with [cffconvert](https://pypi.org/project/cffconvert/) and insert them into the README. The `<level>` parameter is an integer to indicate the heading level of the current context. It will be used to insert nested headers in the content. If omitted, level 1 is assumed.
* `command_output[:<lang>] <command string>`: Insert the output of an arbitrary command. The user will be prompted to confirm the command before it is run to prevent unknowingly executing arbitrary code. `<command string>` should be a valid shell command string. It will be interpreted internally using [shlex.split()](https://pypi.org/project/cffconvert/). The confirmation prompt will show the user the parsed command. The output will be wrapped in a code block. The user may specify an optional language for syntax highlighting by appending `:<lang>` to the end of the `command_output` label, where `<lang>` is the desired language. For example, to insert YAML output, use `command_output:yaml command arg1 arg2 ...`. The command also supports the custom language tag "embedded_markdown", which will insert the command's output into the Markdown document directly instead of fencing it in a code block.
* `links <level>`: Insert project links such as homepage, source code repository, issue tracker, documentation, etc. Optional third-part repository links (PyPI, SWH, HAL) will also be inserted if Prometa detects that they contain the project. The `<level>` parameter is the same as for `citations` above.

# Installation

## From Source

~~~
git clone https://gitlab.inria.fr/jrye/prometa.git
pip install -U prometa
~~~

## From GitLab Package Registry

Follow the instructions in the link provided above.

# Usage

Prometa provides the `prometa` command-line utility to update project metadata. It should be invoked with the directory paths of the target projects. See `prometa --help` for details.

[insert: command_output prometa -h]: #

~~~
usage: prometa [-h] [--config PATH [PATH ...]] [--gen-config PATH]
               [--list-config {all,existing}] [--no-xdg] [--trust]
               [path ...]

Update project metadata.

positional arguments:
  path                  Path to project directory.

options:
  -h, --help            show this help message and exit
  --config PATH [PATH ...]
                        By default, prometa will search for configuration
                        files named "prometa.yaml" or ".prometa.yaml" in the
                        target directory and all of its parent directories,
                        with precedence given to configuration files closest
                        to the target directory. Additional configuration file
                        paths can be passed with this option and they will
                        take precedence over the detected configuration files.
                        If multiple configuration paths are given with this
                        command, their order determines their precedence.
  --gen-config PATH     Generate a configuration file template at the given
                        path. If the path is "-", the file will be printed to
                        STDOUT. Note that prometa will only look for files
                        named "prometa.yaml" or ".prometa.yaml".
  --list-config {all,existing}
                        List either all paths that will be scanned for
                        configuration files for each given project, or only
                        existing ones. The output is printed as a YAML file
                        mapping project directory paths to lists of possible
                        configuration files.
  --no-xdg              Disable loading of configuration files in standard XDG
                        locations.
  --trust               It is possible to insert arbitrary command output into
                        the README file. By default, prometa will prompt the
                        user for confirmation before running the command to
                        prevent arbitrary code execution in the context of a
                        collaborative environment. This option can be used to
                        disable the prompt if the user trusts all of the
                        commands in the README.

~~~

[/insert: command_output prometa -h]: #
