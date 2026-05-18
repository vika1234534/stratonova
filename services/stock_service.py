from database.db import execute_query


# ── Поступления ──────────────────────────────────────────────

def add_receipt(material_id: int, quantity: int, price: float,
                supplier: str, document_number: str, note: str, user_id: int) -> int:
    rid = execute_query(
        """INSERT INTO receipts
           (material_id,quantity,price,supplier,document_number,note,user_id)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (material_id, quantity, price, supplier, document_number, note, user_id),
    )
    execute_query(
        "UPDATE materials SET quantity=quantity+%s WHERE id=%s",
        (quantity, material_id),
    )
    return rid


def get_receipts(limit=300):
    return execute_query(
        """SELECT r.id, r.created_at, m.name AS material, u.name AS unit,
                  r.quantity, r.price,
                  ROUND(r.quantity*r.price,2) AS total,
                  r.supplier, r.document_number, r.note,
                  us.full_name AS created_by
           FROM receipts r
           JOIN materials m ON m.id=r.material_id
           JOIN units     u ON u.id=m.unit_id
           JOIN users    us ON us.id=r.user_id
           ORDER BY r.created_at DESC LIMIT %s""",
        (limit,), fetch=True,
    )


def get_receipt_by_id(rid: int):
    rows = execute_query(
        """SELECT r.*,m.name AS material,u.name AS unit,us.full_name AS created_by
           FROM receipts r
           JOIN materials m ON m.id=r.material_id
           JOIN units     u ON u.id=m.unit_id
           JOIN users    us ON us.id=r.user_id
           WHERE r.id=%s""",
        (rid,), fetch=True,
    )
    return rows[0] if rows else None


# ── Списания ─────────────────────────────────────────────────

def add_writeoff(material_id: int, quantity: int,
                 reason: str, document_number: str, note: str, user_id: int) -> int:
    rows = execute_query(
        "SELECT quantity,name FROM materials WHERE id=%s", (material_id,), fetch=True
    )
    if not rows:
        raise ValueError("Материал не найден")
    mat = rows[0]
    if int(mat["quantity"]) < quantity:
        raise ValueError(
            f"Недостаточно остатка.\n"
            f"Доступно: {mat['quantity']}, списывается: {quantity}"
        )
    wid = execute_query(
        """INSERT INTO writeoffs
           (material_id,quantity,reason,document_number,note,user_id)
           VALUES (%s,%s,%s,%s,%s,%s)""",
        (material_id, quantity, reason, document_number, note, user_id),
    )
    execute_query(
        "UPDATE materials SET quantity=quantity-%s WHERE id=%s",
        (quantity, material_id),
    )
    return wid


def get_writeoffs(limit=300):
    return execute_query(
        """SELECT w.id, w.created_at, m.name AS material, u.name AS unit,
                  w.quantity, w.reason, w.document_number, w.note,
                  us.full_name AS created_by
           FROM writeoffs w
           JOIN materials m ON m.id=w.material_id
           JOIN units     u ON u.id=m.unit_id
           JOIN users    us ON us.id=w.user_id
           ORDER BY w.created_at DESC LIMIT %s""",
        (limit,), fetch=True,
    )


def get_writeoff_by_id(wid: int):
    rows = execute_query(
        """SELECT w.*,m.name AS material,u.name AS unit,us.full_name AS created_by
           FROM writeoffs w
           JOIN materials m ON m.id=w.material_id
           JOIN units     u ON u.id=m.unit_id
           JOIN users    us ON us.id=w.user_id
           WHERE w.id=%s""",
        (wid,), fetch=True,
    )
    return rows[0] if rows else None
