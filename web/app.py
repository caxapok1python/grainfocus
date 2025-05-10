import os
from flask import Flask, render_template, send_from_directory, url_for, jsonify

app = Flask(
    __name__,
    template_folder='templates',  # корень папки web
    static_folder=None  # отключаем default-static
)

B_max = 0
B_min = 100
O_max = 0
O_min = 100


# Роут для отдачи любых CSS/HTML/JS из подпапок main и camera
@app.route('/main-view')
def main_view():
    global B_max, B_min, O_max, O_min
    with open('share/detection/classes.txt', 'r') as f:
        classes = list(map(int, f.readlines()[0].split(',')))
    all_classes = sum(classes)
    broken_pers = round(classes[0] / all_classes * 100, 1)
    objects_pers = round(classes[1] / all_classes * 100, 1)
    B_max = max(B_max, broken_pers)
    B_min = min(B_min, broken_pers)
    O_max = max(O_max, objects_pers)
    O_min = min(O_min, objects_pers)
    return render_template('main.html', min_sor=O_min, max_sor=O_max, now_sor=objects_pers, min_broken=B_min,
                           max_broken=B_max, now_broken=broken_pers)


@app.route('/camera-view')
def camera_view():
    return render_template('camera.html')


@app.route('/share/<path:path>')
def images(path):
    # Using request args for path will expose you to directory traversal attacks
    return send_from_directory('share', path)


# Пример данных, в реальности вы будете брать их из базы или сенсоров
_TIME_POINTS = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]  # минуты
_WEED_PERCENT = [2, 5, 8, 7, 6, 4, 3, 4, 6, 4, 3, 4]  # % сорности
_BROKEN_PERCENT = [1, 3, 4, 6, 5, 3, 2, 3, 5, 3, 2, 3]  # % битого зерна


@app.route('/api/metrics')
def metrics():
    return jsonify({
        'time': _TIME_POINTS,
        'weed': _WEED_PERCENT,
        'broken': _BROKEN_PERCENT
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
