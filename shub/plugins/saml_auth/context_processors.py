"""

Copyright (C) 2017-2020 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from shub.settings import AUTH_SAML_IDP, AUTH_SAML_INSTITUTION


def saml_processor(request):
    return {
        "AUTH_SAML_IDP": AUTH_SAML_IDP,
        "AUTH_SAML_INSTITUTION": AUTH_SAML_INSTITUTION,
    }
