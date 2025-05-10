from flask import Flask, render_template, send_from_directory, jsonify, abort, request
import os

from sqlalchemy import func

from database.db import SessionLocal, Base, engine
from database.models import Session as DBSess, Reading
from database.crud import get_last_session, get_readings, add_reading, create_session

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    sess = create_session(db)
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

# для хранения min/max по сессии
stats = {
    'broken': {'min': 100.0, 'max': 0.0},
    'weed': {'min': 100.0, 'max': 0.0}
}

SHARE_DIR = 'share'
DETECTION_DIR = 'share/detection'
CLASSES_FILE = os.path.join(DETECTION_DIR, 'classes.txt')
RAW_FRAME = 'image.png'
ANNOT_FRAME = 'annotated.png'


@app.route('/main-view')
def index():
    return render_template('main.html')


@app.route('/camera-view')
def camera_view():
    return render_template('camera.html')


@app.route('/share/<path:filename>')
def share(filename):
    # отдаём файлы из папки share/detection
    return send_from_directory(SHARE_DIR, filename)


@app.route('/api/session/latest', methods=['GET'])
def api_latest_session():
    with SessionLocal() as db:
        sess = get_last_session(db)
        if not sess:
            return jsonify({}), 404
        return jsonify({
            'session_id': sess.id,
            'start_ts': sess.start_ts.isoformat(),
            'end_ts': sess.end_ts.isoformat() if sess.end_ts else None
        })


@app.route('/api/session/latest/readings', methods=['GET'])
def api_latest_readings():
    with SessionLocal() as db:
        sess = get_last_session(db)
        if not sess:
            return jsonify([]), 404
        rows = get_readings(db, sess.id)
        return jsonify([
            {
                'ts': r.ts.isoformat(),
                'weed': r.weed_pct,
                'broken': r.broken_pct
            } for r in rows
        ])


@app.route('/api/session/latest/add', methods=['POST'])
def api_add_to_latest():
    data = request.get_json(force=True)
    if 'weed_pct' not in data or 'broken_pct' not in data:
        return jsonify({"error": "Missing fields"}), 400

    # Поля, которые вернём в ответе
    resp_data = {}

    with SessionLocal() as db:
        sess = get_last_session(db)
        if not sess or sess.end_ts is not None:
            # создаём новую сессию, если нужно
            from crud import create_session
            sess = create_session(db, name="Auto session", meta_info={})

        reading = add_reading(db,
                              session_id=sess.id,
                              weed=data['weed_pct'],
                              broken=data['broken_pct'])

        # читаем поля **до** выхода из with
        resp_data = {
            "reading_id": reading.id,
            "session_id": sess.id,
            "ts": reading.ts.isoformat()
        }

    # теперь сессия закрыта, но у нас уже есть необходимые данные
    return jsonify(resp_data), 201


@app.route('/api/session/stats', methods=['GET'])
def api_stats():
    """
    Отдаёт текущие, min/max по последней сессии на основе записанных readings.
    """
    with SessionLocal() as db:
        sess = get_last_session(db)
        if not sess:
            abort(404, 'No active session')

        rows = get_readings(db, sess.id)
        if not rows:
            return jsonify({
                'now': {'weed': None, 'broken': None},
                'min': {'weed': None, 'broken': None},
                'max': {'weed': None, 'broken': None}
            })

        weeds = [r.weed_pct for r in rows]
        brokens = [r.broken_pct for r in rows]

        now = {'weed': weeds[-1], 'broken': brokens[-1]}
        return jsonify({
            'now': now,
            'min': {'weed': min(weeds), 'broken': min(brokens)},
            'max': {'weed': max(weeds), 'broken': max(brokens)}
        })


@app.route('/api/session/images')
def api_images():
    """
    Возвращает URL'ы на последние кадры:
      - raw: необработанный кадр
      - annot: кадр с аннотациями
    """
    return jsonify({
        'raw': f'/share/detection/{RAW_FRAME}',
        'annot': f'/share/detection/{ANNOT_FRAME}'
    })


@app.route('/api/metrics')
def api_metrics():
    """
    Отдаёт агрегированные по минутам показатели 'weed' и 'broken'
    для последней сессии.
    Формат ответа:
    {
      "time":   ["HH:MM", "HH:MM", …],
      "weed":   [float, float, …],
      "broken": [float, float, …]
    }
    """
    # 1) найдём последнюю сессию
    with SessionLocal() as db:
        sess = get_last_session(db)
        if not sess:
            abort(404, "No session found")

        # 2) сгруппируем readings по минуте
        #    т.к. SQLite, воспользуемся SQL-агрегацией:
        rows = (
            db.query(
                func.strftime('%H:%M', Reading.ts).label('minute'),
                func.avg(Reading.weed_pct).label('weed_avg'),
                func.avg(Reading.broken_pct).label('broken_avg')
            )
            .filter(Reading.session_id == sess.id)
            .group_by('minute')
            .order_by('minute')
            .all()
        )

    # 3) распаковываем в списки
    times = [r.minute for r in rows]
    weeds = [round(r.weed_avg, 2) for r in rows]
    brokens = [round(r.broken_avg, 2) for r in rows]

    # 4) если нужно — можно сделать простое скользящее среднее (опционально)
    #    def smooth(data, window=3):
    #        sm = []
    #        for i in range(len(data)):
    #            slice_ = data[max(0, i - (window//2)): min(len(data), i + (window//2) + 1)]
    #            sm.append(round(sum(slice_) / len(slice_), 2))
    #        return sm
    #    weeds   = smooth(weeds)
    #    brokens = smooth(brokens)

    return jsonify({
        'time': times,
        'weed': weeds,
        'broken': brokens
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
