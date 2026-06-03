import unittest
from datetime import date
from tempfile import TemporaryDirectory
from pathlib import Path

import database


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "fit.db"
        database.init_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_exercise_crud(self):
        exercise_id = database.create_exercise(
            "Flexoes", "Peito", "Flexoes tradicionais com postura firme.", self.db_path
        )
        exercise = database.get_exercise(exercise_id, self.db_path)

        self.assertEqual(exercise["name"], "Flexoes")
        self.assertEqual(exercise["muscle_group"], "Peito")

        database.update_exercise(
            exercise_id, "Flexoes diamante", "Triceps", "Maos proximas.", self.db_path
        )
        updated = database.get_exercise(exercise_id, self.db_path)

        self.assertEqual(updated["name"], "Flexoes diamante")
        self.assertEqual(updated["muscle_group"], "Triceps")

    def test_workout_history_and_dashboard_summary(self):
        pushup_id = database.create_exercise("Flexoes", "Peito", "", self.db_path)
        squat_id = database.create_exercise("Agachamentos", "Pernas", "", self.db_path)

        database.create_workout(pushup_id, 4, 15, "2026-06-01", self.db_path)
        database.create_workout(pushup_id, 3, 20, "2026-06-02", self.db_path)
        database.create_workout(squat_id, 5, 12, "2026-06-02", self.db_path)

        history = database.list_workouts("2026-06-02", self.db_path)
        summary = database.get_dashboard_summary(date(2026, 6, 2), self.db_path)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["date"], "2026-06-02")
        self.assertEqual(summary["weekly_workouts"], 3)
        self.assertEqual(summary["weekly_reps"], 180)
        self.assertEqual(summary["top_exercise"], "Flexoes")
        self.assertEqual(summary["level"], 1)
        self.assertEqual(summary["xp"], 240)

    def test_schedule_can_be_replaced(self):
        database.set_available_days([0, 2, 4], self.db_path)
        first_schedule = database.get_available_days(self.db_path)
        self.assertEqual([day["day_of_week"] for day in first_schedule], [0, 2, 4])

        database.set_available_days([1, 3], self.db_path)
        second_schedule = database.get_available_days(self.db_path)
        self.assertEqual([day["day_of_week"] for day in second_schedule], [1, 3])


if __name__ == "__main__":
    unittest.main()
