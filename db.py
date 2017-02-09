# Database abstraction class
import yaml
import sqlite

class Db():
    
    config = yaml.safe_load(open('config/config.yaml'))

    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(config['database']['sqlite']['database'])
            db.row_factory = sqlite3.Row
        return db

    def db_query(self, query, args=(), one=False):
        cur = self.get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

    def db_execute(self, query, args=()):
        cur = self.get_db().execute(query, args)
        get_db().commit()
        lastid = cur.lastrowid
        cur.close()
        return lastid