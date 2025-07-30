import os
from datetime import datetime
from sys import version_info, argv
from os import remove
if version_info[0] == 3 and version_info[1] <= 4:
    from scandir import scandir
else:
    from os import scandir
from os import path as os_path, sep
from platform import node
from sqlite3 import connect, OperationalError, Row
from logging import info, basicConfig, INFO, error, warning
from pathlib import Path
from conffu import Config
from shlex import split
from json import dumps

DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


# noinspection SqlResolve
class TreeWalker:
    log_freq = 1000
    lines = 0
    node = node()

    def rewrite_path(self, p):
        p = str(Path(p).resolve())
        return r'\\{}\{}${}'.format(self.node, p[0].lower(), p[2:]) \
            if self.rewrite_admin and len(p) > 1 and p[1] == ':' else p

    @staticmethod
    def _add_runs(conn, fn):
        conn.execute('CREATE TABLE IF NOT EXISTS runs (root text, start text, end text)')
        dt = datetime.strftime(datetime.fromtimestamp(os.stat(fn).st_ctime), DATE_FORMAT)
        for root in conn.execute('select name from dirs where parent_dir = -1').fetchall():
            conn.execute('INSERT INTO runs VALUES(?, ?, ?)', [root[0], dt, dt])

    def __init__(self, fn, overwrite=False, rewrite=True, rewrite_admin=True, override=False):
        existed = Path(fn).is_file()
        if existed and overwrite:
            remove(fn)

        self._fn = fn
        self._conn = connect(fn)
        self.c = self._conn.cursor()

        self.c.execute('DROP TABLE IF EXISTS old_dirs')
        self.c.execute('DROP TABLE IF EXISTS old_files')
        self.c.execute('DROP TABLE IF EXISTS old_no_access')

        self.rewrite = rewrite
        self.rewrite_admin = rewrite_admin
        self.options = ['rewrite', 'rewrite_admin']

        def set_options():
            self.c.execute('CREATE TABLE options (key text, value text)')
            for key in self.options:
                self.c.execute('INSERT INTO options VALUES(?, ?)', (key, self.__getattribute__(key)))

        def get_options():
            for key in self.options:
                value = self.c.execute('SELECT value FROM options WHERE key=?', [key]).fetchone()[0]
                option = self.__getattribute__(key)
                if value is None:
                    self.c.execute('INSERT INTO options VALUES(?, ?)', (key, option))
                else:
                    if option != type(option)(value):
                        if override:
                            self.c.execute('UPDATE options SET value = ? WHERE key = ?', (option, key))
                        error('options for database do not match, \'{}\' is {}, was {}'.format(key, option, value))

        if not existed or overwrite:
            set_options()
            self.c.execute('CREATE TABLE no_access (id int, parent_dir int, name text, problem int)')
            self.c.execute('CREATE TABLE dirs (id int, parent_dir int, name text, size int, total_file_count int, '
                           'file_count int, min_mtime int, min_atime int, max_mtime int, max_atime int)')
            self.c.execute('CREATE TABLE files (parent_dir int, name text, size int, mtime int, atime int)')
            self.c.execute('CREATE TABLE runs (root text, start text, end text)')
            self.next_dir_id = 0
        else:
            # options were added in later versions, deal with cases where there are none
            if self.c.execute(
                    'SELECT name FROM sqlite_master WHERE type="table" AND name="options"').fetchone() is None:
                set_options()
            else:
                get_options()

            # runs were added in later versions, deal with cases where there are none
            if self.c.execute(
                    'SELECT name FROM sqlite_master WHERE type="table" AND name="runs"').fetchone() is None:
                self._add_runs(self.c, fn)

            self.c.execute('SELECT MAX(id) FROM dirs')
            x = self.c.fetchone()[0]
            self.next_dir_id = 0 if x is None else x + 1

    @property
    def fn(self):
        return self._fn

    @classmethod
    def log_loop(cls, *args):
        if cls.lines % cls.log_freq == 0:
            info(*args)
        cls.lines += 1

    def _do_walk(self, path, parent_dir=-1, filter_callback=None):
        start = datetime.strftime(datetime.utcnow(), DATE_FORMAT)
        self.__class__.log_freq = 100
        dir_id = self.next_dir_id
        self.next_dir_id += 1
        self.log_loop('Processing {}, {}'.format(path, dir_id))
        total_size, min_mtime, min_atime, max_mtime, max_atime, total_count, count, size = (
            0, 10000000000, 10000000000, 0, 0, 0, 0, 0)
        try:
            for entry in scandir(path):
                if filter_callback is None or filter_callback(entry.name):
                    # inspection required due to PyCharm issue PY-46041
                    # noinspection PyUnresolvedReferences
                    if entry.is_dir(follow_symlinks=False):
                        # noinspection PyUnresolvedReferences
                        size, sub_count, mtime, atime = self._do_walk(entry.path, dir_id)
                        total_count += sub_count
                    else:
                        # noinspection PyUnresolvedReferences
                        stat = entry.stat(follow_symlinks=False)
                        size = stat.st_size
                        mtime = int(stat.st_mtime)
                        atime = int(stat.st_atime)
                        total_count += 1
                        count += 1
                        # noinspection PyUnresolvedReferences
                        self.c.execute('INSERT INTO files VALUES(?, ?, ?, ?, ?)',
                                       [dir_id, entry.name, size, mtime, atime])
                    total_size += size
                    min_mtime = min(min_mtime, mtime)
                    min_atime = min(min_atime, atime)
                    max_mtime = max(max_mtime, mtime)
                    max_atime = max(max_atime, atime)
        except (PermissionError, FileNotFoundError, OSError) as e:
            print('Error trying to process "{}": {}'.format(path, e))
            self.c.execute('INSERT INTO no_access VALUES(?, ?, ?, 0)',
                           [dir_id, parent_dir, path])

        self.c.execute('INSERT INTO dirs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       [dir_id, parent_dir, path, total_size, total_count, count, min_mtime, min_atime, max_mtime, max_atime])
        end = datetime.strftime(datetime.utcnow(), DATE_FORMAT)
        if parent_dir == -1:
            self.c.execute('INSERT INTO runs VALUES(?, ?, ?)', [path, start, end])
        return total_size, total_count, min_mtime, min_atime

    def walk(self, path, parent_dir=-1, filter_callback=None):
        if self.rewrite:
            path = self.rewrite_path(path)
        return self._do_walk(path, parent_dir, filter_callback)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.close()

    def commit(self):
        try:
            self.c.execute('COMMIT')
        except OperationalError as e:
            if not str(e).endswith('no transaction is active'):
                raise e

    def close(self):
        self._conn.close()

    def add_db(self, fn):
        def do_add(dir_id, parent_dir):
            nonlocal ca
            ca.execute('SELECT * FROM dirs WHERE id = ?', [dir_id])
            self.c.execute('INSERT INTO dirs VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                           (self.next_dir_id, parent_dir) + ca.fetchone()[2:])
            ca.execute('SELECT * FROM files WHERE parent_dir = ?', [dir_id])
            for f in ca.fetchall():
                self.c.execute('INSERT INTO files VALUES(?, ?, ?, ?, ?)',
                               (self.next_dir_id,) + f[1:])
            ca.execute('SELECT id FROM dirs WHERE parent_dir = ?', [dir_id])
            new_dir_id = self.next_dir_id
            self.next_dir_id += 1
            for d in ca.fetchall():
                do_add(d[0], new_dir_id)

        conn_add = connect(fn)
        try:
            ca = conn_add.cursor()
            ca.execute('SELECT name, id FROM dirs WHERE parent_dir = -1')
            for r in ca.fetchall():
                self.remove(r[0])
                do_add(r[1], -1)
        finally:
            conn_add.close()

    def merge(self, fn):
        with connect(fn) as conn:
            self._add_runs(conn, fn)
            self.next_dir_id = self._do_reindex(conn, offset=self.next_dir_id)

        self.c.execute('ATTACH DATABASE "{}" AS adding'.format(fn))
        self.c.execute('INSERT INTO dirs SELECT * FROM adding.dirs')
        self.c.execute('INSERT INTO files SELECT * FROM adding.files')
        self.c.execute('INSERT INTO no_access SELECT * FROM adding.no_access')
        self.c.execute('INSERT INTO runs SELECT * FROM adding.runs')
        self.c.execute('COMMIT')
        self.c.execute('DETACH DATABASE adding')

    @staticmethod
    def _do_reindex(connection, offset=0):
        cursor = connection.cursor()
        mapping = {old_key: new_key + offset for new_key, old_key in
                   enumerate(
                       t[0]
                       for t in cursor.execute(
                           'SELECT id FROM dirs ORDER BY id'
                       ).fetchall()
                   )
                   } | {-1: -1}

        cursor.execute('ALTER TABLE dirs RENAME TO old_dirs')
        cursor.execute('CREATE TABLE dirs (id int, parent_dir int, name text, size int, total_file_count int, '
                       'file_count int, min_mtime int, min_atime int, max_mtime int, max_atime int)')
        # separate cursor for reading, reusing self.c in loop
        data = connection.execute('SELECT * FROM old_dirs')
        for row in data:
            cursor.execute('INSERT INTO dirs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                           [mapping[row[0]], mapping[row[1]]] + list(row[2:]))
        cursor.execute('DROP TABLE old_dirs')

        cursor.execute('ALTER TABLE files RENAME TO old_files')
        cursor.execute('CREATE TABLE files (parent_dir int, name text, size int, mtime int, atime int)')
        # separate cursor for reading, reusing self.c in loop
        data = connection.execute('SELECT * FROM old_files')
        for row in data:
            cursor.execute('INSERT INTO files VALUES (?, ?, ?, ?, ?)',
                           [mapping[row[0]]] + list(row[1:]))
        cursor.execute('DROP TABLE old_files')

        cursor.execute('ALTER TABLE no_access RENAME TO old_no_access')
        cursor.execute('CREATE TABLE no_access (id int, parent_dir int, name text, problem int)')
        # separate cursor for reading, reusing self.c in loop
        data = connection.execute('SELECT * FROM old_no_access')
        for row in data:
            cursor.execute('INSERT INTO no_access VALUES (?, ?, ?, ?)',
                           [mapping[row[0]], mapping[row[1]]] + list(row[2:]))
        cursor.execute('DROP TABLE old_no_access')
        cursor.execute('COMMIT')

        next_id = cursor.execute('SELECT MAX(id) FROM dirs').fetchone()[0]
        return 0 if next_id is None else next_id + 1

    def reindex(self):
        self._do_reindex(self._conn)

    @staticmethod
    def _is_relative(p1, p2):
        """
        Returns if p1 is relative to p2, i.e. if p1 is either the same as p2, or a subdirectory of p2
        :param p1: path
        :param p2: path
        :return: bool, whether p1 is relative to p2
        """
        # instead of Path.is_relative_to, to ensure 3.4.4 compatibility
        rp1, rp2 = os_path.realpath(p1), os_path.realpath(p2)
        return rp1.startswith(rp2) and (len(rp1) == len(rp2) or rp1[len(rp2)] == sep)

    def remove(self, p):
        def do_remove(dir_id):
            def _query(table, key):
                self.c.execute('DELETE FROM {} '
                               'WHERE {} IN ('
                               '  WITH RECURSIVE children(dir) AS ('
                               '    SELECT ? '
                               '    UNION ALL '
                               '    SELECT dirs.id FROM dirs, children WHERE dirs.parent_dir = children.dir'
                               '  ) '
                               'SELECT dir FROM children)'.format(table, key), [dir_id])
            _query('no_access', 'parent_dir')
            _query('files', 'parent_dir')
            _query('dirs', 'id')

        if self.rewrite:
            p = self.rewrite_path(p)
        self.c.execute('SELECT name, id FROM dirs WHERE parent_dir = -1')
        for r in self.c.fetchall():
            # if a 'root' directory (i.e. without parent) falls within p, remove it (and its children)
            if self._is_relative(r[0], p):
                do_remove(r[1])
            # if p falls within a 'root' directory find that record for p and remove it (and its children)
            elif self._is_relative(p, r[0]):
                self.c.execute('SELECT id FROM dirs WHERE name = ?', [p])
                _id = self.c.fetchone()[0]
                if _id is None:
                    warning('Attempting to remove "{p}" from within "{r[0]}", but no longer in database')
                do_remove(_id)

    def update(self, p, remove_old=True):
        try:
            if self.rewrite:
                p = self.rewrite_path(p)
            if remove_old:
                self.remove(p)
            self._do_walk(p)
        except PermissionError:
            print('Permission error trying to prepare processing of: {}'.format(p))
            self.c.execute('INSERT INTO no_access VALUES(?, ?, ?, 0)', [-1, -1, p])

    def set_host(self, hostname):
        # noinspection SqlWithoutWhere
        self.c.execute(
            r'UPDATE dirs SET name = "\\" || ? || "\" || SUBSTR(name, 1, 1) || "$\" || SUBSTR(name, 4) '
            r'WHERE name LIKE "_:\%"', [hostname])

    def get_tree(self, p=None, d=None):
        if d is None:
            if p is None:
                self.c.execute('SELECT name, id FROM dirs WHERE parent_dir = -1')
                return {r[0]: self.get_tree(d=r[1]) for r in self.c.fetchall()}
            self.c.execute('SELECT id FROM dirs WHERE name = ?', [p])
            d = self.c.fetchone()[0]
        if d is None:
            return False
        self.c.execute('SELECT name, id FROM dirs WHERE parent_dir = ?', [d])
        result = {Path(r[0]).name: self.get_tree(d=r[1]) for r in self.c.fetchall()}
        self.c.execute('SELECT name FROM files WHERE parent_dir = ?', [d])
        result.update({r[0]: None for r in self.c.fetchall()})
        return result

    def _get_list(self, p, files=True):
        rf = self._conn.row_factory
        try:
            self._conn.row_factory = Row
            if self.rewrite:
                p = self.rewrite_path(p)
            self.c.execute(
                'SELECT l.name, l.size, {0} '
                'FROM {1} AS l JOIN dirs ON dirs.id = l.parent_dir '
                'WHERE dirs.name = ?'.format(('l.mtime, l.atime' if files else 'l.min_mtime, l.max_mtime, l.min_atime, l.max_atime'), ('files' if files else 'dirs')), [p])
            return self.c.fetchall()
        finally:
            self._conn.row_factory = rf

    def get_files(self, p):
        return self._get_list(p, True)

    def get_dirs(self, p):
        return self._get_list(p, False)


def run_query(cfg):
    try:
        from treewalker import nice_size
    except ImportError:
        from _nice_size import nice_size

    if not Path(cfg['database']).is_file():
        error('Database to query {} not found.'.format(cfg['database']))
        exit(1)

    sql = ''
    order = 'DESC'
    order_by = 'size'
    if cfg['query_sql']:
        if not Path(cfg['query_sql']).is_file():
            error('Query file "{}" not found.'.format(cfg['query_sql']))
            exit(1)
        with open(cfg['query_sql']) as f:
            sql = f.read()
    elif cfg['query_cli']:
        if isinstance(cfg['query_cli'], list):
            error('The query passed to --query_cli must be enclosed double quotes.')
            exit(1)
        sql = str(cfg['query_cli'])
    elif cfg['query_file'] or cfg['query_dir']:
        q = cfg['query_file'] if 'query_file' in cfg else cfg['query_dir']
        if not isinstance(q, list):
            if not isinstance(q, str):
                if q is not True:
                    error('You must provide some expression for your query: {}'.format(q))
                    print_query_help()
                    exit(1)
                else:
                    # just the default sort order
                    q = ['s_desc']
            else:
                q = split(q)

        target = 'files' if cfg['query_file'] else 'dirs'

        if q[-1].lower() in ['a_desc', 'a_asc', 's_desc', 's_asc']:
            order = q[-1][2:].upper()
            order_by = 'size' if q[-1][0].lower() == 's' else 'name'
            del(q[-1])

        item, location = (q[:q.index('in')], q[q.index('in')+1:]) if 'in' in q else (q, [])

        item_conditions = ' OR '.join('{}.name LIKE "%{}%"'.format(target, keyword) for keyword in item)

        if location:
            location_condition = ' {}.parent_dir IN (SELECT id FROM dirs WHERE {})'.format(
                target, ' OR '.join('name LIKE "%{}%"'.format(keyword) for keyword in location)
            )
            conditions = '({}) AND {}'.format(item_conditions, location_condition) \
                if item_conditions else location_condition
        else:
            conditions = item_conditions

        conditions = 'WHERE {}'.format(conditions) if conditions else conditions
        if target == 'files':
            sql = 'SELECT {0}.size, {0}.name, parent_dirs.name as location ' \
                  'FROM {0} JOIN dirs AS parent_dirs ON parent_dirs.id = {0}.parent_dir {1}'.format(target, conditions)
        else:
            sql = 'SELECT {0}.size, {0}.name FROM {0} {1}'.format(target, conditions)

        sql = '{} ORDER BY {}.{} {}'.format(sql, target, order_by, order)

    limited_sql = '{} LIMIT {}'.format(sql, cfg['query_limit'])

    csv = cfg['query_output'] in ['csv', 'txt']
    txt = cfg['query_output'] == 'txt'
    json = not csv

    con = connect(cfg['database'])
    if json:
        con.row_factory = Row
    cur = con.cursor()
    first_row = True
    nice_pos = []

    try:
        try:
            cur = cur.execute(limited_sql)
        except OperationalError as e:
            if str(e).startswith('near "LIMIT"'):
                warning('Ignoring LIMIT from treewalker, as provided script already includes a LIMIT.')
                cur = cur.execute(sql)
            else:
                raise e
    except OperationalError as e:
        print('Operational query error: {}'.format(e))
        exit(1)
    n = 0

    bin_nice = 'si' not in cfg['query_nice']
    try:
        dp_nice = int(cfg['query_nice'][0])
    except ValueError:
        try:
            dp_nice = int(cfg['query_nice'][1])
        except ValueError:
            # default precision
            dp_nice = 1

    while True:
        row = cur.fetchone()
        if row is None:
            break
        n += 1
        if first_row:
            header = [col[0] for col in cur.description]
            nice_pos = [i for i, f in enumerate(header) if f.startswith('nice_')]
            if csv:
                print(','.join(header))
            first_row = False
        if csv:
            if nice_pos:
                row = (x if i not in nice_pos else nice_size(x, not bin_nice, dp_nice) for i, x in enumerate(row))
            print(','.join(str(x) for x in row))
        elif json:
            if nice_pos:
                row = {
                    k: x if i not in nice_pos else nice_size(x, not bin_nice, dp_nice)
                    for i, (k, x) in enumerate(dict(row).items())
                }
            else:
                row = dict(row)
            print(dumps(row))

    if txt:
        print('\nTotal rows: {}'.format(n))
        if n == cfg['query_limit']:
            print('Query limit reached, there may be more rows in the database')


def print_query_help():
    from ._version import __version__
    print(
        '\nTreewalker '+__version__+' - Query help\n'
        '\n'
        'Examples:\n'
        '\n'
        'Show this help text:\n'
        '   treewalker -qh\n'
        'Run the sql query in test.sql and write the result to stdout as JSON:\n'
        '   treewalker -db my_files.sqlite -qs test.sql -qo json\n'
        'Run a SQL query directly, to select root folders:\n'
        '   treewalker -db my_files.sqlite -qc "SELECT * FROM dirs WHERE parent_dir = 0"\n'
        'Files that have ".txt" or ".csv" in their name in a dir with "temp dir":\n'
        '   treewalker -db my_files.sqlite -qf .txt .csv in "temp dir" s_desc\n'
        'Dirs that have "image" in their name inside a dir with "-temp" or ".bak":\n'
        '   treewalker -db my_files.sqlite -qd "image in -temp .bak asc"\n'
        '   (to be able to use switch characters like "-" or "/", quotes are needed)\n'
        'The 10 largest files in the database with SI-type sizes with precision 2:\n'
        '   treewalker -db my_files.sqlite -qf s_desc -ql 10 -qn si 2\n'
        '\n'
        'Note that "a_asc", "a_desc", "s_asc" and "s_desc" at the end of a -qd or -qf\n'
        'expression are modifiers for sorting, alphanumeric or size (default s_desc).\n'
        '\n'
        'If you mix these options, only one will get executed; order of preference:\n'
        '   -qh, -qs, -qc, -qf, -qd (i.e. as shown above)\n\n'
    )


def print_help():
    from ._version import __version__
    print(
        '\nTreewalker '+__version__+'\n'
        '\nTreewalker traverses a directory tree from a starting path, adding files and\n'
        'folders to a SQLite3 database.\n'
        '\n'
        'Use: `treewalker [options] --db filename --walk path(s) | --merge filename\n'
        '\n'
        'Options:\n'
        '-h/--help                     : This text.\n'
        '-db/--database filename       : SQLite3 database to work on. (required)\n'
        '-w/--walk path [path [..]]    : Path(s) to `walk` and add to the database.\n'
        '-m/--merge path [path [..]]   : Path to additional database(s) to merge.\n'
        '-rm/--remove path [path [..]] : Path(s) to recursively remove from database.\n'
        '-ow/--overwrite               : Overwrite (wipe) the database (or add to it).\n'
        '                                (default False/append)\n'
        '-qd/--query_dir expression    : Run a quick query for dirs in the DB.\n'
        '-qf/--query_file expression   : Run a quick query for files in the DB.\n'
        '-qh/--query_help              : Show additional help on quick query syntax.\n'
        '-ql/--query_limit n           : Maximum #rows from a query (default 1,000).\n'
        '-qn/--query_nice [si|bin] n   : Output nice size as SI or binary, with \n'
        '                                precision n (default bin 1).\n'
        '-qo/--query_output type       : Specify how to output query results. Either:\n'
        '                                csv, txt (default, csv with info), or json.\n'
        '-qc/--query_cli query         : Run a SQLite query from the CLI against the DB.\n'
        '-qs/--query_sql path          : Run a SQLite query from file against the DB.\n'
        '-rw/--rewrite                 : Rewrite paths to resolved paths. (default True,\n'
        '                                set to False or 0 to change)\n'
        '-ra/--rewrite_admin           : Rewrite local drive letters to administrative\n'
        '                                shares. (default True)\n'
        '-sh/--set_host hostname       : Set all records with local drive letters to\n'
        '                                administrative shares for hostname\n'
        '                                (--walk/--merge/--remove/--set_host required)\n'
        '\n'
        'Examples:\n'
        '\n'
        'Create a new database with the structure and contents of two temp directories:\n'
        '   treewalker --overwrite --db temp.sqlite --walk c:/temp d:/temp e:/temp\n'
        'Remove a subset of files already in a database:\n'
        '   treewalker --remove d:/temp/secret --db temp_files.sqlite\n'
        'Add previously generated files to the database:\n'
        '   treewalker --merge other_tmp_files.sqlite --db temp_files.sqlite\n'
        'Run treewalker with options from a .json configuration file:\n'
        '   treewalker -cfg options.json\n\n'
    )


def cli_entry_point():
    basicConfig(level=INFO)

    cfg = Config.startup(
        defaults={'merge': [], 'overwrite': False, 'remove': [], 'walk': [],
                  'rewrite': True, 'rewrite_admin': True, 'query_limit': 1000, 'query_output': 'txt',
                  'query_nice': ['bin', '1']},
        aliases={'db': 'database', 'w': 'walk', 'm': 'merge', 'p': 'walk', 'path': 'walk',
                 'ow': 'overwrite', 'rm': 'remove', 'h': 'help', '?': 'help',
                 'rw': 'rewrite', 'ra': 'rewrite_admin', 'sh': 'set_host',
                 'qo': 'query_output', 'qh': 'query_help', 'ql': 'query_limit',
                 'qd': 'query_dir', 'qf': 'query_file',
                 'qc': 'query_cli', 'qs': 'query_sql', 'qn': 'query_nice'},
        no_key_error=True
    )

    if cfg.get_as_type('help', bool, False):
        print_help()
        exit(0)

    if cfg.get_as_type('query_help', bool, False):
        print_query_help()
        exit(0)

    overwrite = cfg.get_as_type('overwrite', bool, False)

    if any(a in ('-p', '/p', '--p', '-path', '/path', '--path') for a in argv):
        warning('Using -p or --path is deprecated, and will be removed for 2.x, please use -w or --walk instead.')

    if 'database' not in cfg:
        error('Provide "database" in configuration file, or on the command line as "--database <some filename>"')
        print_help()
        exit(1)

    if cfg.merge:
        fns = cfg.merge
        if not isinstance(fns, list):
            fns = [fns]
        for fn in fns:
            if not Path(fn).is_file():
                error('File to merge not found: {}'.format(fn))
                exit(2)
        for fn in fns:
            if cfg['set_host'] is not None:
                with TreeWalker(fn, overwrite=False) as tree_walker:
                    tree_walker.set_host(cfg.set_host)
            info('Merging "{}" into "{}" (not processing further options)'.format(fn, cfg.database))
            with TreeWalker(cfg.database, overwrite=overwrite) as tree_walker:
                tree_walker.merge(fn)
        exit(0)

    if cfg['set_host']:
        with TreeWalker(cfg.database, overwrite=overwrite) as tree_walker:
            tree_walker.set_host(cfg.set_host)

    if cfg['reindex']:
        print('Reindexing {}...'.format(cfg.database))
        with TreeWalker(cfg.database, overwrite=overwrite) as tree_walker:
            tree_walker.reindex()
        exit(0)

    cfg['query_output'] = cfg['query_output'].lower()
    if cfg['query_output'] not in ['csv', 'json', 'txt']:
        error('Unsupported value for --query_output: {}'.format(cfg['query_output']))
        exit(1)

    if cfg['query_dir'] or cfg['query_file'] or cfg['query_cli'] or cfg['query_sql']:
        run_query(cfg)
        exit(0)

    if not isinstance(cfg['query_nice'], list):
        cfg['query_nice'] = [cfg['query_nice']]

    if cfg['walk']:
        if not isinstance(cfg.walk, list):
            cfg.walk = [cfg.walk]
    else:
        cfg['walk'] = []
    if isinstance(cfg.database, list):
        cfg.walk.extend(cfg.database[1:])
        cfg.database = cfg.database[0]

    with TreeWalker(cfg.database, overwrite=overwrite,
                    rewrite=cfg.get_as_type('rewrite', bool, True),
                    rewrite_admin=cfg.get_as_type('rewrite_admin', bool, True)) as tree_walker:
        paths = cfg.walk + cfg.arguments[''][2:]

        for path in paths:
            tree_walker.update(path)

        if cfg.remove is not None:
            if not isinstance(cfg.remove, list):
                cfg.remove = [cfg.remove]
            for path in cfg.remove:
                if cfg.get_as_type('rewrite', bool, True):
                    path = tree_walker.rewrite_path(path)
                tree_walker.remove(path)


if __name__ == '__main__':
    cli_entry_point()
