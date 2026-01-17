import sqlite3
import argparse
import sys


def getargs(args):
    parser = argparse.ArgumentParser(description="Manage Sqlite Database")
    #for list subcommand
    parser.add_argument("-a", help="list all users")
    parser.add_argument("userid", help="userid that be listed")
    #for create subcommand
    parser.add_argument("dbname", help="database name")
    
    subcommand = args[1]
    args = args[1:]
    if subcommand == "list":
        args = parser.parse_args(args)
        return subcommand, (args.a, args.userid)
    elif subcommand == "create":
        args = parser.parse_args(args)
        return subcommand, (args.dbname)
    else:
        return None, None


def create_db():
    db = sqlite3.connect("users.db")
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users 
        (userid TEXT RPIMARY KEY,
        nickname TEXT,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        key BLOB NOT NULL,
        password_hash BLOB NOT NULL,
        status INTEGER)""")

    db.commit()
    db.close()


def list_users():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT userid FROM users")
    ent = cur.fetchall()
    print(ent)


def main():
    if sys.argv[1] == "create":
        create_db()
    elif sys.argv[1] == "list":
        list_users()

if __name__ == "__main__":
    main()
