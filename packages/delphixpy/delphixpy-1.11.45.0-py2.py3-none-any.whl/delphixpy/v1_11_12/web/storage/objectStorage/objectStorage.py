#
# Copyright 2025 by Delphix
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Package "storage.objectStorage"
"""
from delphixpy.v1_11_12 import response_validator

def get(engine):
    """
    Retrieve the specified S3ObjectStore object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_12.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_11_12.web.vo.S3ObjectStore`
    """
    url = "/resources/json/delphix/storage/objectStorage"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['S3ObjectStore'], returns_list=False, raw_result=raw_result)

def set(engine, s3_object_store=None):
    """
    Update the specified S3ObjectStore object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_12.delphix_engine.DelphixEngine`
    :param s3_object_store: Payload object.
    :type s3_object_store: :py:class:`v1_11_12.web.vo.S3ObjectStore`
    """
    url = "/resources/json/delphix/storage/objectStorage"
    response = engine.post(url, s3_object_store.to_dict(dirty=True) if s3_object_store else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def test_connection(engine, s3_object_store_test):
    """
    Test connectivity to an object store.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_12.delphix_engine.DelphixEngine`
    :param s3_object_store_test: Payload object.
    :type s3_object_store_test: :py:class:`v1_11_12.web.vo.S3ObjectStoreTest`
    """
    url = "/resources/json/delphix/storage/objectStorage/testConnection"
    response = engine.post(url, s3_object_store_test.to_dict(dirty=True) if s3_object_store_test else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

