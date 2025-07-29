#!/usr/bin/env python3
"""
Insert data into the README.
"""

import logging
import shlex
import subprocess
import tomllib

from .exception import PrometaException
from .id.hal import get_hal_url_by_origin
from .id.swh import get_swh_url_by_origin, swh_project_exists
from .insert import MarkdownInserter
from .python.common import get_pypi_url

LOGGER = logging.getLogger(__name__)


class ReadmeInserter(MarkdownInserter):
    """
    Insert data into the Markdown file.
    """

    def __init__(self, project):
        super().__init__()
        self.project = project
        self._labels_found = set()

    @staticmethod
    def _split_level(label):
        """
        Extract the header level from a label.

        Args:
            label:
                A string with the label and header leavel in format "<label>
                <level>".

        Returns:
            The label and the level. If no level was found, the level defaults
            to 1.
        """
        label = label.strip()
        try:
            label, level = label.split(None, 1)
        except ValueError:
            LOGGER.debug("Missing header level in label [%s]: assuming 1", label)
            return label, 1
        return label, int(level)

    @staticmethod
    def _get_lang_and_command(label):
        """
        Extract command and optional language from the label.

        Args:
            label:
                A string of the format "command[:<lang>] <cmd>", e.g. "command
                echo test" or "command:yaml some_cmd_to_print_yaml". The command
                string will be parsed by shlex.split().

        Returns:
            The language and the command. The language will be None if not found
            and the command will be a list of command words.
        """
        label, command = label.split(None, 1)
        try:
            label, lang = label.split(":", 1)
            lang = lang.strip()
        except ValueError:
            lang = None
        return lang, shlex.split(command)

    def _get_links_section(self, label):
        """
        Get the section containing standard links.
        """
        label, level = self._split_level(label)
        header_prefix = "#" * (level + 1)

        lines = [f"{header_prefix} GitLab", ""]

        lines.extend(
            self.get_link(name.title(), link)
            for name, link in self.project.urls.items()
        )

        other_repos = []
        if any(self.project.packages):
            lines.append(
                self.get_link(
                    "GitLab package registry",
                    self.project.git_repo.get_section_url("packages"),
                )
            )
            for pkg in self.project.packages.values():
                for name, url in pkg.links:
                    other_repos.append(self.get_link(name, url))

        origin_url = self.project.git_repo.public_git_url
        if swh_project_exists(origin_url):
            other_repos.append(
                self.get_link("Software Heritage", get_swh_url_by_origin(origin_url))
            )

        hal_url = get_hal_url_by_origin(origin_url)
        if hal_url:
            other_repos.append(self.get_link("HAL open science", hal_url))

        if other_repos:
            lines.extend(("", f"{header_prefix} Other Repositories", "", *other_repos))

        return "\n".join(
            line if not line or line.startswith("#") else f"* {line}" for line in lines
        )

    def _get_citation_section(self, _label):
        """
        Get the section containing citation examples for different targets.
        """
        path = self.project.citation_cff_path
        citation_cff_url = self.project.git_repo.get_main_blob_url(path.name)
        blocks = [
            "Please cite this software using the metadata provided in "
            f"[{path.name}]({citation_cff_url}). "
            "The following extracts are provided for different applications.",
            "",
        ]
        if path.exists():
            for fmt in (
                "cff",
                "apalike",
                "bibtex",
                "endnote",
                "ris",
                "schema.org",
                "zenodo",
            ):
                cmd = ["cffconvert", "-i", str(path), "-f", fmt]
                LOGGER.debug("Converting %s to %s", path, fmt)
                output = subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                ).stdout.decode()
                blocks.append(f"{fmt}\n: ~~~\n{output.strip()}\n~~~\n")
        return "\n".join(blocks)

    def _get_command_output_section(self, label):
        """
        Get the output of a command.
        """
        lang, command = self._get_lang_and_command(label)
        if not self.project.config.get("trust_commands", default=False):
            ans = input(f"Run command {command}? [y/N] ")
            if ans.strip().lower() != "y":
                LOGGER.info("Skipping command %s", command)
                return None
        LOGGER.info("Running command: %s", command)
        try:
            output = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                cwd=self.project.readme_md_path.parent,
            ).stdout.decode()
        except (subprocess.CalledProcessError, OSError) as err:
            raise PrometaException(err) from err
        if lang == "embedded_markdown":
            return output
        lang = lang if lang else ""
        return f"~~~{lang}\n{output}\n~~~\n"

    def get_output(self, label, content):
        """
        Override parent get_output.
        """
        self._labels_found.add(label)
        if label.startswith("citations"):
            return self._get_citation_section(label)
        if label.startswith("links"):
            return self._get_links_section(label)
        if label.startswith("command_output"):
            output = self._get_command_output_section(label)
            return content if output is None else output
        LOGGER.warning("Unhandled label in README: %s", label)
        return content
