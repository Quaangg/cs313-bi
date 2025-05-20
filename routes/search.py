from flask import Blueprint, render_template, request
from connectDB import connect_mysql

search_bp = Blueprint('search', __name__)
conn = connect_mysql()

@search_bp.route('/search')
def search():
    print("alo gọi rồi nè")
    q = request.args.get('q', '').strip().lower()
    type_ = request.args.get('type', 'user')
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc').upper()
    if order not in ['ASC', 'DESC']:
        order = 'ASC'

    cursor = conn.cursor(dictionary=True)

    users, courses = [], []

    if q:
        cursor.execute("""
            SELECT * FROM user_info 
            WHERE LOWER(uid) LIKE %s OR LOWER(name) LIKE %s
        """, (f"%{q}%", f"%{q}%"))
        users = cursor.fetchall()

        cursor.execute("""
            SELECT DISTINCT c.cid FROM course_resource c 
            WHERE LOWER(c.cid) LIKE %s
        """, (f"%{q}%",))
        courses = cursor.fetchall()
    else:
        if type_ == 'user':
            cursor.execute(f"SELECT * FROM user_info ORDER BY uid {order}")
            users = cursor.fetchall()
        else:
            cursor.execute(f"SELECT DISTINCT cid FROM course_resource ORDER BY cid {order}")
            courses = cursor.fetchall()

    data = users if type_ == 'user' else courses

    return render_template("search.html",
        query=q,
        users=users,
        courses=courses,
        data=data,
        type_=type_,
        sort_by=sort_by,
        order=order
    )
