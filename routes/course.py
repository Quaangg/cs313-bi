from flask import Blueprint, render_template
from connectDB import connect_mysql

course_bp = Blueprint('course', __name__)
conn = connect_mysql()

@course_bp.route('/course/<cid>')
def course_detail(cid):
    cursor = conn.cursor(dictionary=True)

    # 1. Lấy thông tin cơ bản của khóa học
    # cursor.execute("""
    #     SELECT * FROM course_info WHERE cid = %s
    # """, (cid,))
    # course = cursor.fetchone()
    course = str(cid)

    # 2. Lấy danh sách người dùng đã đăng ký khóa học này
    cursor.execute("""
        SELECT DISTINCT u.uid, u.name 
        FROM user_info u
        INNER JOIN course_resource cr ON cr.cid = %s
        INNER JOIN user_video uv ON uv.vid = cr.rid
        WHERE uv.uid = u.uid
        UNION
        SELECT DISTINCT u.uid, u.name 
        FROM user_info u
        INNER JOIN course_resource cr ON cr.cid = %s
        INNER JOIN user_problem up ON up.pid = cr.rid
        WHERE up.uid = u.uid
    """, (cid, cid))
    users = cursor.fetchall()

    # 3. Tính mức độ hoàn thành của mỗi user
    user_progress = {}
    for user in users:
        uid = user['uid']

        # Tính số lượng resource mà user đã hoàn thành trong khóa học này
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

        # Tính số lượng tổng resource trong khóa học này
        cursor.execute("""
            SELECT COUNT(DISTINCT rid) as total
            FROM course_resource WHERE cid = %s
        """, (cid,))
        total_res = cursor.fetchone()['total']

        # Tính mức độ hoàn thành (số lượng tài nguyên đã hoàn thành / tổng số tài nguyên)
        if total_res > 0:
            completion_rate = active_res / total_res
        else:
            completion_rate = 0

        user_progress[uid] = {
            'name': user['name'],
            'completion_rate': completion_rate
        }

    # 4. Tính tỉ lệ hoàn thành trung bình của khóa học
    total_completion = sum([user['completion_rate'] for user in user_progress.values()])
    avg_completion_rate = total_completion / len(user_progress) if user_progress else 0

    return render_template(
        "course_detail.html", 
        course=course, 
        users=user_progress, 
        avg_completion_rate=avg_completion_rate
    )
