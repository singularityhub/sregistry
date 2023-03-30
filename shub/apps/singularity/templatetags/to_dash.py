"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from django import template

register = template.Library()


@register.filter
def to_dash(value):
    if isinstance(value, str):
        return value.replace(".", "-")
    return value
