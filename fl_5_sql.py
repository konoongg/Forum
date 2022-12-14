import sqlite3

conn = sqlite3.connect('fl5.db')
cursor = conn.cursor()

users  = '''CREATE TABLE IF NOT EXISTS users (user_id INTEGER NOT NULL,
                                              login TEXT NOT NULL,
                                              password STRING NOT NULL,
                                              mail STRING NOT NULL,
                                              PRIMARY KEY(user_id),
                                              UNIQUE(login,password,user_id)) '''
cursor.execute(users)

pst = '''CREATE TABLE IF NOT EXISTS pst (pst_id INTEGER NOT NULL,
                                              autor TEXT NOT NULL,
                                              title STRING NOT NULL,
                                              intro TEXT NOT NULL,
                                              text TEXT NOT NULL,
                                              date DATE NOT NULL,
                                              PRIMARY KEY(pst_id),
                                              UNIQUE(pst_id),
                                              FOREIGN KEY (autor) references users(login))'''
cursor.execute(pst)

com  = '''CREATE TABLE IF NOT EXISTS com (c_id INTEGER NOT NULL,
                                            p_id INTEGER NOT NULL,
                                            autor TEXT NOT NULL,
                                            text TEXT NOT NULL,
                                            date DATE NOT NULL,
                                            FOREIGN KEY (p_id) references pst(pst_id),
                                            FOREIGN KEY (autor) references users(login),
                                            PRIMARY KEY(c_id),
                                            UNIQUE(c_id))'''
cursor.execute(com)

