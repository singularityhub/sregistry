'''

Copyright (C) 2017-2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2017-2018 Vanessa Sochat.

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

from shub.logger import bot
from urllib.parse import unquote
from django.contrib.auth.mixins import LoginRequiredMixin
#from rest_framework.exceptions import PermissionDenied
#from rest_framework.parsers import FormParser, MultiPartParser
#from shub.apps.main.models import Collection,Container
#from rest_framework.viewsets import ModelViewSet
#from shub.apps.api.models import ImageFile  # MyChunkedUpload equivalent
#from rest_framework import serializers
#from shub.apps.api.utils import ( 
#    validate_request, 
#    has_permission, 
#    get_request_user
#)
#from sregistry.main.registry.auth import generate_timestamp

from django.views.generic.base import TemplateView
from chunked_upload.views import (
    ChunkedUploadView,
    ChunkedUploadCompleteView
)

from shub.apps.api.models import ChunkedImage

# TODO: this should link to the command line upload
#class ChunkedUploadTerm():

class ChunkedUploadUI(LoginRequiredMixin, TemplateView):
    template_name = 'routes/upload.html'


class ImageChunkedUpload(LoginRequiredMixin, ChunkedUploadView):

    model = ChunkedImage
    field_name = 'the_file'

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass

    def get_extra_attrs(self, request):
        '''
        Extra attribute values to be passed to the new ChunkedUpload instance.
        Should return a dictionary-like object.
        '''
        return {}


class ImageChunkedUploadComplete(LoginRequiredMixin, ChunkedUploadCompleteView):

    model = ChunkedImage

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass

    def on_completion(self, uploaded_file, request):
        from shub.apps.api.actions.create import upload_container

        body = unquote(request.body.decode('utf-8'))
        params = { a[0]:a[1] for a in [x.split('=') for x in body.split('&')]}

        # Expected params are upload_id, name, md5, and cid
        upload_container(cid = params['cid'],
                         request = request,
                         version = params['md5'],
                         upload_id = params['upload_id'],
                         name = params['name'])

        # Do something with the uploaded file. E.g.:
        # * Store the uploaded file on another model:
        # SomeModel.objects.create(user=request.user, file=uploaded_file)
        # * Pass it as an argument to a function:
        # function_that_process_file(uploaded_file)

    def get_response_data(self, chunked_upload, request):
        return {'message': ("You successfully uploaded '%s' (%s bytes)!" %
                            (chunked_upload.filename, chunked_upload.offset))}
