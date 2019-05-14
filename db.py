import sqlite3
from time import *
import datetime


def spph(elem):
    h = 0
    for i in elem:
        h += ord(i) * len(elem)**2
    return h


class DB:
    def __init__(self, type):
        d = {'users': 'users.db', 'tasks': 'tasks.db', 'orders': 'orders.db'}
        conn = sqlite3.connect(d[type], check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128),
                             mail VARCHAR(128),
                             is_admin VARCHAR(10)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash, mail, is_admin=False):
        cursor = self.connection.cursor()
        password_hash = spph(password_hash)
        cursor.execute('''INSERT INTO users
                          (user_name, password_hash, mail, is_admin)
                          VALUES (?,?,?,?)''', (user_name, password_hash, mail,
                                                str(is_admin)))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        password_hash = spph(password_hash)
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0], row[3]) if row else (False,)


class TasksModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             title VARCHAR(50),
                             description VARCHAR(512),
                             date INTEGER,
                             creator_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, description, creator_id):
        cursor = self.connection.cursor()
        cursor.execute(
                        '''INSERT INTO tasks
                           (title, description, date, creator_id)
                           VALUES (?,?,?,?,?)''', (title, description, time(),
                                                   creator_id)
                      )
        cursor.close()
        self.connection.commit()

    def get(self, id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (int(id), ))
        task = cursor.fetchone()
        return task

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        return tasks

    def delete(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (goods_id,))
        cursor.close()
        self.connection.commit()
