# Copyright 2025 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from requests.auth import AuthBase

auth_header = "X-Cisco-AI-Defense-API-Key"


class RuntimeAuth(AuthBase):
    """Custom authentication class for runtime authentication."""

    def __init__(self, token: str):
        self.token = token
        self.validate()

    def __call__(self, request):
        request.headers[auth_header] = f"{self.token}"
        return request

    def validate(self):
        """Validate the API key format."""
        if not self.token or not isinstance(self.token, str) or len(self.token) != 64:
            raise ValueError("Invalid API key format")
        return True
