import sqlite3
import hashlib
import os

class Sqlite3_DB():
    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file)
    

    def disconnect(self):
        self.connect.close()
        self.connect = None


    def query(self, table, column_name, value, select_column_s=None):
        ent = None
        error = None

        if select_column_s:
            select_column_s = ", ".join(select_column_s)
        else:
            select_column_s = "*"

        cur = self.connect.cursor()
        try:
            cur.execute(f"SELECT {select_column_s} FROM {table} WHERE {column_name} = ?", (value,))
        except Exception as err:
            error = err
        finally:
            ent = cur.fetchall()
            cur.close()

        return error, ent


    def insert(self, table, value_s, insert_clumn_s=None):
        error = None

        if insert_clumn_s:
            insert_clumn_s = ", ".join(insert_clumn_s)
            insert_clumn_s = f"({insert_clumn_s})"
        else:
            insert_clumn_s = ""
        place_holders = ", ".join(["?"] * len(value_s))
        cur = self.connect.cursor()
        try:
            cur.execute(f"INSERT INTO {table} {insert_clumn_s} VALUES ({place_holders})", value_s)
            self.connect.commit()
        except Exception as err:
            error = err
        finally:
            cur.close()

        return error


    def delete(self, table, column_name, value):
        error = None

        cur = self.connect.cursor()
        try:
            cur.execute(f"DELETE FROM {table} WHERE {column_name} = ?", (value,))
            self.connect.commit()
        except Exception as err:
            error = err
        finally:
            cur.close()

        return error


    def update(self, table, column_name, value, update_column_s, update_value_s):
        error = None
        cur = self.connect.cursor()
        update_columns_str = [f"{ele} = ?" for ele in update_column_s]
        update_columns_str = ", ".join(update_columns_str)
        try:
            cur.execute(f"UPDATE {table} SET {update_columns_str} WHERE {column_name} = ?", update_value_s + [value])
        except Exception as err:
            error = err
        finally:
            cur.close()
        return error



def test():
    db = Sqlite3_DB("users.db")
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", "19921003".encode(), salt, 1000_000)
    r = db.add_user("zhaojt", "zhao", "19911321193", "zhaojt@outlook.com", 260119110201, salt, password_hash, 0)
    print(r)
    r = db.add_user("fanghl", "ben", "19911321192", "fanghl@outlook.com", 260119110101, salt, password_hash, 0)
    print(r)
    ent = db.get_user("zhaojt")
    print(ent)

if __name__ == "__main__":
    test()
