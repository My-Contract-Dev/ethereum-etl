# MIT License
#
# Copyright (c) 2020 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import collections

from clickhouse_driver import dbapi

from blockchainetl.jobs.exporters.converters.composite_item_converter import CompositeItemConverter


class ClickhouseItemExporter:

    def __init__(self, connection_url, item_type_to_insert_stmt_mapping, converters=(), print_sql=True):
        self.connection_url = connection_url
        self.item_type_to_insert_stmt_mapping = item_type_to_insert_stmt_mapping
        self.converter = CompositeItemConverter(converters)
        self.print_sql = print_sql

    def open(self):
        pass

    def export_items(self, items):
        items_grouped_by_type = group_by_item_type(items)

        for item_type, insert_stmt in self.item_type_to_insert_stmt_mapping.items():
            item_group = items_grouped_by_type.get(item_type)
            if item_group:
                connection = self.connect()
                cursor = connection.cursor()
                cursor.set_types_check(True)
                converted_items = list(self.convert_items(item_group))
                cursor.execute(insert_stmt, converted_items)
                connection.commit()
                connection.close()

    def convert_items(self, items):
        for item in items:
            yield self.converter.convert_item(item)

    def connect(self):
        return dbapi.connect(self.connection_url)

    def close(self):
        pass


def group_by_item_type(items):
    result = collections.defaultdict(list)
    for item in items:
        result[item.get('type')].append(item)

    return result
