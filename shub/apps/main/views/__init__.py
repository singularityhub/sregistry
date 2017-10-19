'''

Copyright (c) 2017, Vanessa Sochat, All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''


from .demos import (
    edit_demo,
    view_demo,
    collection_demos
)

from .download import (
    download_container,
    download_share,
    download_recipe
)

from .collections import (
    all_collections,
    collection_commands,
    delete_collection,
    edit_collection,
    get_collection,    
    make_collection_private,
    make_collection_public,
    my_collections,
    user_collections,
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
