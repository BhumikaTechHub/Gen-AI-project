import sqlite3

DB_NAME = "pitchdeck.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS slides(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER,
        slide_no INTEGER,
        score INTEGER,
        feedback TEXT,
        rewrite TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_report(filename):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO reports(filename) VALUES(?)",
        (filename,)
    )

    report_id = cur.lastrowid

    conn.commit()
    conn.close()

    return report_id


def save_slide(report_id, slide_no, score, feedback, rewrite):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO slides(
        report_id,
        slide_no,
        score,
        feedback,
        rewrite
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        report_id,
        slide_no,
        score,
        feedback,
        rewrite
    ))

    conn.commit()
    conn.close()


def get_reports():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    SELECT id, filename, upload_time
    FROM reports
    ORDER BY id DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return rows