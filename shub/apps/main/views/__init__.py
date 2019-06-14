'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from .download import (
    download_container,
    download_share,
    download_recipe
)

from .collections import (
    all_collections,
    collection_commands,
    collection_settings,
    delete_collection,
    edit_collection,
    edit_contributors,
    get_collection,    
    get_collection_named,
    make_collection_private,
    make_collection_public,
    new_collection,
    my_collections,
    view_collection,
    view_named_collection
)


from .containers import (
    view_container,
    view_named_container,
    get_container,
    change_freeze_status,
    container_details,
    container_tags,
    delete_container
)

from .compare import (
    containers_treemap,
    collection_treemap,
    container_size_data,
    collection_size_data,
    single_collection_size_data
)

from .labels import (
    view_label,
    view_label_key,
    view_label_keyval,
    all_labels,
    get_label,
    update_container_labels
)

from .stars import (
    star_collection,
    collection_stars,
    collection_downloads
)

from .share import (
    generate_share
)

from .tags import (
    remove_tag,
    add_tag,
    all_tags,
    view_tag
)
