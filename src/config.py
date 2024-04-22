import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))
NAMESUBD = 'sqlite'

if NAMESUBD == 'sqlite':
    path = os.path.join(BASEDIR, "db", "reestrsi.db")
    DATABASE_URL = f'sqlite:///{path}'
