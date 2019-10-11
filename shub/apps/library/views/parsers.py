'''

Copyright (C) 2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from django.conf import settings
from rest_framework.parsers import (
    BaseParser,
    DataAndFiles
)
from django.http.multipartparser import MultiPartParserError, parse_header

import codecs
from urllib import parse

from django.conf import settings
from django.core.files.uploadhandler import StopFutureHandlers
from django.http import QueryDict
from django.http.multipartparser import ChunkIter
from django.http.multipartparser import \
    MultiPartParser as DjangoMultiPartParser
from django.http.multipartparser import MultiPartParserError, parse_header
from django.utils.encoding import force_str

from rest_framework import renderers
from rest_framework.exceptions import ParseError
from rest_framework.settings import api_settings
from rest_framework.utils import json


import os
import uuid


class OctetStreamParser(BaseParser):
    """
    Parser for file upload data.
    """
    media_type = 'application/octet-stream'
    errors = {
        'unhandled': 'FileUpload parse error - none of upload handlers can handle the stream',
    }

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Treats the incoming bytestream as a raw file upload and returns
        a `DataAndFiles` object.
        `.data` will be None (we expect request body to be a file content).
        `.files` will be a `QueryDict` containing one 'file' element.
        """
        parser_context = parser_context or {}
        request = parser_context['request']
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
        meta = request.META
        upload_handlers = request.upload_handlers

        print("WE ARE IN THE PARSER")
        filename = "%s.sif" %(str(uuid.uuid4()))
        print(filename)

        # Note that this code is extracted from Django's handling of
        # file uploads in MultiPartParser.
        content_type = meta.get('HTTP_CONTENT_TYPE',
                                meta.get('CONTENT_TYPE', ''))
        try:
            content_length = int(meta.get('HTTP_CONTENT_LENGTH',
                                          meta.get('CONTENT_LENGTH', 0)))
        except (ValueError, TypeError):
            content_length = None

        # See if the handler will want to take care of the parsing.
        for handler in upload_handlers:
            result = handler.handle_raw_input(stream,
                                              meta,
                                              content_length,
                                              None,
                                              encoding)
            if result is not None:
                return DataAndFiles({}, {'file': result[1]})

        # This is the standard case.
        possible_sizes = [x.chunk_size for x in upload_handlers if x.chunk_size]
        chunk_size = min([2 ** 31 - 4] + possible_sizes)
        chunks = ChunkIter(stream, chunk_size)
        counters = [0] * len(upload_handlers)

        for index, handler in enumerate(upload_handlers):
            try:
                handler.new_file(None, filename, content_type,
                                 content_length, encoding)
            except StopFutureHandlers:
                upload_handlers = upload_handlers[:index + 1]
                break

        for chunk in chunks:
            for index, handler in enumerate(upload_handlers):
                chunk_length = len(chunk)
                chunk = handler.receive_data_chunk(chunk, counters[index])
                counters[index] += chunk_length
                if chunk is None:
                    break

        for index, handler in enumerate(upload_handlers):
            file_obj = handler.file_complete(counters[index])
            if file_obj is not None:
                return DataAndFiles({}, {'file': file_obj})

        raise ParseError(self.errors['unhandled'])
