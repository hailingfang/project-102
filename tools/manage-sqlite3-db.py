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
        user_id_db TEXT RPIMARY KEY,
        status TEXT NOT NULL DEFAULT 'active',
        created_at INTEGER NOT NULL,
        updated_at INTEGER,
        deleted_at INTEGER)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS user_credentials (
        user_id_db TEXT RPIMARY KEY,
        email TEXT UNIQUE,
        email_verified INTEGER NOT NULL DEFAULT 0,
        phone TEXT UNIQUE,
        phone_verified INTEGER NOT NULL DEFAULT 0,
        password_algo TEXT NOT NULL,
        password_salt BLOB NOT NULL,
        password_hash BLOB NOT NULL,
        created_at INTEGER NOT NULL,
        updated_at INTEGER,
        FOREIGN KEY (user_id_db) REFERENCES user_identity(user_id_db))""")

    cur.execute("""CREATE TABLE IF NOT EXISTS user_profile (
        user_id_db TEXT PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        user_id_changed_at INTEGER,
        nickname TEXT NOT NULL,
        avatar_id TEXT,
        gender TEXT,
        birth_date INTEGER,
        city TEXT,
        bio TEXT,
        words TEXT,
        created_at INTEGER NOT NULL,
        updated_at INTEGER,
        FOREIGN KEY (user_id_db) REFERENCES user_identity(user_id_db))""")

    cur.execute("""CREATE TABLE IF NOT EXISTS user_attributes (
        user_id_db TEXT PRIMARY KEY,
        hieght_cm INTEGER,
        weight_kg INTEGER,
        hometown TEXT,
        education_level TEXT,
        ocupation TEXT,
        income_level TEXT,
        updated_at INTEGER,
        FOREIGN KEY (user_id_db) REFERENCES user_identity(user_id_db))""")

    cur.execute("""CREATE TABLE IF NOT EXISTS user_media (
        media_id TEXT PRIMARY KEY,
        user_id_db TEXT NOT NULL,
        media_type TEXT NOT NULL,
        storage_key TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        FOREIGN KEY (user_id_db) REFERENCES user_identity(user_id_db))""")
    
    db.commit()
    cur.close()
    db.close()


def create_sessions_db():
    db = sqlite3.connect("sessions.db")
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS user_session (
        session_id TEXT PRIMARY KEY,
        user_id_db TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL,
        ip_hash TEXT,
        user_agent TEXT)""")

    db.commit()
    cur.close()
    db.close()


def create_logs_db():
    db = sqlite3.connect("logs.db")
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS auth_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id_db TEXT,
        action TEXT NOT NULL,
        action_result TEXT,
        created_at INTEGER NOT NULL,
        metadata TEXT)""")

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
    elif sys.argv[1] == "create-logsdb":
        create_logs_db()
    elif sys.argv[1] == "create-sessionsdb":
        create_sessions_db()
    elif sys.argv[1] == "list":
        list_users()

if __name__ == "__main__":
    main()
