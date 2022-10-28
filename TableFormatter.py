import argparse
from itertools import product
from typing import List, Dict

import pyperclip as cp

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--rows', type=str, nargs='+', help='row numbers to display, eg. "-r :2 3 5:7 7 9:"')
parser.add_argument('-c', '--columns', type=str, nargs='+', help='column names to display, eg. "-c col1 \'Column Name 2\' col3"')
parser.add_argument('-cc', '--columns-combined', type=str, help='column names to display, eg. "-cc \'col1;col2\'"')
parser.add_argument('-s', '--search', nargs='+', help='values to be searched, TODO')
parser.print_help()

args = parser.parse_args()

# example: parse --rows :2 3 5:6 7 9: -> 0, 1, -, 3, -, 5, -, 7, -, 9+
if args.rows:
    newRows = {}
    for r in args.rows:
        if ':' in r:

            left = r.split(':')[0]
            if left:
                left = int(left)

            right = r.split(':')[1]
            if right:
                right = int(right)

            if not left:
                for i in range(right):
                    newRows[i] = 1
            elif not right:
                newRows['inf'] = left
                # newRows[left] = 'inf'
                # newRows['inf'] = 1
            else:
                for i in range(left, right):
                    newRows[i] = 1
        else:
            newRows[int(r)] = 1
    args.rows = newRows
# example: parse --columns-combined "Ln;Card no;Customer id" -> ['Ln', 'Card no', 'Customer id']
if args.columns_combined:
    args.columns = str(args.columns_combined).split(';')
# TODO example: parse --search 2018-01-02 {"First name": [Katarina, Luise], AnotherKey:"Another value"} Age=CHILD
# TODO example: parse --where "Age=CHILD and (First name=Katarina OR First name = Luise)"

# args.columns = ['Ln', 'Age']
# args.rows = ['0:1', '3:']
# args = parser.parse_args(['--rows', '1', '2', '--columns', 'XXX'])

print(args)


class Column:
    def __init__(self, name):
        self.name = name
        self.width = len(name)


ColumnName = str
Value = object


class Table:
    def __init__(self, columns: List[Column], rows: List[Dict[ColumnName, Value]]):
        self.columns = columns
        self.rows = rows

    def normalize(self):
        for row in self.rows:
            for col in self.columns:
                val = row[col.name]
                valWidth = len(str(val))
                col.width = max(col.width, valWidth)

    def print(self, args):
        columns = self.columns
        rows = self.rows

        if args:
            if args.columns:
                colInArgs = lambda col: col.name in args.columns
                columns = list(filter(colInArgs, columns))
            if args.rows:
                newRows = []
                inf = args.rows.get('inf', False)
                for row in rows:
                    rowNo = row['_rowNo']
                    toPrint = (inf and rowNo >= inf) or args.rows.get(rowNo, False)
                    if toPrint:
                        newRows.append(row)
                rows = newRows
            if args.search:
                pass  # TODO

        colToHorizontalDelimiter = lambda col: '-' * (col.width + 2)
        colToNameWithWidth = lambda col: ' {:{width}} '.format(col.name, width=col.width)
        rowToValueWithWidth = lambda prod: ' {:{width}} '.format(prod[1][prod[0].name], width=prod[0].width)
        # rowToValueWithWidth = lambda col, row: ' {:{width}} '.format(row[col.name], width=col.width)

        print('|'.join(map(colToNameWithWidth, columns)))
        print('+'.join(map(colToHorizontalDelimiter, columns)))

        for i, row in enumerate(rows):
            # print('|'.join(map(rowToValueWithWidth, columns, repeat(row, len(columns)))))
            print('|'.join(map(rowToValueWithWidth, list(product(columns, [row])))))
            # toPrint = not args.rows or ((inf and i >= inf) or args.rows.get(i, False))
            # if toPrint:
            #     print('|'.join(map(rowToValueWithWidth, columns, repeat(row, len(columns)))))


print('hello')

columns = []
rows = []

text = cp.paste()
lines = text.splitlines()
for i, line in enumerate(lines):
    if i == 0:
        columnCount = int(line.split('\t')[1])
    elif 'columnCount' in locals():
        if 2 <= i <= (columnCount + 1):  # [n] name=X, width=-1
            columnName = line.split(',')[0].split('=')[1]
            column = Column(columnName)
            columns.append(column)
        elif i == (columnCount + 2):  # rowCount X
            rowCount = int(line.split('\t')[1])
        elif i >= (columnCount + 4):  # [n] val1;val2;val3;...
            sIndex = line.find('[') + 1
            eIndex = line.find(']')
            rowNo = line[sIndex:eIndex]

            line = line[(eIndex + 2):]
            values = line.split(';')

            row = {'_rowNo': int(rowNo)}
            for j, val in enumerate(values):
                if j < columnCount:
                    column = columns[j]
                    row[column.name] = val
            rows.append(row)

table = Table(columns, rows)
table.normalize()
table.print(args)
