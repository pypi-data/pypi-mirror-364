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
Package "service.time"
"""
from delphixpy.v1_11_36 import response_validator

def get(engine):
    """
    Retrieve the specified TimeConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_36.delphix_engine.DelphixEngine`
    :rtype: :py:class:`v1_11_36.web.vo.TimeConfig`
    """
    url = "/resources/json/delphix/service/time"
    response = engine.get(url)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=['TimeConfig'], returns_list=False, raw_result=raw_result)

def set(engine, time_config=None):
    """
    Update the specified TimeConfig object.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_36.delphix_engine.DelphixEngine`
    :param time_config: Payload object.
    :type time_config: :py:class:`v1_11_36.web.vo.TimeConfig`
    """
    url = "/resources/json/delphix/service/time"
    response = engine.post(url, time_config.to_dict(dirty=True) if time_config else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

def validate_ntp(engine, validate_ntp_parameters):
    """
    Validate NTP configuration without committing changes by asking NTP server
    for time.

    :param engine: The Delphix Engine
    :type engine: :py:class:`delphixpy.v1_11_36.delphix_engine.DelphixEngine`
    :param validate_ntp_parameters: Payload object.
    :type validate_ntp_parameters:
        :py:class:`v1_11_36.web.vo.ValidateNTPParameters`
    """
    url = "/resources/json/delphix/service/time/validateNtp"
    response = engine.post(url, validate_ntp_parameters.to_dict(dirty=True) if validate_ntp_parameters else None)
    result = response_validator.validate(response, engine)
    raw_result = getattr(engine, 'raw_result', False)
    return response_validator.parse_result(result, undef_enabled=True, return_types=None, returns_list=None, raw_result=raw_result)

