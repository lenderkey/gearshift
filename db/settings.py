#
#   db/settings.py
#
#   David Janes
#   Gearshift
#   2023-09-15
#
#   Database operations
#

from Context import Context

def settings_put(key:str, value:str) -> None:
    cursor = Context.instance.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))

def settings_get(key:str, default:str=None) -> str:
    cursor = Context.instance.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))

    row = cursor.fetchone()
    if row is None:
        return default

    return row[0]

def settings_delete(key:str) -> None:
    cursor = Context.instance.cursor()
    cursor.execute("DELETE FROM settings WHERE key = ?", (key,))

def settings() -> dict:
    cursor = Context.instance.cursor()
    cursor.execute("SELECT key, value FROM settings")

    return {
        row[0]: row[1]
        for row in cursor.fetchall()
    }
