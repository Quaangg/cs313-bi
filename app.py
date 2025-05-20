from flask import Flask, render_template
import os
from connectDB import connect_mysql
from stats import get_stats_data
from routes.search import search_bp
from routes.user import user_bp
from routes.course import course_bp


# Flask app
app = Flask(__name__)
conn = connect_mysql()
app.register_blueprint(search_bp)
app.register_blueprint(user_bp)
app.register_blueprint(course_bp)

# Flask routes
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/stats')
def stats():
    data = get_stats_data(conn)
    return render_template("stats.html", **data)

# Route chi tiết tạm thời
# @app.route('/user/<uid>')
# def user_detail(uid):
#     return f"<h2>Thông tin người dùng: {uid}</h2>"

# @app.route('/course/<cid>')
# def course_detail(cid):
#     return f"<h2>Thông tin khóa học: {cid}</h2>"


if __name__ == '__main__':
    app.run(debug=True)
