from database.db import execute_query


def get_dashboard_stats():
    mat   = execute_query("SELECT COUNT(*) AS cnt, SUM(quantity*price) AS val FROM materials", fetch=True)[0]
    low   = execute_query("SELECT COUNT(*) AS cnt FROM materials WHERE quantity<min_quantity", fetch=True)[0]
    rcnt  = execute_query("SELECT COUNT(*) AS cnt FROM receipts WHERE DATE(created_at)=CURDATE()", fetch=True)[0]
    wcnt  = execute_query("SELECT COUNT(*) AS cnt FROM writeoffs WHERE DATE(created_at)=CURDATE()", fetch=True)[0]

    last_r = execute_query(
        """SELECT r.created_at,m.name AS material,r.quantity,u.name AS unit,r.supplier
           FROM receipts r JOIN materials m ON m.id=r.material_id
           JOIN units u ON u.id=m.unit_id
           ORDER BY r.created_at DESC LIMIT 8""", fetch=True)

    last_w = execute_query(
        """SELECT w.created_at,m.name AS material,w.quantity,u.name AS unit,w.reason
           FROM writeoffs w JOIN materials m ON m.id=w.material_id
           JOIN units u ON u.id=m.unit_id
           ORDER BY w.created_at DESC LIMIT 8""", fetch=True)

    low_list = execute_query(
        """SELECT m.name,c.name AS category,u.name AS unit,m.quantity,m.min_quantity
           FROM materials m
           JOIN categories c ON c.id=m.category_id
           JOIN units      u ON u.id=m.unit_id
           WHERE m.quantity<m.min_quantity ORDER BY m.name""", fetch=True)

    return {
        "materials_count": mat["cnt"],
        "total_value":     float(mat["val"] or 0),
        "low_stock_count": low["cnt"],
        "receipts_today":  rcnt["cnt"],
        "writeoffs_today": wcnt["cnt"],
        "last_receipts":   last_r,
        "last_writeoffs":  last_w,
        "low_list":        low_list,
    }


def get_stock_report():
    return execute_query(
        """SELECT m.name,c.name AS category,u.name AS unit,
                  m.quantity,m.min_quantity,m.price,
                  ROUND(m.quantity*m.price,2) AS total_value,
                  CASE WHEN m.quantity<m.min_quantity THEN 'Ниже нормы' ELSE 'В норме' END AS status
           FROM materials m
           JOIN categories c ON c.id=m.category_id
           JOIN units      u ON u.id=m.unit_id
           ORDER BY c.name,m.name""", fetch=True)


def get_receipts_report(date_from=None, date_to=None):
    sql = """SELECT r.id,r.created_at,m.name AS material,u.name AS unit,
                    r.quantity,r.price,ROUND(r.quantity*r.price,2) AS total,
                    r.supplier,r.document_number,us.full_name AS created_by
             FROM receipts r
             JOIN materials m ON m.id=r.material_id
             JOIN units     u ON u.id=m.unit_id
             JOIN users    us ON us.id=r.user_id"""
    params, conds = [], []
    if date_from: conds.append("DATE(r.created_at)>=%s"); params.append(date_from)
    if date_to:   conds.append("DATE(r.created_at)<=%s"); params.append(date_to)
    if conds: sql += " WHERE " + " AND ".join(conds)
    sql += " ORDER BY r.created_at DESC"
    return execute_query(sql, tuple(params), fetch=True)


def get_writeoffs_report(date_from=None, date_to=None):
    sql = """SELECT w.id,w.created_at,m.name AS material,u.name AS unit,
                    w.quantity,w.reason,w.document_number,us.full_name AS created_by
             FROM writeoffs w
             JOIN materials m ON m.id=w.material_id
             JOIN units     u ON u.id=m.unit_id
             JOIN users    us ON us.id=w.user_id"""
    params, conds = [], []
    if date_from: conds.append("DATE(w.created_at)>=%s"); params.append(date_from)
    if date_to:   conds.append("DATE(w.created_at)<=%s"); params.append(date_to)
    if conds: sql += " WHERE " + " AND ".join(conds)
    sql += " ORDER BY w.created_at DESC"
    return execute_query(sql, tuple(params), fetch=True)
