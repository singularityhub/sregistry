"""

Copyright 2017-2023 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.forms import ModelForm

from shub.apps.users.models import Team


class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ("name", "team_image", "permission")

    def clean(self):
        cleaned_data = super(TeamForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout()
        self.helper.add_input(Submit("submit", "Save"))
