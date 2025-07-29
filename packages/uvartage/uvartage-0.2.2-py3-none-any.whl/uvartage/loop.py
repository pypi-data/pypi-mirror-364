# -*- coding: utf-8 -*-

"""uvartage cmd loop implementation"""

import cmd
import fnmatch
import getpass
import logging
import os
import pathlib
import shlex
import subprocess

from . import backends
from .commons import EMPTY, PACKAGE, POSIX


class Loop(cmd.Cmd):
    """Command loop"""

    intro = "Welcome to the uv wrapper shell. Type help or ? to list commands.\n"
    prompt = f"({PACKAGE}) → "
    _masked = "[masked]"
    _masked_entered_password = "[masked: entered password]"
    _default_index_key = "primary"
    _extra_index_key_base = "extra"

    def __init__(
        self,
        ca_file: pathlib.Path | None,
        hostname_argument: str,
        repositories: list[str],
        default_username: str,
    ) -> None:
        """Initialize with the provided arguments"""
        if not repositories:
            raise ValueError("At least one repository is required")
        #
        self._environment = dict(os.environ)
        if isinstance(ca_file, pathlib.Path):
            ca_full_path = ca_file.resolve()
            if not ca_full_path.is_file():
                raise ValueError(f"{ca_full_path} does not exist or is not a file")
            #
            self._environment.update(SSL_CERT_FILE=str(ca_full_path))
        #
        self._backend = backends.get_backend(
            backends.SupportedBackendType.ARTIFACTORY,
            hostname_argument,
            default_username,
        )
        self._password = getpass.getpass(
            f"Please enter the password for {self._backend.username}"
            f" on {self._backend.hostname} (input is hidden): "
        )
        if not self._password:
            raise ValueError("Stopping due to empty password input")
        #
        self._password_masked: set[str] = set()
        self._extra_indexes: list[str] = []
        for index_number, index_repository in enumerate(repositories):
            self.add_index(index_number, index_repository)
        #
        if self._extra_indexes:
            self._environment.update(UV_INDEX=" ".join(self._extra_indexes))
        #
        super().__init__()

    def add_index(self, index_number: int, index_repository: str) -> None:
        """Add one index"""
        index_url = self._backend.get_index_url(index_repository)
        if not index_number:
            index_key = self._default_index_key
        elif index_number > 0:
            index_key = f"{self._extra_index_key_base}{index_number}"
        else:
            raise ValueError(f"Invalid index number {index_number}")
        #
        index_envvalue = f"{index_key}={index_url}"
        if index_number:
            self._extra_indexes.append(index_envvalue)
        else:
            self._environment.update(UV_DEFAULT_INDEX=index_envvalue)
        #
        index_cred_prefix = f"UV_INDEX_{index_key.upper()}"
        self._password_masked.add(f"{index_cred_prefix}_PASSWORD")
        self._environment.update(
            {
                f"{index_cred_prefix}_USERNAME": self._backend.username,
                f"{index_cred_prefix}_PASSWORD": self._password,
            }
        )

    def execute_command(
        self,
        command: str,
        *additional_args: str,
        arg: str = EMPTY,
    ) -> None:
        """execute command through subprocess.run() in the set environment,
        without outputcapture or check
        """
        full_command = [command] + list(additional_args) + shlex.split(arg)
        subprocess.run(full_command, env=self._environment, check=False)

    def execute_supported_command(
        self,
        command: str,
        *additional_args: str,
        arg: str = EMPTY,
        required_os: str = POSIX,
    ) -> None:
        """execute command through self.execute_command()
        ONLY if it is supported on the current OS
        """
        if os.name == required_os:
            self.execute_command(command, *additional_args, arg=arg)
        else:
            logging.error(
                "The %r command is supported for %s only, bur not for %s",
                command,
                required_os,
                os.name,
            )
        #

    def do_cd(self, arg) -> None:
        """Change directory"""
        if not arg:
            arg = self._environment["HOME"]
        #
        os.chdir(arg)

    def do_env(self, arg) -> None:
        """Print the environment variables"""
        if not arg:
            arg = "*"
        #
        for key in sorted(fnmatch.filter(self._environment, arg)):
            if key in self._password_masked:
                print(f"{key}={self._masked_entered_password}")
            elif any(to_mask in key.lower() for to_mask in ("password", "token")):
                print(f"{key}={self._masked}")
            else:
                print(f"{key}={self._environment[key]}")
            #
        #

    def do_ls(self, arg) -> None:
        """Print directory contents (no autocomplete), POSIX variant"""
        self.execute_supported_command("ls", arg=arg, required_os=POSIX)

    def do_pwd(self, unused_arg) -> None:
        """Print working directory"""
        if unused_arg:
            logging.warning("Ignored argument(s) %r", unused_arg)
        #
        print(os.getcwd())

    def do_uv(self, arg) -> None:
        """Run uv with the provided arguments"""
        self.execute_command("uv", arg=arg)

    def do_uvx(self, arg) -> None:
        """Run uvx with the provided arguments"""
        self.execute_command("uvx", arg=arg)

    # pylint: disable=invalid-name ; required to support EOF character
    def do_EOF(self, unused_arg) -> bool:
        """Exit the REPL by EOF (eg. Ctrl-D on Unix)"""
        print()
        if unused_arg:
            logging.warning("Ignored argument(s) %r", unused_arg)
        #
        logging.info("bye")
        return True

    def emptyline(self) -> bool:
        """do nothing on empty input"""
        return False
