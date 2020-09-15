"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

Modified from: https://github.com/mugwort-rc/django-pgpdb
Commit: 763c2708c16bf58064f741ceb2e2ab752dea3663 (no LICENSE)

"""

from django import forms
from django.utils.translation import ugettext_lazy as _


class KeyServerAddForm(forms.Form):
    """form used for validation of adding a key"""

    keytext = forms.CharField(widget=forms.Textarea)
    options = forms.CharField(
        required=False, widget=forms.HiddenInput(attrs={"disabled": "disabled"})
    )


class KeyServerLookupForm(forms.Form):
    """form used for validation of looking up a key"""

    op = forms.RegexField(
        r"(?i)(get|index|vindex|x-.+|)",
        required=False,
        widget=forms.RadioSelect(
            choices=(("index", _("Index")), ("vindex", _("Verbose Index")))
        ),
        label=_("Search operation"),
        initial="vindex",
    )
    search = forms.CharField()
    options = forms.CharField(
        required=False, widget=forms.HiddenInput(attrs={"disabled": "disabled"})
    )
    fingerprint = forms.RegexField(
        r"(?i)(on|off|)",
        required=False,
        widget=forms.CheckboxInput(attrs={"checked": "checked", "value": "on"}),
        label=_("Show fingerprint"),
    )
    exact = forms.RegexField(
        r"(?i)(on|off|)",
        required=False,
        widget=forms.CheckboxInput(attrs={"value": "on"}),
        label=_("Exact match"),
    )
