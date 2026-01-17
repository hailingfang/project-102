import sqlite3
import hashlib
import os

class Sqlite3_DB():
    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file)
    

    def disconnect(self):
        self.connect.close()


    def if_userid_used(self, userid):
        cur = self.connect.cursor()
        cur.execute("SELECT 1 FROM users WHERE userid = ? LIMIT 1", (userid,))
        res = cur.fetchone()
        cur.close()
        if res:
            return True
        else:
            return False


    def if_phone_used(self, phone):
        cur = self.connect.cursor()
        cur.execute("SELECT 1 FROM users WHERE phone = ? LIMIT 1", (phone,))
        res = cur.fetchone()
        cur.close()
        if res:
            return True
        else:
            return False


    def if_email_used(self, email):
        cur = self.connect.cursor()
        cur.execute("SELECT 1 FROM users WHERE email = ? LIMIT 1", (email,))
        res = cur.fetchone()
        cur.close()
        if res:
            return True
        else:
            return False


    def add_user(self, userid, nickname, phone, email, salt, password_hash, status=0):
        cur = self.connect.cursor()
        cur.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (userid, nickname, phone, email, salt, password_hash, status))
    
        self.connect.commit()

        if cur.rowcount == 1:
            return_v = 0
        else:
            return_v = 1
        cur.close()

        return return_v


    def get_user(self, userid):
        cur = self.connect.cursor()
        cur.execute("SELECT * FROM users WHERE userid = ? LIMIT 1", (userid, ))
        entry = cur.fetchone()
        cur.close()
        return entry
    

    def rm_user(self, userid):
        if self.if_userid_used(userid):
            cur = self.connect.cursor()
            cur.execute("DELETE FROM users WHERE userid = ?", (userid, ))
            self.connect.commit()
            cur.close()
            return 0
        else:
            return 1


    def get_all_users(self):
        cur = self.connect.cursor()
        cur.execute("SELECT userid FROM users")
        entry_s = cur.fetchall()
        return entry_s


def test():
    db = Sqlite3_DB("users.db")
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", "19921003".encode(), salt, 1000_000)
    r = db.add_user("zhaojt", "zhao", "19911321193", "zhaojt@outlook.com", salt, password_hash, 0)
    print(r)
    r = db.add_user("fanghl", "ben", "19911321192", "fanghl@outlook.com", salt, password_hash, 0)
    print(r)
    ent = db.get_user("zhaojt")
    print(ent)

if __name__ == "__main__":
    test()
