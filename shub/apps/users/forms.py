'''

Copyright (c) 2017-2019 Vanessa Sochat

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from crispy_forms.layout import (
    Button, 
    Field, 
    HTML, 
    Layout, 
    Submit
)

from crispy_forms.bootstrap import (
    AppendedText, 
    FormActions, 
    PrependedText, 
    Tab,
    TabHolder
)

from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from shub.apps.users.models import Team

from django.forms import ModelForm
from django import forms


class TeamForm(ModelForm):

    class Meta:
        model = Team
        fields = ("name", "team_image", "permission",)

    def clean(self):
        cleaned_data = super(TeamForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):

        super(TeamForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout()
        tab_holder = TabHolder()
        self.helper.add_input(Submit("submit", "Save"))
