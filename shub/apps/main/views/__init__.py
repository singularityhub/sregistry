"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

from .collections import (
    all_collections,
    collection_commands,
    collection_settings,
    delete_collection,
    edit_collection,
    edit_contributors,
    get_collection,
    make_collection_private,
    make_collection_public,
    my_collections,
    new_collection,
    view_collection,
    view_named_collection,
)
from .compare import collection_size_data, collections_treemap, container_size_data
from .containers import (
    change_freeze_status,
    container_details,
    container_tags,
    delete_container,
    get_container,
    view_container,
    view_named_container,
)
from .download import download_container, download_recipe, download_share
from .labels import (
    all_labels,
    get_label,
    update_container_labels,
    view_label,
    view_label_key,
    view_label_keyval,
)
from .share import generate_share
from .stars import collection_downloads, collection_stars, star_collection
from .tags import add_tag, all_tags, remove_tag, view_tag
