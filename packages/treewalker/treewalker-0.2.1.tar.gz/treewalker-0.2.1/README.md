# Treewalker

A simple package to walk a directory tree and collect files and sizes into a SQLite DB.

## Usage

For simple (and most) use cases, simply install the package from PyPI:
```commandline
pip install treewalker
```
And run it from the command line:
```commandline
treewalker --help
treewalker --db test.sqlite --walk C:/temp
```
This is the preferred and recommended way to run Treewalker.

## Usage and development

Get started (change directory to where you want the project first):
```commandline
pip install treewalker
```

Run the script with your own .json configuration:
```commandline
python treewalker.py --cfg my_config.json
```

```my_config.json
{
    "database": "test.sqlite",
    "walk": "c:/temp"
}
```

Or run the script entirely from the command line:
```commandline
python treewalker.py --db test.sqlite --walk c:\temp
```

Or build a single file executable if you need this to run on Windows systems that won't have Python pre-installed:
```commandline
scripts/build_pyinstaller.bat c:/target/folder
scripts/build_pyinstaller_xp.bat c:/target/folder

```
This creates a `treewalker.exe`, which can be run 'anywhere':
```commandline
.\treewalker.exe --db test.sqlite --walk c:\temp
```

Note that the executable will be limited to running on systems that support the version of Python you're using to build it. I.e. for Windows XP (32-bit or 64-bit), the very latest version of Python you can use is 3.4.4.

## Getting at the data

You can easily access the contents of any of the sqlite files:
```python
from sqlite3 import connect

conn = connect('test.sqlite')
c = conn.cursor()
# show all the root directories
print(c.execute('SELECT * FROM dirs WHERE parent_dir<0').fetchall())
# show all files that have "test" in their name (case-insensitive)
print(c.execute('SELECT * FROM files WHERE name LIKE "%test%"').fetchall())
```
Look at the documentation of the Python standard sqlite3 library for more examples. https://docs.python.org/3/library/sqlite3.html and at the documentation of Treewalker at https://treewalker.readthedocs.io