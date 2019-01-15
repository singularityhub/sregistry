'''

Copyright (C) 2017-2019 Vanessa Sochat.

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

from django.shortcuts import render
from django.template.context import RequestContext


def handler404(request):
    response = render(request,'base/404.html', {})
    response.status_code = 404
    return response

def handler500(request):
    response = render(request,'base/500.html', {})
    response.status_code = 500
    return response
