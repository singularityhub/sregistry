'''

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

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
        fields = ("name","team_image",)

    def clean(self):
        cleaned_data = super(TeamForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):

        super(TeamForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout()
        #self.helper.layout = Layout(
        #    'name',
        #    'team_image',
        #    HTML("""{% if form.team_image.value %}<img class="img-responsive" src="/images/{{ form.team_image.value }}">{% endif %}""", ))
        tab_holder = TabHolder()
        self.helper.add_input(Submit("submit", "Save"))
