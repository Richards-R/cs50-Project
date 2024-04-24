import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import datetime
from random import randint

# login_required


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database of Users, Results histories and Questions(Problems)
db = SQL("sqlite:///testprobs.db")

# Retrieve unique number of years
total_years = db.execute("SELECT COUNT(DISTINCT year) FROM Problems")
ty = total_years[0]['COUNT(DISTINCT year)']

# Retrieve start year
start_year = db.execute("SELECT MIN(year) FROM Problems")
sy = start_year[0]['MIN(year)']

# Retrieve unique number of questions (each year)
total_questions = db.execute("SELECT COUNT(DISTINCT Prob_No) FROM Problems")
tq = total_questions[0]['COUNT(DISTINCT Prob_No)']

# Retrieve start question
start_question = db.execute("SELECT MIN(Prob_No) FROM Problems")
sq = start_question[0]['MIN(Prob_No)']


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show years and questions"""

    name = db.execute("SELECT Username FROM users WHERE id = ?;", session['user_id'])
    user_name = name[0]['Username']

    # Create object for each question to include accuracy% for conditional styling of background colour
    matrix_arr = []
    for yr in range(sy, (sy+ty)):
        for qt in range(sq, (sq+tq)):
            temp_obj = {"year": yr, "quest_num": qt, "accuracy": "grey_bg", "max(id)": None}
            matrix_arr.append(temp_obj)

    accuracy = db.execute(
        "SELECT year, quest_num, accuracy, max(id) FROM results WHERE user_id = ? GROUP BY year, quest_num;", user_name)

    for i in matrix_arr:
        for j in accuracy:
            if i['year'] == j['year'] and i['quest_num'] == j['quest_num']:
                i['accuracy'] = j['accuracy']
                if int(i['accuracy']) > 75:
                    i['accuracy'] = "green_bg"
                elif int(i['accuracy']) > 50:
                    i['accuracy'] = "yellow_bg"
                elif int(i['accuracy']) >= 0:
                    i['accuracy'] = "red_bg"
                else:
                    i['accuracy'] = "grey_bg"

    return render_template("years.html", def_year=0, def_quest=0, matrix_arr=matrix_arr, ty=ty, sy=sy, tq=tq, sq=sq)


@app.route("/select", methods=["POST"])
@login_required
def select():
    """Select question from database"""

    quest_num = None
    year = request.form.get("year_button")
    default_year = request.form.get("def_year")
    default_quest = request.form.get("def_quest")
    matrix_input = request.form.get("matrix_input")
    prev_select = request.form.get("prev_select")
    next_select = request.form.get("next_select")
    random_select = request.form.get("random_select")

    if prev_select:
        if int(default_quest) == sq:
            year = int(default_year) - 1
            quest_num = tq
        else:
            quest_num = int(default_quest) - 1

    if next_select:
        if int(default_quest) == tq:
            year = int(default_year) + 1
            quest_num = sq
        else:
            quest_num = int(default_quest) + 1

    if random_select:
        year = randint(sy, (sy+ty-1))
        quest_num = randint(sq, tq)

    if year is None:
        if matrix_input:
            matrix_input = int(matrix_input)
            quest_num = matrix_input % tq
            year = round(((matrix_input-1 - (matrix_input % tq))/tq)+sy)
            if quest_num == 0:
                quest_num = tq
                year -= 1
        else:
            year = default_year

    name = db.execute("SELECT Username FROM users WHERE id = ?;", session['user_id'])
    user_name = name[0]['Username']

    if quest_num is None:
        quest_num = request.form.get("question")

    questions = db.execute("""
                            SELECT Year,
                                    Prob_No,
                                    Question,
                                    Alt_1,
                                    Alt_2,
                                    Alt_3,
                                    Alt_4,
                                    Alt_5,
                                    Choice_1,
                                    Choice_2,
                                    Choice_3,
                                    Choice_4,
                                    Correct_Ans,
                                    Explanation
                                FROM Problems
                                WHERE Year = ?
                                AND Prob_No = ?;""", year, quest_num)

    if not questions:
        flash("🎩Select a year Mr. Wonka!🎩")
        return redirect("/", 400)

    alts = 0
    for alt in range(5):

        opt = 'Alt_'+str(alt+1)
        if questions[0][opt]:
            alts += 1

    question_entry = {
        'Year': questions[0]['Year'],
        'Prob_No': questions[0]['Prob_No'],
        'Question': questions[0]['Question'],
        'Alt_1': questions[0]['Alt_1'],
        'Alt_2': questions[0]['Alt_2'],
        'Alt_3': questions[0]['Alt_3'],
        'Alt_4': questions[0]['Alt_4'],
        'Alt_5': questions[0]['Alt_5'],
        'Choice_1': questions[0]['Choice_1'],
        'Choice_2': questions[0]['Choice_2'],
        'Choice_3': questions[0]['Choice_3'],
        'Choice_4': questions[0]['Choice_4'],
        'Correct_Ans': questions[0]['Correct_Ans'],
        'Link': questions[0]['Explanation']
    }

    total_tries = db.execute(
        "SELECT COUNT(*) FROM results WHERE user_id = ? AND year = ? AND quest_num = ?", user_name, int(year), int(quest_num))
    total_correct = db.execute(
        "SELECT COUNT(*) FROM results WHERE user_id = ? AND year = ? AND quest_num = ? AND mark = 1", user_name, int(year), int(quest_num))

    if not total_tries[0]['COUNT(*)']:
        pct_score = -1
    elif not total_correct[0]['COUNT(*)']:
        pct_score = 0
    else:
        pct_score = total_correct[0]['COUNT(*)']/total_tries[0]['COUNT(*)'] * 100

    latest_ten = db.execute(
        "SELECT date, mark FROM results WHERE user_id = ? AND year = ? AND quest_num = ? ORDER BY date DESC LIMIT 10", user_name, int(year), int(quest_num))
    latest_ten_len = len(latest_ten)

    # Update object for each question to include accuracy% for conditional styling of background colour
    matrix_arr = []
    for yr in range(sy, (sy+ty)):
        for qt in range(sq, (sq+tq)):
            temp_obj = {"year": yr, "quest_num": qt, "accuracy": "grey_bg", "max(id)": None}
            matrix_arr.append(temp_obj)

    accuracy = db.execute(
        "SELECT year, quest_num, accuracy, max(id) FROM results WHERE user_id = ? GROUP BY year, quest_num;", user_name)

    for i in matrix_arr:
        for j in accuracy:
            if i['year'] == j['year'] and i['quest_num'] == j['quest_num']:
                i['accuracy'] = j['accuracy']
                if int(i['accuracy']) > 75:
                    i['accuracy'] = "green_bg"
                elif int(i['accuracy']) > 50:
                    i['accuracy'] = "yellow_bg"
                elif int(i['accuracy']) >= 0:
                    i['accuracy'] = "red_bg"
                else:
                    i['accuracy'] = "grey_bg"

    return render_template("years.html", question_entry=question_entry, alts=alts, pct_score=str(round(pct_score))+" %", latest_ten=latest_ten, latest_ten_len=latest_ten_len, def_year=year, def_quest=quest_num, matrix_arr=matrix_arr,  ty=ty, sy=sy, tq=tq, sq=sq)


@app.route("/submit", methods=["POST"])
@login_required
def submit():
    """Submit answer for testing"""

    name = db.execute("SELECT Username FROM users WHERE id = ?;", session['user_id'])
    user_name = name[0]['Username']

    answer = request.form.get("ans_button")

    year = request.form.get("q_year")

    quest_num = request.form.get("q_num")

    questions = db.execute("""
                           SELECT Year,
                                  Prob_No,
                                  Question,
                                  Alt_1,
                                  Alt_2,
                                  Alt_3,
                                  Alt_4,
                                  Alt_5,
                                  Choice_1,
                                  Choice_2,
                                  Choice_3,
                                  Choice_4,
                                  Correct_Ans,
                                  Explanation
                             FROM Problems
                            WHERE Year = ?
                              AND Prob_No = ?;""", year, quest_num)

    question_entry = {
        'Year': questions[0]['Year'],
        'Prob_No': questions[0]['Prob_No'],
        'Question': questions[0]['Question'],
        'Alt_1': questions[0]['Alt_1'],
        'Alt_2': questions[0]['Alt_2'],
        'Alt_3': questions[0]['Alt_3'],
        'Alt_4': questions[0]['Alt_4'],
        'Alt_5': questions[0]['Alt_5'],
        'Choice_1': questions[0]['Choice_1'],
        'Choice_2': questions[0]['Choice_2'],
        'Choice_3': questions[0]['Choice_3'],
        'Choice_4': questions[0]['Choice_4'],
        'Correct_Ans': questions[0]['Correct_Ans'],
        'Link': questions[0]['Explanation']
    }

    alts = 0
    for alt in range(5):
        opt = 'Alt_'+str(alt+1)
        if questions[0][opt]:
            alts += 1

    date = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
    mark = 0
    response = None
    if int(answer) == questions[0]['Correct_Ans']:
        mark = 1
        response = "Correct"
    else:
        response = "Incorrect"

    last_id = db.execute("INSERT INTO results(user_id, year, quest_num, date, mark) VALUES (?, ?, ?, ?, ?)",
                         user_name, int(year), int(quest_num), date, mark)

    total_tries = db.execute(
        "SELECT COUNT(*) FROM results WHERE user_id = ? AND year = ? AND quest_num = ?", user_name, int(year), int(quest_num))
    total_correct = db.execute(
        "SELECT COUNT(*) FROM results WHERE user_id = ? AND year = ? AND quest_num = ? AND mark = 1", user_name, int(year), int(quest_num))

    pct_score = total_correct[0]['COUNT(*)']/total_tries[0]['COUNT(*)'] * 100

    db.execute("UPDATE results SET accuracy = ? WHERE id = ? ", pct_score, last_id)

    latest_ten = db.execute(
        "SELECT date, mark FROM results WHERE user_id = ? AND year = ? AND quest_num = ? ORDER BY date DESC LIMIT 10", user_name, int(year), int(quest_num))
    latest_ten_len = len(latest_ten)

    # Update object for each question to include accuracy% for conditional styling of background colour
    matrix_arr = []
    for yr in range(sy, (sy+ty)):
        for qt in range(sq, (sq+tq)):
            temp_obj = {"year": yr, "quest_num": qt, "accuracy": "grey_bg", "max(id)": None}
            matrix_arr.append(temp_obj)

    accuracy = db.execute(
        "SELECT year, quest_num, accuracy, max(id) FROM results WHERE user_id = ? GROUP BY year, quest_num;", user_name)

    # Colour results in User's result history matrix according to cummulative preformance of previous attempts
    for i in matrix_arr:
        for j in accuracy:
            if i['year'] == j['year'] and i['quest_num'] == j['quest_num']:
                i['accuracy'] = j['accuracy']
                if int(i['accuracy']) > 75:
                    i['accuracy'] = "green_bg"
                elif int(i['accuracy']) > 50:
                    i['accuracy'] = "yellow_bg"
                elif int(i['accuracy']) >= 0:
                    i['accuracy'] = "red_bg"
                else:
                    i['accuracy'] = "grey_bg"

    return render_template("years.html", question_entry=question_entry, alts=alts, mark=mark, pct_score=str(round(pct_score))+" %", latest_ten=latest_ten, latest_ten_len=latest_ten_len, response=response, def_year=year, def_quest=quest_num, matrix_arr=matrix_arr, ty=ty, sy=sy, tq=tq, sq=sq)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username") or not request.form.get("password"):
            flash(
                f"Please enter both Username and Password")
            return redirect("/login", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE Username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash(
                f"Please enter a valid Username and Password")
            return redirect("/login", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["ID"]
        session["username"] = rows[0]["Username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        question_entry = {
            'Year': "Year",
            'Prob_No': "#",
            'Question': "Select a year and question above...",
            'Alt_1': None,
            'Alt_2': None,
            'Alt_3': None,
            'Alt_4': None,
            'Alt_5': None,
            'Choice_1': " ",
            'Choice_2': " ",
            'Choice_3': " ",
            'Choice_4': " ",
            'Correct_Ans': " ",
            'Link': " "
        }

        alts = 0

        return render_template("login.html", question_entry=question_entry, alts=alts)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("username")
        pass1 = request.form.get("password")
        pass2 = request.form.get("confirmation")
        if not name or not pass1 or not pass2:
            flash('Please enter all required fields')
            return redirect("/register", 400)

        name_exists = db.execute("SELECT * FROM Users WHERE Username = ?", name)

        if not name:
            flash('Please enter a username')
            return redirect("/register", 400)
        if pass1 != pass2:
            flash('Passwords do not match')
            return redirect("/register", 400)
        if name_exists:
            flash('Username "' + name + '" already in use. Please enter a new username')
            return redirect("/register", 400)

        hashed_pass = generate_password_hash(pass1, method='scrypt', salt_length=16)

        db.execute("INSERT INTO Users (Username, hash) VALUES (?, ?)", name, hashed_pass)

        question_entry = {
            'Year': "Year",
            'Prob_No': "#",
            'Question': "Select a year and question above...",
                        'Alt_1': None,
                        'Alt_2': None,
                        'Alt_3': None,
                        'Alt_4': None,
                        'Alt_5': None,
                        'Choice_1': " ",
                        'Choice_2': " ",
                        'Choice_3': " ",
                        'Choice_4': " ",
                        'Correct_Ans': " ",
                        'Link': " "
        }
        alts = 0

        return render_template("login.html", question_entry=question_entry, alts=alts, name=name)
