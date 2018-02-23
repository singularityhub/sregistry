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
    make_collection_private,
    make_collection_public,
    my_collections,
    view_collection
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
