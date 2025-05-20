def get_stats_data(conn):
    cursor = conn.cursor()

    # 1. Active user rate
    cursor.execute('''
        SELECT COUNT(DISTINCT uid) FROM (
            SELECT uid FROM user_video
            UNION
            SELECT uid FROM user_problem
            UNION
            SELECT uid FROM user_comment
        ) AS active_users
    ''')
    active_users = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM user_info')
    total_users = cursor.fetchone()[0]

    active_user_rate = round((active_users / total_users) * 100, 2) if total_users else 0

    # 2. Tổng số user-course
    cursor.execute('SELECT COUNT(*) FROM user_course')
    total_course_registrations = cursor.fetchone()[0]

    # 3. user_predict distribution
    cursor.execute('SELECT predict, COUNT(*) FROM user_predict GROUP BY predict')
    label_data = cursor.fetchall()
    labels = [str(row[0]) for row in label_data]
    label_counts = [row[1] for row in label_data]

    # 4. Top 10 course activity
    cursor.execute('''
        SELECT cr.cid, COUNT(*) as activity_count
        FROM course_resource cr
        LEFT JOIN user_video uv ON cr.rid = uv.vid
        LEFT JOIN exercise_problem ep ON cr.rid = ep.eid
        LEFT JOIN user_problem up ON ep.pid = up.pid
        GROUP BY cr.cid
        ORDER BY activity_count DESC
        LIMIT 10
    ''')
    top_courses = cursor.fetchall()
    top_course_labels = [row[0] for row in top_courses]
    top_course_counts = [row[1] for row in top_courses]

    cursor.close()

    return {
        "active_user_rate": active_user_rate,
        "total_users": total_users,
        "total_course_registrations": total_course_registrations,
        "labels": labels,
        "label_counts": label_counts,
        "top_course_labels": top_course_labels,
        "top_course_counts": top_course_counts
    }
