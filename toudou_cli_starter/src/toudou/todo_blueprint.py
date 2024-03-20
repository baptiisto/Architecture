import io
import logging
from sqlalchemy.exc import OperationalError

from wtforms import ValidationError
from flask import Blueprint, render_template, request, Response, abort, flash, redirect, url_for
from toudou.models import create_todo, get_all_todos, delete_todo, get_todo, update_todo, init_db
from toudou.services import import_from_csv, get_string_csv
from toudou.form import FormCreate , FormDelete , FormUpdate,FormImport
todo_blueprint = Blueprint("todo_blueprint", __name__, url_prefix="/")
@todo_blueprint.route("/")
def accueil():
    init_db()
    return render_template("accueil.html")

@todo_blueprint.route("/create", methods=["GET", "POST"])
def create():
    form = FormCreate()
    if request.method == "GET":
        return render_template("create.html", requete="GET",form=form)
    elif form.validate_on_submit():
        tache = form.nameTodo.data
        complete = form.etat.data
        complete = complete.lower() == "true"
        date = form.date.data
        create_todo(tache, complete, date)
        return render_template("create.html", requete="POST",form=form)
    else:
        raise ValidationError("Formulaire invalide")

@todo_blueprint.route("/todos", methods=["GET"])
def afficher_todos():
    listTodos = get_all_todos()
    return render_template("todos.html", listTodos=listTodos)

@todo_blueprint.route("/delete", methods=["GET", "POST"])
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
            return render_template("delete.html", requete="POST",form=form)
        else:
            raise ValidationError("Formulaire invalide")
    else:
        return render_template("delete.html", requete="GET",form=form)

@todo_blueprint.route("/update", methods=["GET", "POST"])
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
            raise ValidationError("Formulaire invalide")
    else:
        return render_template("update.html", form=form, requete="GET")
@todo_blueprint.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    form = FormImport()
    if request.method == "POST":
        if form.validate_on_submit():
            csv_file = form.csv_file.data
            import_from_csv(csv_file.stream)
            return render_template("importCsv.html", form=form, requete="POST")
        else:
            raise ValidationError("Formulaire invalide")

    return render_template("importCsv.html", form=form, requete="GET")


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