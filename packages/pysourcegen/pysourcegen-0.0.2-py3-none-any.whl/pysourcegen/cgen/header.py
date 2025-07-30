# Copyright 2024 Compen Embedded B.V.
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

from pysourcegen.cgen.item import CItem


class CHeader:

    def __init__(self, guardtext: str):
        self.template = [
            '[HEAD]\n', f'#ifndef DRIVER_{guardtext.upper()}_H',
            f'#define DRIVER_{guardtext.upper()}_H\n', '[INC]', '[ITEMS]\n',
            f'#endif  // DRIVER_{guardtext.upper()}_H'
        ]
        self.__includes = []
        self.__items = []
        self.__head = []
        self.__spaces = 4

    def AddHead(self, head: CItem) -> None:
        self.__head.append(head)

    def AddInclude(self, include: str) -> None:
        self.__includes.append(include)

    def Add(self, item: CItem) -> None:
        self.__items.append(item)

    def __ParseHead(self) -> str:
        items = []
        for item in self.__head:
            items.append(str(item))
        return '\n'.join(items)

    def __ParseIncludes(self) -> str:
        includes = []
        for inc in self.__includes:
            includes.append(f'#include <{inc}>')
        return '\n'.join(includes)

    def __ParseItems(self) -> str:
        items = []
        for item in self.__items:
            items.append(str(item))
        return '\n'.join(items)

    def __str__(self):
        retval = '\n'.join(self.template)
        retval = retval.replace('[HEAD]', self.__ParseHead())
        retval = retval.replace('[INC]', self.__ParseIncludes())
        retval = retval.replace('[ITEMS]', self.__ParseItems())
        return retval
