import os
from flask import Flask, render_template, send_from_directory, url_for, jsonify

app = Flask(
    __name__,
    template_folder='.',      # корень папки web
    static_folder=None        # отключаем default-static
)

# Роут для отдачи любых CSS/HTML/JS из подпапок main и camera
@app.route('/main-view')
def main_view():
    return render_template('main.html', min_sor=6, max_sor=11.9, now_sor=17.8, min_broken=1, max_broken=4, now_broken=1.4)

@app.route('/camera-view')
def camera_view():
    return render_template('camera.html', a=1)

@app.route('/img/<path:path>')
def images(path):
    # Using request args for path will expose you to directory traversal attacks
    return send_from_directory('img', path)



if __name__ == '__main__':
    # путь до файла БД (SQLite)
    db_path = os.path.join(app.root_path, '..', 'database.sqlite')
    os.environ.setdefault('SQLITE_PATH', db_path)
    app.run(host='0.0.0.0', port=8000, debug=True)