import io
import logging
from sqlalchemy.exc import OperationalError

from wtforms import ValidationError
from flask import Blueprint, render_template, request, Response, abort, flash, redirect, url_for, send_file
from toudou.models import create_todo, get_all_todos, delete_todo, get_todo, update_todo, init_db
from toudou.services import import_from_csv, export_to_csv
from toudou.form import FormCreate , FormDelete , FormUpdate,FormImport
from toudou.vue.viewsWeb import auth
todo_blueprint = Blueprint("todo_blueprint", __name__, url_prefix="/")
@todo_blueprint.route("/")
def accueil():
    init_db()
    return render_template("accueil.html")

@todo_blueprint.route("/create", methods=["GET", "POST"])
@auth.login_required(role="admin")

def create():
    form = FormCreate()
    if request.method == "GET":
        return render_template("create.html", requete="GET", form=form)
    elif form.validate_on_submit():
        tache = form.nameTodo.data
        complete = form.etat.data
        complete = complete.lower() == "true"
        date = form.date.data
        create_todo(tache, complete, date)
        return render_template("create.html", requete="POST", form=form)
    else:
        abort(ValidationError("Formulaire invalide"))

@todo_blueprint.route("/todos", methods=["GET"])
@auth.login_required(role=["user","admin"])
def afficher_todos():
    listTodos = get_all_todos()
    return render_template("todos.html", listTodos=listTodos)

@todo_blueprint.route("/delete", methods=["GET", "POST"])
@auth.login_required(role="admin")
def delete_todos():
    form = FormDelete()
    listTodos = get_all_todos()
    requete = request.method
    options = [(str(todo.id), todo.task) for todo in listTodos]
    form.select_field.choices = options
    if requete == "POST":
        if form.validate_on_submit():
            id = form.select_field.data
            delete_todo(id)
            listTodos = get_all_todos()
            options = [(str(todo.id), todo.task) for todo in listTodos]
            form.select_field.choices = options
            return render_template("delete.html", requete="POST", form=form)
        else:
            abort(ValidationError("Formulaire invalide"))
    else:
        return render_template("delete.html", requete="GET", form=form)

@todo_blueprint.route("/update", methods=["GET", "POST"])
@auth.login_required(role="admin")
def update():
    form = FormUpdate()

    # Récupérer les todos pour construire les options du formulaire
    listTodos = get_all_todos()
    options = [(str(todo.id), todo.task) for todo in listTodos]
    form.select_field.choices = options
    if request.method == "POST":
        if form.validate_on_submit():
            id = form.select_field.data
            tache = form.nameTodo.data
            complete = form.etat.data.lower() == "true"
            date = form.date.data

            # Récupérer la tâche à mettre à jour
            todo = get_todo(id)

            # Utiliser les valeurs par défaut si les champs ne sont pas renseignés dans le formulaire
            if not date:
                date = todo.due
            if not tache:
                tache = todo.task

            update_todo(id, tache, complete, date)

            listTodos = get_all_todos()
            options = [(str(todo.id), todo.task) for todo in listTodos]
            form.select_field.choices = options

            return render_template("update.html", form=form, requete="POST")
        else:
            abort(ValidationError("Formulaire invalide"))
    else:
        return render_template("update.html", form=form, requete="GET")
@todo_blueprint.route("/import_csv", methods=["GET", "POST"])
@auth.login_required(role="admin")
def import_csv():
    form = FormImport()
    if request.method == "POST":
        if form.validate_on_submit():
            csv_file = form.csv_file.data
            import_from_csv(csv_file.stream)
            return render_template("importCsv.html", form=form, requete="POST")
        else:
            abort(ValidationError("Formulaire invalide"))

    return render_template("importCsv.html", form=form, requete="GET")


@todo_blueprint.route('/download_csv', methods=["GET", "POST"])
@auth.login_required(role="admin")
def download_csv():
    if request.method == "POST":
        csv = export_to_csv()
        content_bytes = csv.getvalue().encode()
        bytes_io = io.BytesIO(content_bytes)
        return send_file(bytes_io, as_attachment=True, mimetype='application/octet-stream',download_name="toudous.csv")
    else:
        return render_template("downloadCsv.html")

@todo_blueprint.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    logging.exception(error)
    return render_template("accueil.html")

@todo_blueprint.errorhandler(ValidationError)
def handle_validation_error(e):
    flash("Formulaire invalide", 'error')
    return redirect(request.referrer)
@todo_blueprint.errorhandler(OperationalError)
def handle_operational_error(e):
    flash(str(e), 'error')
    return redirect(url_for('todo_blueprint.accueil'))
@todo_blueprint.errorhandler(ValueError)
def handle_operational_error(e):
    flash(str(e), 'error')
    return redirect(url_for('todo_blueprint.accueil'))