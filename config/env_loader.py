"""Minimal .env file loader (no external dependencies).

Reads KEY=VALUE lines and puts them into os.environ without overriding
variables that are already set in the environment.
"""

import os


def load_dotenv(path, environ=None):
    """Parse a .env file into os.environ.

    - Blank lines and lines starting with # are ignored.
    - Supports optional `export ` prefix.
    - Strips surrounding single or double quotes from values.
    - Existing environment variables take precedence over file values.

    Returns the number of variables actually set.
    """
    if environ is None:
        environ = os.environ
    path = str(path)
    if not os.path.isfile(path):
        return 0

    set_count = 0
    with open(path, encoding='utf-8') as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            line = line.removeprefix('export ')
            if '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if key and key not in environ:
                environ[key] = value
                set_count += 1
    return set_count
