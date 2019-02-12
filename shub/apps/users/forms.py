'''

Copyright (c) 2017-2019 Vanessa Sochat

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
