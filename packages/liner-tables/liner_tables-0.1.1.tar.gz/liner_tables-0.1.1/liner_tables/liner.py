class Table:
    def __init__(self, headers):
        self.headers = headers
        self.data = []

    def add(self, row):
        self.data.append(row)

    def remove(self, condition):
        if isinstance(condition, int):
            if 1 <= condition <= len(self.data):
                del self.data[condition - 1]
        elif isinstance(condition, dict):
            key = next(iter(condition))
            value = condition[key]
            if key not in self.headers:
                raise Exception(f"Column '{key}' is not valid.")
            key_idx = self.headers.index(key)

            for i, row in enumerate(self.data):
                if str(row[key_idx]) == str(value):
                    del self.data[i]
                    break

    def render(self):
        rows = [self.headers] + self.data
        col_widths = [max(len(str(row[i])) for row in rows) + 2 for i in range(len(self.headers))]

        def format_row(index, row):
            if index is not None:
                row_num = f"{index}.".ljust(3)
            else:
                row_num = " # ".ljust(3)
            row_str = "│".join(f" {str(row[i]).ljust(col_widths[i] - 1)}" for i in range(len(row)))
            return f"{row_num}│{row_str}│"

        def separator():
            return "───┼" + "┼".join("─" * col_widths[i] for i in range(len(col_widths))) + "┼"

        output = format_row(None, self.headers) + '\n'
        output += separator() + '\n'
        for i, row in enumerate(self.data, start=1):
            output += format_row(i, row) + '\n'

        return output


def create(headers, data):
    t = Table(headers)
    t.add(data)
    return t


def remove(table, condition):
    table.remove(condition)
    return table
