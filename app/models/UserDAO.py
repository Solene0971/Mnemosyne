import sqlite3
import os
import bcrypt
from app.models.User import User
from app.models.UserDAOInterface import UserDAOInterface
from flask import current_app

class UserSqliteDAO(UserDAOInterface):
    """
    User data access object dédié à SQLite
    """

    def __init__(self):
        # On pointe vers le dossier instance/database.db
        # Si on est dans le contexte flask, on utilise current_app, sinon un chemin relatif par défaut
        if current_app:
             self.databasename = os.path.join(current_app.instance_path, 'database.db')
        else:
             # Fallback si appelé hors contexte (rare avec le factory pattern)
             self.databasename = os.path.join('instance', 'database.db')
        
        self._initTable()

    def _getDbConnection(self):
        conn = sqlite3.connect(self.databasename)
        conn.row_factory = sqlite3.Row
        return conn

    def _initTable(self):
        conn = self._getDbConnection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        ''')
        conn.commit()
        conn.close()
    
    def _generatePwdHash(self, password):
        password_bytes = password.encode('utf-8')
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        password_hash = hashed_bytes.decode('utf-8')
        return password_hash

    def verifyMDP(self,username, password):
        conn = self._getDbConnection()
        try:
            user = conn.execute("SELECT * FROM admin WHERE username = ?;",(username,)).fetchone()
        except sqlite3.OperationalError:
            return None
        finally:
            conn.close()
        
        if user:
            password_bytes = password.encode('utf-8')
            stored_hash_bytes = user["password"].encode('utf-8')
            
            if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                return User(user)
                
        return None
    
    def addUser(self, username, password):
        conn = self._getDbConnection()
        hached_pwd = self._generatePwdHash(password)
        try:
            conn.execute("insert into admin (username,password) values (?,?)", (username,hached_pwd,))
            conn.commit()
        except sqlite3.OperationalError:
            return None
        finally:
            conn.close()
        return None
    
    def suppUser(self,username):
        conn = self._getDbConnection()
        try:
            conn.execute("delete from admin where username = ?",(username,))
            conn.commit()
        except sqlite3.OperationalError:
            return None
        finally:
            conn.close()
        return None
    
    def getAllUser(self):
        conn = self._getDbConnection()
        try:
            users = conn.execute('select * from admin').fetchall()
        except sqlite3.OperationalError:
            return None
        finally:
            conn.close()

        if users:
            return [User(user_data) for user_data in users]
        return None
        
    
    def change_mdp(self,username, mdp):
        mdphashed = self._generatePwdHash(mdp)
        conn = self._getDbConnection()
        conn.execute("update admin set password = ? where username = ?;",(mdphashed,username,))
        conn.commit()
        conn.close()
        user = self.verifyMDP(username,mdp)
        if user :
            return True 
        return False 
        