from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc

from . import models
from .models import Session as DBSess
import datetime


def create_session(db: DBSession) -> DBSess:
    """
    Создаёт новую запись в таблице sessions и возвращает её.
    """
    # 1. Инстанцируем модель — это именно запись в таблицу sessions
    new_sess = DBSess()
    # 2. Добавляем её в текущую сессию подключения к БД
    db.add(new_sess)
    # 3. Физически сохраняем в базе
    db.commit()
    # 4. Чтобы new_sess получил сгенерированный id и ts
    db.refresh(new_sess)
    return new_sess
def end_session(db: DBSession, session_id: int) -> models.Session:
    sess = db.query(models.Session).get(session_id)
    if sess and sess.end_ts is None:
        sess.end_ts = datetime.datetime.utcnow()
        db.commit()
        db.refresh(sess)
    return sess

def add_reading(db: DBSession, session_id: int, weed: float, broken: float) -> models.Reading:
    reading = models.Reading(session_id=session_id, weed_pct=weed, broken_pct=broken)
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading

def get_readings(db: DBSession, session_id: int):
    return (
        db.query(models.Reading)
          .filter(models.Reading.session_id == session_id)
          .order_by(models.Reading.ts)
          .all()
    )

def get_last_session(db: DBSession) -> models.Session | None:
    """
    Возвращает самую недавно созданную сессию (по start_ts).
    """
    return (
        db.query(models.Session)
          .order_by(desc(models.Session.start_ts))
          .first()
    )