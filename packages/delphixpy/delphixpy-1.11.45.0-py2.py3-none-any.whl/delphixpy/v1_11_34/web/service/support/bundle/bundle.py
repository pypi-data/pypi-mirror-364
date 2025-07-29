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
Package "service.support.bundle"
"""
from delphixpy.v1_11_34 import response_validator

def get(engine):
    """
    Retrieve the specified SupportBundleConfiguration object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_34.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_11_34.web.vo.SupportBundleConfiguration`
    """
    url = "/resources/json/delphix/service/support/bundle"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['SupportBundleConfiguration'], returns_list=False, raw_result=raw_result)

def set(engine, support_bundle_configuration=None):
    """
    Update the specified SupportBundleConfiguration object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_34.delphix_engine.DelphixEngine`
    :param support_bundle_configuration: Payload object.
    :type support_bundle_configuration:
        :py:class:`v1_11_34.web.vo.SupportBundleConfiguration`
    """
    url = "/resources/json/delphix/service/support/bundle"
    response = engine.post(url, support_bundle_configuration.to_dict(dirty=True) if support_bundle_configuration else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def upload(engine, support_bundle_upload_parameters=None):
    """
    Generates and uploads a support bundle to the Delphix support site.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_34.delphix_engine.DelphixEngine`
    :param support_bundle_upload_parameters: Payload object.
    :type support_bundle_upload_parameters:
        :py:class:`v1_11_34.web.vo.SupportBundleUploadParameters`
    """
    url = "/resources/json/delphix/service/support/bundle/upload"
    response = engine.post(url, support_bundle_upload_parameters.to_dict(dirty=True) if support_bundle_upload_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def generate(engine, support_bundle_generate_parameters=None):
    """
    Generates a support bundle. Returns a token that can later be used to
    download the file.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_34.delphix_engine.DelphixEngine`
    :param support_bundle_generate_parameters: Payload object.
    :type support_bundle_generate_parameters:
        :py:class:`v1_11_34.web.vo.SupportBundleGenerateParameters`
    :rtype: ``str``
    """
    url = "/resources/json/delphix/service/support/bundle/generate"
    response = engine.post(url, support_bundle_generate_parameters.to_dict(dirty=True) if support_bundle_generate_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['str'], returns_list=False, raw_result=raw_result)

