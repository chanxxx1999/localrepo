# Copyright 2016 Splunk, Inc.
# SPDX-FileCopyrightText: 2020 2020
#
# SPDX-License-Identifier: Apache-2.0

"""
This module contains configuration parser for Splunk local.metadata.
"""

import os
import re

try:
    from configparser import ConfigParser, NoSectionError, NoOptionError
except ImportError:
    from ConfigParser import (
        SafeConfigParser as ConfigParser,
        NoSectionError,
        NoOptionError,
    )

from .splunkenv import make_splunkhome_path

__all__ = ["MetadataReader"]


class MetadataReader:
    """Metadata reader for `app`.

    :param app: App name.
    :type app: ``string``

    :raises IOError: If Splunk `app` doesn't exist.
    """

    def __init__(self, app):
        local_meta = make_splunkhome_path(
            ["etc", "apps", app, "metadata", "local.meta"]
        )

        self._cfg = ConfigParser()
        # Loosen restriction on stanzas without header names.
        self._cfg.SECTCRE = re.compile(r"\[(?P<header>[^]]*)\]")

        if os.path.isfile(local_meta):
            # May raise ConfigParser.ParsingError
            self._cfg.read(local_meta)
        else:
            raise OSError("No such file: %s." % local_meta)

    def get(self, conf, stanza, option):
        """Return the metadata value of option in [conf/stanza] section.

        :param conf: Conf name.
        :type conf: ``string``
        :param stanza: Stanza name.
        :type stanza: ``string``
        :param option: Option name in section [conf/stanza].
        :type option: ``string``
        :returns: Value of option in section [conf/stanza].
        :rtype: ``string``

        :raises ValueError: Raises ValueError if the value cannot be determined.
            Note that this can occur in several situations:

        - The section does not exist.
        - The section exists but the option does not exist.
        """

        try:
            return self._cfg.get("/".join([conf, stanza]), option)
        except (NoSectionError, NoOptionError):
            raise ValueError("The metadata value could not be determined.")

    def get_float(self, conf, stanza, option):
        """Return the metadata value of option in [conf/stanza] section as a float.

        :param conf: Conf name.
        :type conf: ``string``
        :param stanza: Stanza name.
        :type stanza: ``string``
        :param option: Option name in section [conf/stanza].
        :type option: ``string``
        :returns: A float value.
        :rtype: ``float``

        :raises ValueError: Raises ValueError if the value cannot be determined.
            Note that this can occur in several situations:

        - The stanza exists but the value does not exist (perhaps having never
          been updated).
        - The stanza does not exist.
        - The value exists but cannot be converted to a float.
        """

        try:
            return self._cfg.getfloat("/".join([conf, stanza]), option)
        except (NoSectionError, NoOptionError):
            raise ValueError("The metadata value could not be determined.")
