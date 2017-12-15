'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017 Vanessa Sochat.

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
    Layout, 
    Submit
)

from crispy_forms.bootstrap import TabHolder
from crispy_forms.helper import FormHelper
from django.forms import ModelForm
from django import forms

import os

from shub.apps.main.models import Demo

class DemoForm(ModelForm):

    class Meta:
        model = Demo
        fields = ("description","url","kind")

    def clean(self):
        cleaned_data = super(DemoForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):

        super(DemoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-2'
        self.helper.field_class = 'col-md-10'
        self.helper.layout = Layout()
        tab_holder = TabHolder()
        self.helper.add_input(Submit("submit", "Save"))



def update_form(form,updates):
    '''update_form will update a query dict for a form
    :param form: should be the form object generated from the request.POST
    :param updates: should be a dictionary of {field:value} to update
    '''
    qd = form.data.copy()
    for field,value in updates.iteritems():
        qd[field] = value
    form.data = qd
    return form
