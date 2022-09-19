"""

Copyright (C) 2017-2022 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""

import os

RQ_QUEUES = {"default": {"URL": os.getenv("REDIS_URL", "redis://redis/0")}}

RQ = {"host": "redis", "db": 0}


# background tasks
BACKGROUND_TASK_RUN_ASYNC = True
