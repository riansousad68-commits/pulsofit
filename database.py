import sqlite3
from datetime import date, timedelta
from pathlib import Path


DATABASE_PATH = Path("workout_tracker.db")


def get_connection(db_path=DATABASE_PATH):
    """Open a SQLite connection configured to return rows like dictionaries."""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path=DATABASE_PATH):
    """Create all database tables used by the application."""
    with get_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                muscle_group TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_id INTEGER NOT NULL,
                sets INTEGER NOT NULL CHECK (sets > 0),
                reps INTEGER NOT NULL CHECK (reps > 0),
                date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS availability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_of_week INTEGER NOT NULL UNIQUE CHECK (day_of_week BETWEEN 0 AND 6)
            );
            """
        )


def create_exercise(name, muscle_group, description, db_path=DATABASE_PATH):
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO exercises (name, muscle_group, description)
            VALUES (?, ?, ?)
            """,
            (name.strip(), muscle_group.strip(), description.strip()),
        )
        return cursor.lastrowid


def list_exercises(db_path=DATABASE_PATH):
    with get_connection(db_path) as connection:
        return connection.execute(
            "SELECT * FROM exercises ORDER BY name COLLATE NOCASE"
        ).fetchall()


def get_exercise(exercise_id, db_path=DATABASE_PATH):
    with get_connection(db_path) as connection:
        return connection.execute(
            "SELECT * FROM exercises WHERE id = ?", (exercise_id,)
        ).fetchone()


def update_exercise(exercise_id, name, muscle_group, description, db_path=DATABASE_PATH):
    with get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE exercises
            SET name = ?, muscle_group = ?, description = ?
            WHERE id = ?
            """,
            (name.strip(), muscle_group.strip(), description.strip(), exercise_id),
        )


def delete_exercise(exercise_id, db_path=DATABASE_PATH):
    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM exercises WHERE id = ?", (exercise_id,))


def create_workout(exercise_id, sets, reps, workout_date, db_path=DATABASE_PATH):
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO workouts (exercise_id, sets, reps, date)
            VALUES (?, ?, ?, ?)
            """,
            (exercise_id, int(sets), int(reps), workout_date),
        )
        return cursor.lastrowid


def list_workouts(workout_date=None, db_path=DATABASE_PATH):
    sql = """
        SELECT
            workouts.*,
            exercises.name AS exercise_name,
            exercises.muscle_group AS muscle_group,
            workouts.sets * workouts.reps AS total_reps
        FROM workouts
        JOIN exercises ON exercises.id = workouts.exercise_id
    """
    params = ()

    if workout_date:
        sql += " WHERE workouts.date = ?"
        params = (workout_date,)

    sql += " ORDER BY workouts.date DESC, workouts.id DESC"

    with get_connection(db_path) as connection:
        return connection.execute(sql, params).fetchall()


def get_workout(workout_id, db_path=DATABASE_PATH):
    with get_connection(db_path) as connection:
        return connection.execute(
            "SELECT * FROM workouts WHERE id = ?", (workout_id,)
        ).fetchone()


def update_workout(workout_id, exercise_id, sets, reps, workout_date, db_path=DATABASE_PATH):
    with get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE workouts
            SET exercise_id = ?, sets = ?, reps = ?, date = ?
            WHERE id = ?
            """,
            (exercise_id, int(sets), int(reps), workout_date, workout_id),
        )


def delete_workout(workout_id, db_path=DATABASE_PATH):
    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))


def set_available_days(days, db_path=DATABASE_PATH):
    normalized_days = sorted({int(day) for day in days if str(day).isdigit()})
    normalized_days = [day for day in normalized_days if 0 <= day <= 6]

    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM availability")
        connection.executemany(
            "INSERT INTO availability (day_of_week) VALUES (?)",
            [(day,) for day in normalized_days],
        )


def get_available_days(db_path=DATABASE_PATH):
    with get_connection(db_path) as connection:
        return connection.execute(
            "SELECT day_of_week FROM availability ORDER BY day_of_week"
        ).fetchall()


def get_dashboard_summary(reference_date=None, db_path=DATABASE_PATH):
    """Return weekly stats and a game-like level based on total training volume."""
    today = reference_date or date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    with get_connection(db_path) as connection:
        weekly = connection.execute(
            """
            SELECT
                COUNT(*) AS weekly_workouts,
                COALESCE(SUM(sets * reps), 0) AS weekly_reps
            FROM workouts
            WHERE date BETWEEN ? AND ?
            """,
            (week_start.isoformat(), week_end.isoformat()),
        ).fetchone()

        top = connection.execute(
            """
            SELECT exercises.name, SUM(workouts.sets * workouts.reps) AS volume
            FROM workouts
            JOIN exercises ON exercises.id = workouts.exercise_id
            GROUP BY exercises.id
            ORDER BY volume DESC, exercises.name COLLATE NOCASE
            LIMIT 1
            """
        ).fetchone()

        lifetime = connection.execute(
            "SELECT COALESCE(SUM(sets * reps), 0) AS reps, COALESCE(SUM(sets), 0) AS sets FROM workouts"
        ).fetchone()

    xp = int(lifetime["reps"] + (lifetime["sets"] * 5))
    level = max(1, (xp // 250) + 1)
    current_level_floor = (level - 1) * 250
    next_level_floor = level * 250
    progress = int(((xp - current_level_floor) / 250) * 100)

    return {
        "weekly_workouts": weekly["weekly_workouts"],
        "weekly_reps": weekly["weekly_reps"],
        "top_exercise": top["name"] if top else "Nenhum ainda",
        "xp": xp,
        "level": level,
        "next_level_xp": next_level_floor,
        "progress": min(progress, 100),
    }
