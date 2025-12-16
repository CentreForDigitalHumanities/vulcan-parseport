# Copyright 2022 Jonas Groschwitz
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This file is derived from vulcan/server_launcher.py
# Original source: https://github.com/jgroschwitz/vulcan

# MODIFICATIONS:
# - Removed unused imports
# - Removed comment.
# - Linting.


from vulcan.file_loader import create_layout_from_filepath
from vulcan.server.server import Server


def launch_server_from_file(
    input_path: str,
    port=5050,
    address="localhost",
    is_json_file=False,
    show_node_names=False,
    propbank_path: str | None = None,
    show_wikipedia_articles=False,
):

    layout = create_layout_from_filepath(
        input_path,
        is_json_file,
        propbank_path,
        show_wikipedia_articles,
    )

    server = Server(
        layout,
        port=port,
        address=address,
        show_node_names=show_node_names,
    )

    server.start()
