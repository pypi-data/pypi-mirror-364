##
#   Copyright 2021 Alibaba, Inc. and its affiliates. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##

# -*- coding: utf-8 -*-

from dashvector.common.handler import RPCRequest
from dashvector.core.proto import dashvector_pb2


class GetVersionRequest(RPCRequest):
    def __init__(self):
        """
        GetVersionRequest: google.protobuf.Message
        """
        version_request = dashvector_pb2.GetVersionRequest()

        super().__init__(request=version_request)
