from flask import Blueprint, render_template
from connectDB import connect_mysql

user_bp = Blueprint('user', __name__)
conn = connect_mysql()

@user_bp.route('/user/<uid>')
def user_detail(uid):
    cursor = conn.cursor(dictionary=True)

    # Lấy thông tin người dùng
    cursor.execute("SELECT * FROM user_info WHERE uid = %s", (uid,))
    user = cursor.fetchone()

    if not user:
        return "Không tìm thấy người dùng", 404

    # Lấy nhãn dự đoán
    cursor.execute("SELECT predict FROM user_predict WHERE uid = %s", (uid,))
    row = cursor.fetchone()
    predict_label = row['predict'] if row else None

    # Lấy danh sách khóa học đã đăng ký
    cursor.execute("SELECT DISTINCT cid FROM user_course WHERE uid = %s", (uid,))
    courses = cursor.fetchall()

    progress_data = []
    for course in courses:
        cid = course['cid']
        # Tổng số resource của khóa học
        cursor.execute("SELECT COUNT(*) as total FROM course_resource WHERE cid = %s", (cid,))
        total_res = cursor.fetchone()['total']

        # Số resource mà user có hoạt động
        cursor.execute("""
            SELECT COUNT(DISTINCT cr.rid) as active
            FROM (
                SELECT vid AS rid FROM user_video WHERE uid = %s
                UNION
                SELECT ep.eid AS rid 
                FROM user_problem up
                INNER JOIN exercise_problem ep ON up.pid = ep.pid
                WHERE up.uid = %s
            ) AS all_activity
            INNER JOIN course_resource cr ON cr.rid = all_activity.rid
            WHERE cr.cid = %s
        """, (uid, uid, cid))
        active_res = cursor.fetchone()['active']

        progress = int((active_res / total_res) * 100) if total_res > 0 else 0

        progress_data.append({
            'cid': cid,
            'progress': progress
        })

    # Sắp xếp giảm dần theo % hoàn thành
    progress_data.sort(key=lambda x: -x['progress'])

    return render_template("user_detail.html", user=user, predict=predict_label, progress_data=progress_data)
