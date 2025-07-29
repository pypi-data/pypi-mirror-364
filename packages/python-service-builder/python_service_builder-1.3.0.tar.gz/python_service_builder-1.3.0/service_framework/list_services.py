# Copyright 2022 David Harcombe
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import urllib.parse
import urllib.request
from collections import namedtuple
from contextlib import closing, suppress
from pprint import pprint
from typing import Mapping
from urllib.request import urlopen

import aenum as enum
from absl import app

from service_framework.services import ServiceDefinition

""" _summary_
"""


class ServiceFinder(enum.EnumMeta):
  def __call__(cls, value, *args, **kwargs):
    api = ServiceLister().find(name=value.lower())
    if api:
      (service_name, version) = api[0]
      definition = ServiceDefinition(
          service_name=service_name,
          version=version,
          discovery_service_url=(
              f'https://{service_name}.googleapis.com/$discovery/rest'
              f'?version={version}'))
      return definition

    else:
      raise Exception(f'No service found for {value}')


class ServiceLister(object):
  def find_all(self) -> Mapping[str, str]:
    return self.find(None)

  def find(self, name: str) -> Mapping[str, str]:
    Components = namedtuple(
        typename='Components',
        field_names=['scheme', 'netloc', 'url', 'path', 'query', 'fragment']
    )

    apis = {}

    parameters = {#'fields': 'items.name,items.version',
                  'preferred': 'true'}
    if name:
      parameters |= {'name': name}

    url = urllib.parse.urlunparse(
        Components(
            scheme='https',
            netloc='www.googleapis.com',
            query=urllib.parse.urlencode(parameters),
            path='',
            url='/discovery/v1/apis',
            fragment=None
        )
    )

    r = urllib.request.Request(url)
    with closing(urlopen(r)) as _api_list:
      api_list = json.loads(_api_list.read())
      if items := api_list.get('items', None):
        for api in items:
          apis[api['name'].upper()] = (api['name'], api['version'], api['discoveryRestUrl'])

    return apis


def main(unused) -> None:
  del unused

  # apis = ServiceLister().find(name='CHAT'.lower())
  apis = ServiceLister().find_all()
  pprint(apis, indent=2)


if __name__ == '__main__':
  with suppress(SystemExit):
    app.run(main)
