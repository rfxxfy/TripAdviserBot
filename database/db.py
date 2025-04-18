import time
import logging
import psycopg2
from psycopg2.extras import DictCursor
from contextlib import contextmanager
from database.db_config import DB_CONFIG

logger = logging.getLogger(__name__)

@contextmanager
def get_connection():
    """Контекстный менеджер для соединения с БД"""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_cursor(commit: bool = False):
    """
    Контекстный менеджер для курсора.
    Логирует время выполнения каждого запроса.
    """
    start_time = time.time()
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=DictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()
            elapsed = time.time() - start_time
            logger.info(f"[DB] Запрос выполнен за {elapsed:.4f} секунд")


def save_feedback(user_id, feedback_text):
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO feedback (user_id, feedback_text)
            VALUES (%s, %s)
            RETURNING feedback_id
            """,
            (user_id, feedback_text)
        )
        return cursor.fetchone()[0]


def register_user(user_id, username=None, first_name=None, last_name=None):
    """
    Регистрирует или обновляет пользователя.
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET last_activity = CURRENT_TIMESTAMP,
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name
            RETURNING user_id
            """,
            (user_id, username, first_name, last_name)
        )
        user = cursor.fetchone()[0]
    return user


def start_session(user_id):
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO sessions (user_id)
            VALUES (%s)
            RETURNING session_id
            """,
            (user_id,)
        )
        session_id = cursor.fetchone()[0]
    return session_id


def complete_session(session_id):
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            UPDATE sessions
            SET end_time = CURRENT_TIMESTAMP, completed = TRUE
            WHERE session_id = %s
            """,
            (session_id,)
        )

def save_route_selection(session_id, route_type, selected):
    """
    Функции для работы с маршрутами и предпочтениями
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO route_selections (session_id, route_type, selected)
            VALUES (%s, %s, %s)
            """,
            (session_id, route_type, selected)
        )

def save_location(session_id, departure_city, lat=None, lon=None):
    """
    Сохраняет выбор типа маршрута пользователя в базе данных.

    :param

    - session_id (int): Уникальный идентификатор сессии.
    - route_type (str): Тип маршрута (например, "photo", "food").
    - selected (bool): Был ли выбран данный тип маршрута (True/False).

    Returns:
    - None: Ничего не возвращает, сохраняет данные в базе.
    """
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO location_data (session_id, departure_city, lat, lon)
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, departure_city, lat, lon)
        )

def save_photo_location(session_id, photo_location_type):
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO photo_location_selections (session_id, photo_location_type)
            VALUES (%s, %s)
            """,
            (session_id, photo_location_type)
        )

def save_cuisine(session_id, cuisine_type):
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO cuisine_selections (session_id, cuisine_type)
            VALUES (%s, %s)
            """,
            (session_id, cuisine_type)
        )

def save_route_parameters(session_id, budget, days):
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO route_parameters (session_id, budget, days)
            VALUES (%s, %s, %s)
            """,
            (session_id, budget, days)
        )

def get_popular_routes(limit=10):
    """
    Returns the most frequently chosen route types.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT route_type, COUNT(*) as count
            FROM route_selections
            WHERE selected = TRUE
            GROUP BY route_type
            ORDER BY count DESC
            LIMIT %s;
            """,
            (limit,)
        )
        return cursor.fetchall()

def get_completion_stats():
    """
    Returns statistics about session completion rates.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                COUNT(*) as completed_sessions, 
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sessions) as completion_percentage
            FROM sessions
            WHERE completed = TRUE;
            """
        )
        return cursor.fetchone()

def get_user_stats_by_period(period='day', limit=30):
    """
    Returns user statistics aggregated by the specified period.
    
    :param period: 'day' or 'week'
    :param limit: Number of most recent periods to return
    """
    period_sql = "DATE(first_seen)" if period == 'day' else "DATE_TRUNC('week', first_seen)"
    
    with get_cursor() as cursor:
        cursor.execute(
            f"""
            SELECT {period_sql} as period, COUNT(*) as new_users
            FROM users
            GROUP BY period
            ORDER BY period DESC
            LIMIT %s;
            """,
            (limit,)
        )
        return cursor.fetchall()

def get_popular_cuisines(limit=10):
    """
    Returns the most frequently selected cuisine types.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT cuisine_type, COUNT(*) as count
            FROM cuisine_selections
            GROUP BY cuisine_type
            ORDER BY count DESC
            LIMIT %s;
            """,
            (limit,)
        )
        return cursor.fetchall()

def get_popular_photo_locations(limit=10):
    """
    Returns the most frequently selected photo location types.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT photo_location_type, COUNT(*) as count
            FROM photo_location_selections
            GROUP BY photo_location_type
            ORDER BY count DESC
            LIMIT %s;
            """,
            (limit,)
        )
        return cursor.fetchall()

def get_popular_departure_cities(limit=10):
    """
    Returns the most frequently entered departure cities.
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT departure_city, COUNT(*) as count
            FROM location_data
            GROUP BY departure_city
            ORDER BY count DESC
            LIMIT %s;
            """,
            (limit,)
        )
        return cursor.fetchall()


def is_user_admin(user_id: int) -> bool:
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT is_admin FROM users WHERE user_id = %s",
            (user_id,)
        )
        result = cursor.fetchone()
    return bool(result and result.get("is_admin", False))


def set_user_admin(target_user_id: int, is_admin: bool = True):
    with get_cursor(commit=True) as cursor:
        cursor.execute(
            "UPDATE users SET is_admin = %s WHERE user_id = %s",
            (is_admin, target_user_id)
        )


def get_all_users(limit: int = 100):
    with get_cursor() as cursor:
        cursor.execute(
            """
            SELECT user_id, username, first_name, last_name, is_admin
            FROM users
            ORDER BY first_seen DESC
            LIMIT %s
            """,
            (limit,)
        )
        return cursor.fetchall()