import uuid
import io

from flask import Flask, render_template, request ,Response
from toudou.models import create_todo, get_all_todos ,delete_todo, get_todo, update_todo
from toudou.services import import_from_csv ,get_string_csv
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def hello():
        return render_template("accueil.html")
@app.route("/create", methods=["GET", "POST"])
def create():
    requete = request.method
    if requete =="GET":
        return render_template("create.html",error=None,requete=requete)
    else:
        donnees = request.form
        tache = donnees['tache']
        complete = (donnees['complete'])
        complete = complete.lower() == "true"
        date = donnees['date']
        if date !="":
            date = datetime.strptime(date, "%Y-%m-%d")
        else:
            date = None
        error = create_todo(tache,complete,date)
        return render_template("create.html",error=error,requete=requete)

@app.route("/todos", methods=["GET"])
def afficher_todos():

    listTodos = get_all_todos()
    if type(listTodos) == str:
        error = listTodos
        return render_template("todos.html", error=error,listTodos=[])
    else:
        return render_template("todos.html", error=None, listTodos=listTodos)

@app.route("/delete",  methods=["GET", "POST"])
def delete_todos():

    listTodos = get_all_todos()

    if type(listTodos) == str:
        error = listTodos
        return render_template("delete.html", error=error,listTodos=[],requete="GET")

    requete = request.method

    if requete == "POST":
        donnees = request.form
        id =donnees["toudouId"]
        id = uuid.UUID(id)
        delete_todo(id)
        listTodos = get_all_todos()
        return render_template("delete.html", error=None, listTodos=listTodos, requete="POST")

    return render_template("delete.html", error=None, listTodos=listTodos, requete="GET")


@app.route("/update", methods=["GET", "POST"])
def update():
    requete = request.method
    if requete =="GET":
        listTodos = get_all_todos()
        errorList = None
        if type(listTodos) == str:
            errorList = listTodos
        return render_template("update.html",errorUpdate= None,errorList = errorList,listTodos=listTodos,requete="GET")
    else:
        donnees = request.form
        id = donnees["toudouId"]
        id = uuid.UUID(id)
        tache = donnees['tache']
        complete = donnees['complete']
        complete = complete.lower() == "true"
        date = donnees['date']

        todo = get_todo(id)
        if date !="":
            date = datetime.strptime(date, "%Y-%m-%d")
        else:
            date = todo.due
        if tache =="":
            tache = todo.task
        errorUpdate = update_todo(id,tache,complete,date)
        listTodos = get_all_todos()
        errorList = None
        if type(listTodos) == str:
            errorList = listTodos
            listTodos = []
            print(errorList)
        return render_template("update.html", errorUpdate=errorUpdate, errorList=errorList, listTodos=listTodos, requete=requete)


@app.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    try:
        if request.method == 'POST':
            csv_file = request.files['file']
            csv_file_stream = io.TextIOWrapper(csv_file, encoding='utf-8')
            import_from_csv(csv_file_stream)
            return  render_template("importCsv.html",requete="POST",error=None)
        else:
            return render_template("importCsv.html", requete="GET",error=None)
    except Exception as e:
            return render_template("importCsv.html", requete="POST", error=str(e))
from flask import redirect, url_for

@app.route('/download_csv',methods=["GET", "POST"])
def download_csv():
    if request.method == "POST":
        csv_data = get_string_csv()
        response = Response(csv_data, content_type='text/csv')
        response.headers["Content-Disposition"] = "attachment; filename=toudous.csv"
        return response
    else:
        return render_template("downloadCsv.html")
if __name__ == "__main__":
    app.run(debug=True)