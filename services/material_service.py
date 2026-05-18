from database.db import execute_query


def get_categories():
    return execute_query("SELECT id,name FROM categories ORDER BY name", fetch=True)


def get_units():
    return execute_query("SELECT id,name FROM units ORDER BY name", fetch=True)


def get_materials(search="", category_id=None):
    sql = """
        SELECT m.id, m.name, c.name AS category, u.name AS unit,
               m.quantity, m.min_quantity, m.price,
               CASE WHEN m.quantity < m.min_quantity THEN 1 ELSE 0 END AS low_stock
        FROM materials m
        JOIN categories c ON c.id=m.category_id
        JOIN units      u ON u.id=m.unit_id
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND m.name LIKE %s"; params.append(f"%{search}%")
    if category_id:
        sql += " AND m.category_id=%s"; params.append(category_id)
    sql += " ORDER BY c.name, m.name"
    return execute_query(sql, tuple(params), fetch=True)


def get_material_by_id(mid: int):
    rows = execute_query(
        """SELECT m.*,c.name AS category,u.name AS unit
           FROM materials m
           JOIN categories c ON c.id=m.category_id
           JOIN units      u ON u.id=m.unit_id
           WHERE m.id=%s""",
        (mid,), fetch=True,
    )
    return rows[0] if rows else None


def add_material(name, category_id, unit_id, quantity: int, min_quantity: int, price, description=""):
    return execute_query(
        """INSERT INTO materials
           (name,category_id,unit_id,quantity,min_quantity,price,description)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (name, category_id, unit_id, quantity, min_quantity, price, description),
    )


def update_material(mid, name, category_id, unit_id, min_quantity: int, price, description=""):
    execute_query(
        """UPDATE materials
           SET name=%s,category_id=%s,unit_id=%s,min_quantity=%s,price=%s,description=%s
           WHERE id=%s""",
        (name, category_id, unit_id, min_quantity, price, description, mid),
    )


def set_min_quantity(mid: int, min_qty: int):
    execute_query("UPDATE materials SET min_quantity=%s WHERE id=%s", (min_qty, mid))


def delete_material(mid: int):
    execute_query("DELETE FROM materials WHERE id=%s", (mid,))


def get_low_stock():
    return execute_query(
        """SELECT m.id,m.name,c.name AS category,u.name AS unit,
                  m.quantity,m.min_quantity
           FROM materials m
           JOIN categories c ON c.id=m.category_id
           JOIN units      u ON u.id=m.unit_id
           WHERE m.quantity < m.min_quantity ORDER BY m.name""",
        fetch=True,
    )
