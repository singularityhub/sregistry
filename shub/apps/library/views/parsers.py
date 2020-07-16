"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from rest_framework.parsers import BaseParser


class EmptyParser(BaseParser):
    """Parser for empty stream for unused PUT endpoint.
    """

    media_type = ""

    def parse(self, stream, media_type=None, parser_context=None):
        """Returns the read stream, which should be empty.
        """
        return stream.read()
