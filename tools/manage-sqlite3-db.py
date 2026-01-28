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


def create_users_db():
    db = sqlite3.connect("users.db")
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS user_identity (
        userid TEXT RPIMARY KEY,
        nickname TEXT,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        register_time INTEGER NOT NULL,
        salt BLOB NOT NULL,
        password_hash BLOB NOT NULL,
        status INTEGER NOT NULL)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS user_basic_info (
                userid TEXT PRIMARY KEY,
                avatar TEXT,
                birthday INTEGER,
                height INTEGER,
                weight INTEGER,
                hometown TEXT,
                current_city TEXT)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS user_education (
                userid TEXT,
                education_level TEXT,
                school_name TEXT,
                school_start_date INTEGER,
                school_end_date INTEGER)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS user_occupation (
                userid TEXT PRIMARY KEY,
                job_type TEXT,
                income_level TEXT)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS user_photo (
                userid TEXT PRIMARY KEY,
                p1 TEXT,
                p2 TEXT,
                p3 TEXT,
                p4 TEXT,
                p5 TEXT,
                p6 TEXT,
                p7 TEXT,
                p8 TEXT,
                p9 TEXT)""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS user_words (
                userid TEXT PRIMARY KEY,
                words TEXT)""")

    db.commit()
    cur.close()
    db.close()


def create_log_db():
    db = sqlite3.connect("log.db")
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS login_logout_log (
                userid TEXT,
                action TEXT,
                action_time INTEGER,
                action_result INTEGER)""")

    db.commit()
    cur.close()
    db.close()


def create_session_db():
    db = sqlite3.connect("session.db")
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS live_session (
                session_id TEXT PRIMARY KEY,
                userid TEXT,
                expire_time INTEGER)""")

    db.commit()
    cur.close()
    db.close()


def list_users():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT userid FROM users")
    ent = cur.fetchall()
    print(ent)


def main():
    if sys.argv[1] == "create-usersdb":
        create_users_db()
    elif sys.argv[1] == "create-logdb":
        create_log_db()
    elif sys.argv[1] == "create-sessiondb":
        create_session_db()
    elif sys.argv[1] == "list":
        list_users()

if __name__ == "__main__":
    main()
