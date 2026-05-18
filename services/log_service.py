from database.db import execute_query


def log(user_id: int, action: str, details: str = ""):
    try:
        execute_query(
            "INSERT INTO event_logs (user_id, action, details) VALUES (%s,%s,%s)",
            (user_id, action, details),
        )
    except Exception:
        pass  # логирование не должно ломать основной поток


def get_logs(limit: int = 300):
    return execute_query(
        """SELECT el.id, el.created_at, u.full_name, u.role,
                  el.action, el.details
           FROM event_logs el
           LEFT JOIN users u ON u.id = el.user_id
           ORDER BY el.created_at DESC LIMIT %s""",
        (limit,), fetch=True,
    )
