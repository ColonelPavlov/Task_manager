def get_total_users(cursor):
    cursor.execute("SELECT COUNT(*) AS total FROM users")
    return cursor.fetchone()["total"]

def get_total_tasks(cursor):
    cursor.execute("SELECT COUNT(*) AS total_tasks FROM tasks")
    return cursor.fetchone()["total_tasks"]

def get_task_priorities_by_user(cursor, username):
    cursor.execute("SELECT priority, COUNT(*) AS count_tasks FROM tasks JOIN users ON tasks.user_id = users.user_id WHERE users.username = %s GROUP BY priority", (username,))
    return cursor.fetchall()

def get_task_statuses_by_user(cursor, username):
    cursor.execute("SELECT status, COUNT(*) AS count_tasks FROM tasks JOIN users ON tasks.user_id = users.user_id WHERE users.username = %s GROUP BY status", (username,))
    return cursor.fetchall()