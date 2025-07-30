# liner_tables

**`liner_tables`** is a lightweight Python module for creating and manipulating clean, printable text tables in the terminal. Ideal for CLI tools, debugging, or simple tabular reports.

---

## 🔧 Features

- Easily create and add rows to a table
- Remove rows by index or column value
- Print a clean, aligned text-based table to the terminal
- Doesn't require a module

---

## 📦 Installation

If using locally, just save `liner_tables.py` in your project directory.

```bash
pip install liner_tables
```

---

## Code example:
```python
import liner_tables as table

headers = ['Name', 'From']
data = ['John', 'US']

# Create first table
t = table.create(headers, data)

# To add another data
t.add(['Mike', 'CAD'])

# Delete from column value
t = table.remove(t, {'From': 'CAD'})

# Print the results
print(t.render())
```

## Output:
``` bash
 # │ Name │ From │
───┼──────┼──────┼
1. │ John │ US   │
```
