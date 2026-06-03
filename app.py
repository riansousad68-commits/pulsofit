from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for

import database


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-me"

DAY_LABELS = [
    (0, "Segunda"),
    (1, "Terca"),
    (2, "Quarta"),
    (3, "Quinta"),
    (4, "Sexta"),
    (5, "Sabado"),
    (6, "Domingo"),
]


@app.before_request
def prepare_database():
    """Guarantee the SQLite schema exists before handling a page request."""
    database.init_db()


@app.route("/")
def index():
    selected_date = request.args.get("date", "")
    exercises = database.list_exercises()
    workouts = database.list_workouts(selected_date or None)
    summary = database.get_dashboard_summary()
    available_days = {row["day_of_week"] for row in database.get_available_days()}

    return render_template(
        "index.html",
        today=date.today().isoformat(),
        selected_date=selected_date,
        exercises=exercises,
        workouts=workouts,
        summary=summary,
        day_labels=DAY_LABELS,
        available_days=available_days,
    )


@app.post("/exercises")
def add_exercise():
    name = request.form.get("name", "").strip()
    muscle_group = request.form.get("muscle_group", "").strip()
    description = request.form.get("description", "").strip()

    if not name or not muscle_group:
        flash("Informe o nome e o grupo muscular do exercicio.", "error")
        return redirect(url_for("index"))

    database.create_exercise(name, muscle_group, description)
    flash("Exercicio cadastrado com sucesso.", "success")
    return redirect(url_for("index"))


@app.post("/exercises/<int:exercise_id>/edit")
def edit_exercise(exercise_id):
    name = request.form.get("name", "").strip()
    muscle_group = request.form.get("muscle_group", "").strip()
    description = request.form.get("description", "").strip()

    if not name or not muscle_group:
        flash("Nome e grupo muscular sao obrigatorios.", "error")
        return redirect(url_for("index"))

    database.update_exercise(exercise_id, name, muscle_group, description)
    flash("Exercicio atualizado.", "success")
    return redirect(url_for("index"))


@app.post("/exercises/<int:exercise_id>/delete")
def remove_exercise(exercise_id):
    database.delete_exercise(exercise_id)
    flash("Exercicio removido junto com seus treinos.", "success")
    return redirect(url_for("index"))


@app.post("/workouts")
def add_workout():
    exercise_id = request.form.get("exercise_id")
    sets = request.form.get("sets", type=int)
    reps = request.form.get("reps", type=int)
    workout_date = request.form.get("date", "").strip()

    if not exercise_id or not sets or not reps or not workout_date:
        flash("Preencha exercicio, series, repeticoes e data.", "error")
        return redirect(url_for("index"))

    database.create_workout(exercise_id, sets, reps, workout_date)
    flash("Treino registrado. XP adicionado!", "success")
    return redirect(url_for("index"))


@app.post("/workouts/<int:workout_id>/edit")
def edit_workout(workout_id):
    exercise_id = request.form.get("exercise_id")
    sets = request.form.get("sets", type=int)
    reps = request.form.get("reps", type=int)
    workout_date = request.form.get("date", "").strip()

    if not exercise_id or not sets or not reps or not workout_date:
        flash("Todos os campos do treino sao obrigatorios.", "error")
        return redirect(url_for("index"))

    database.update_workout(workout_id, exercise_id, sets, reps, workout_date)
    flash("Treino atualizado.", "success")
    return redirect(url_for("index"))


@app.post("/workouts/<int:workout_id>/delete")
def remove_workout(workout_id):
    database.delete_workout(workout_id)
    flash("Registro de treino deletado.", "success")
    return redirect(url_for("index"))


@app.post("/schedule")
def update_schedule():
    days = request.form.getlist("days")
    database.set_available_days(days)
    flash("Cronograma atualizado.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    database.init_db()
    app.run(debug=True)
