import sqlite3
from flask import Flask, redirect, render_template, request, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    rows = db.query("SELECT id, password_hash FROM users WHERE username = ?", [username])
    if not rows:
        return "VIRHE: väärä tunnus tai salasana"

    user_id = rows[0]["id"]
    password_hash = rows[0]["password_hash"]

    if check_password_hash(password_hash, password):
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät täsmää"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return render_template("registered.html")

@app.route("/recipes")
def recipes():
    return render_template("recipes.html")

@app.route("/add_recipe")
def add_recipe():
    if "username" not in session:
        abort(403)
    return render_template("add_recipe.html")

@app.route("/send", methods=["POST"])
def send():
    if "username" not in session:
        abort(403)

    dish_name = request.form["dish_name"].strip()
    dish_type = request.form.get("dish_type")
    diet = ", ".join(request.form.getlist("diet"))
    ingredients = request.form["ingredients"]
    comment = request.form["comment"]
    grade = request.form.get("grade")

    if not dish_name or not dish_type or not grade:
        return "Täytä vähintään nimi, ruokalaji ja arvosana"

    if dish_type not in ("Alkuruoka", "Pääruoka", "Jälkiruoka"):
        abort(400)

    grade = int(grade)
    if grade < 1 or grade > 5:
        abort(400)

    db.execute(
        "INSERT INTO recipe (user_id, name, dish_type, diet, ingredients, comment, grade) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        [session["user_id"], dish_name, dish_type, diet, ingredients, comment, grade])

    return redirect("/recipes")

def get_own_recipe(recipe_id):
    if "user_id" not in session:
        abort(403)
    rows = db.query("SELECT * FROM recipe WHERE id = ?", [recipe_id])
    if not rows:
        abort(404)
    recipe = rows[0]
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    return recipe

@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    recipe = get_own_recipe(recipe_id)

    if request.method == "GET":
        return render_template("edit_recipe.html", recipe=recipe)

    dish_name = request.form["dish_name"].strip()
    dish_type = request.form.get("dish_type")
    diet = ", ".join(request.form.getlist("diet"))
    ingredients = request.form["ingredients"]
    comment = request.form["comment"]
    grade = request.form.get("grade")

    if not dish_name or not dish_type or not grade:
        return "Täytä vähintään nimi, ruokalaji ja arvosana"
    if dish_type not in ("Alkuruoka", "Pääruoka", "Jälkiruoka"):
        abort(400)
    grade = int(grade)
    if grade < 1 or grade > 5:
        abort(400)

    db.execute(
        "UPDATE recipe SET name = ?, dish_type = ?, diet = ?, "
        "ingredients = ?, comment = ?, grade = ? WHERE id = ?",
        [dish_name, dish_type, diet, ingredients, comment, grade, recipe_id])

    return redirect("/recipes")

DISH_TYPES = ("Alkuruoka", "Pääruoka", "Jälkiruoka")
DIETS = ("Gluteeniton", "Laktoositon", "Vegaaninen")

@app.route("/search")
def search():
    author = request.args.get("author", "").strip()
    name = request.args.get("name", "").strip()
    comment = request.args.get("comment", "").strip()
    dish_types = [d for d in request.args.getlist("dish_type") if d in DISH_TYPES]
    diets = [d for d in request.args.getlist("diet") if d in DIETS]
    grades = [int(g) for g in request.args.getlist("grade") if g in ("1", "2", "3", "4", "5")]

    searched = bool(request.args)
    results = []

    if searched:
        sql = ("SELECT r.id, r.user_id, r.name, r.dish_type, r.diet, r.ingredients, "
                "r.comment, r.grade, u.username "
                "FROM recipe r JOIN users u ON u.id = r.user_id WHERE 1 = 1")
        params = []

        if author:
            sql += " AND py_lower(u.username) LIKE ?"
            params.append("%" + author.lower() + "%")

        if name:
            sql += " AND py_lower(r.name) LIKE ?"
            params.append("%" + name.lower() + "%")

        if comment:
            sql += " AND py_lower(r.comment) LIKE ?"
            params.append("%" + comment.lower() + "%")

        if dish_types:
            sql += " AND r.dish_type IN (" + ", ".join("?" * len(dish_types)) + ")"
            params += dish_types

        if grades:
            sql += " AND r.grade IN (" + ", ".join("?" * len(grades)) + ")"
            params += grades

        for diet in diets:
            sql += " AND r.diet LIKE ?"
            params.append("%" + diet + "%")

        sql += " ORDER BY r.name"
        results = db.query(sql, params)

    return render_template("search.html", results=results, searched=searched,
                           name=name, comment=comment, dish_types=dish_types,
                           author=author, diets=diets, grades=grades)

@app.route("/delete_recipe/<int:recipe_id>", methods=["POST"])
def delete_recipe(recipe_id):
    get_own_recipe(recipe_id)   # tarkistaa kirjautumisen, olemassaolon ja omistajan
    db.execute("DELETE FROM recipe WHERE id = ?", [recipe_id])
    return redirect("/recipes")

@app.route("/starters")
def starters():
    recipes = db.query(
        "SELECT r.id, r.user_id, r.name, r.diet, r.ingredients, r.comment, r.grade, "
        "u.username "
        "FROM recipe r JOIN users u ON u.id = r.user_id "
        "WHERE r.dish_type = ? ORDER BY r.name",
        ["Alkuruoka"])
    return render_template("starters.html", recipes=recipes)

@app.route("/mains")
def mains():
    recipes = db.query(
        "SELECT r.id, r.user_id, r.name, r.diet, r.ingredients, r.comment, r.grade, "
        "u.username "
        "FROM recipe r JOIN users u ON u.id = r.user_id "
        "WHERE r.dish_type = ? ORDER BY r.name",
        ["Pääruoka"])
    return render_template("mains.html", recipes=recipes)

@app.route("/desserts")
def desserts():
    recipes = db.query(
        "SELECT r.id, r.user_id, r.name, r.diet, r.ingredients, r.comment, r.grade, "
        "u.username "
        "FROM recipe r JOIN users u ON u.id = r.user_id "
        "WHERE r.dish_type = ? ORDER BY r.name",
        ["Jälkiruoka"])
    return render_template("desserts.html", recipes=recipes)


if __name__ == "__main__":
    app.run(debug=True)