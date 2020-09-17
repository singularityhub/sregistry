"""

Copyright (C) 2019-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

Modified from: https://github.com/mugwort-rc/django-pgpdb
Commit: 763c2708c16bf58064f741ceb2e2ab752dea3663 (no LICENSE)

"""

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.http.response import Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import pgpdump

from shub.plugins.pgp import forms, models, utils


@csrf_exempt
def add(request):
    """add a key to the keyserver"""
    if request.method != "POST":
        raise Http404

    form = forms.KeyServerAddForm(request.POST)
    c = {}
    try:
        if not form.is_valid():
            raise __AddException
        keytext = form.cleaned_data["keytext"]
        # check keytext
        try:
            pgp = pgpdump.AsciiData(keytext.encode("utf-8", "ignore"))
        except:
            raise __AddException
        keys = utils.parse_public_key_packets(pgp)
        keytexts = []
        for data, packets in keys:
            if not utils.is_valid_packets(packets):
                raise __AddException
            keytext = utils.encode_ascii_armor(data)
            keytexts.append(keytext)
        pgpkeys = []
        for keytext in keytexts:
            pgpkey = models.PGPKeyModel.objects.save_to_storage(None, keytext)
            pgpkeys.append(pgpkey)
        c = {"pgpkeys": pgpkeys}
    except __AddException:
        content = render(request, "pgpdb/add_invalid_post.html")
        return HttpResponseBadRequest(content)
    return render(request, "pgpdb/added.html", c)


def lookup(request):
    """lookup a key on the keyserver"""
    form = forms.KeyServerLookupForm(request.GET)
    try:
        if not form.is_valid():
            raise __LookupException
        search = form.cleaned_data["search"]
        keys = None
        if search.startswith("0x"):
            search_ = search[2:].lower()
            query = {}
            if len(search_) in [32, 40]:
                # v3 or v4 fingerprint
                query = {"public_keys__fingerprint__exact": search_}
            elif len(search_) in [8, 16]:
                # 32bit or 64bit keyid
                query = {"public_keys__keyid__exact": search_}
            else:
                raise __LookupException
            keys = models.PGPKeyModel.objects.filter(**query)
        else:
            query = {"userids__userid__icontains": search}
            keys = models.PGPKeyModel.objects.filter(**query)
        if keys.count() == 0:
            raise __LookupException

        # display by op
        op = form.cleaned_data["op"].lower()
        options_str = form.cleaned_data["options"].lower()
        options = [x.strip() for x in options_str.split(",")]
        if "mr" in options:

            # machine readable response
            if op == "get":
                resp = HttpResponse(
                    utils.keys_ascii_armor(keys),
                    content_type="application/pgp-keys",  # RFC-3156
                )
                resp["Content-Disposition"] = 'attachment; filename="pgpkey.asc"'
                return resp
            else:
                resp = HttpResponse(
                    utils.build_machine_readable_indexes(keys),
                    content_type="text/plain",
                )
                return resp
        else:

            # html response
            op = op if op else "index"
            if op == "get":
                c = {"key": utils.keys_ascii_armor(keys), "search": search}
                return render(request, "pgpdb/lookup_get.html", c)
            elif op in ["index", "vindex"]:
                c = {"keys": keys, "search": search}
                if op == "index":
                    return render(request, "pgpdb/lookup_index.html", c)
                else:
                    return render(request, "pgpdb/lookup_vindex.html", c)

    except __LookupException:
        content = render(request, "pgpdb/lookup_not_found.html")
        return HttpResponseNotFound(content)


class __AddException(Exception):
    pass


class __LookupException(Exception):
    pass
