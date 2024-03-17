import io
import logging
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, Response, abort, flash, redirect, url_for
from toudou.models import create_todo, get_all_todos, delete_todo, get_todo, update_todo, init_db
from toudou.services import import_from_csv, get_string_csv
from toudou.form import MyForm
todo_blueprint = Blueprint("todo_blueprint", __name__, url_prefix="/")
@todo_blueprint.route("/")
def accueil():
    init_db()
    abort(500)
    return render_template("accueil.html")

@todo_blueprint.route("/create", methods=["GET", "POST"])
def create():
    form = MyForm()
    if request.method == "GET":
        return render_template("create.html", error=None, requete="GET",form=form)
    elif form.validate_on_submit():
        tache = form.nameTodo.data
        complete = form.etat.data
        complete = complete.lower() == "true"
        date = form.date.data
        error = create_todo(tache, complete, date)
        return render_template("create.html", error=error, requete="POST",form=form)
    return render_template("create.html", error="ntm", requete="POST",form=form)

@todo_blueprint.route("/todos", methods=["GET"])
def afficher_todos():
    listTodos = get_all_todos()
    if isinstance(listTodos, str):
        error = listTodos
        return render_template("todos.html", error=error, listTodos=[])
    else:
        return render_template("todos.html", error=None, listTodos=listTodos)

@todo_blueprint.route("/delete", methods=["GET", "POST"])
def delete_todos():
    listTodos = get_all_todos()
    if isinstance(listTodos, str):
        error = listTodos
        return render_template("delete.html", error=error, listTodos=[], requete="GET")
    requete = request.method
    if requete == "POST":
        donnees = request.form
        id = uuid.UUID(donnees["toudouId"])
        delete_todo(id)
        listTodos = get_all_todos()
        return render_template("delete.html", error=None, listTodos=listTodos, requete="POST")
    return render_template("delete.html", error=None, listTodos=listTodos, requete="GET")

@todo_blueprint.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "GET":
        listTodos = get_all_todos()
        errorList = None
        if isinstance(listTodos, str):
            errorList = listTodos
        return render_template("update.html", errorUpdate=None, errorList=errorList, listTodos=listTodos, requete="GET")
    else:
        donnees = request.form
        id = uuid.UUID(donnees["toudouId"])
        tache = donnees['tache']
        complete = donnees['complete']
        complete = complete.lower() == "true"
        date = donnees['date']
        todo = get_todo(id)
        if date:
            date = datetime.strptime(date, "%Y-%m-%d")
        else:
            date = todo.due
        if not tache:
            tache = todo.task
        errorUpdate = update_todo(id, tache, complete, date)
        listTodos = get_all_todos()
        errorList = None
        if isinstance(listTodos, str):
            errorList = listTodos
            listTodos = []
        return render_template("update.html", errorUpdate=errorUpdate, errorList=errorList, listTodos=listTodos, requete="POST")

@todo_blueprint.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    try:
        if request.method == 'POST':
            csv_file = request.files['file']
            csv_file_stream = io.TextIOWrapper(csv_file, encoding='utf-8')
            import_from_csv(csv_file_stream)
            return render_template("importCsv.html", requete="POST", error=None)
        else:
            return render_template("importCsv.html", requete="GET", error=None)
    except Exception as e:
        return render_template("importCsv.html", requete="POST", error=str(e))

@todo_blueprint.route('/download_csv', methods=["GET", "POST"])
def download_csv():
    if request.method == "POST":
        csv_data = get_string_csv()
        response = Response(csv_data, content_type='text/csv')
        response.headers["Content-Disposition"] = "attachment; filename=toudous.csv"
        return response
    else:
        return render_template("downloadCsv.html")

@todo_blueprint.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    logging.exception(error)
    return render_template("accueil.html")