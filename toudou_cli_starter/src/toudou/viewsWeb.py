from flask import Flask, render_template, request
from toudou.models import create_todo, get_all_todos
from datetime import datetime


app = Flask(__name__)

@app.route("/")
def hello():
        return render_template("create.html")
@app.route("/create", methods=["GET", "POST"])
def create():
    requete = request.method
    if requete =="GET":
        return render_template("create.html",error=None,requete=requete)
    else:
        donnees = request.form
        tache = donnees['tache']
        complete = bool(donnees['complete'])
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
        print(1)
        return render_template("todos.html", error=error,listTodos=[])
    else:
        print(2)
        return render_template("todos.html", error=None, listTodos=listTodos)





if __name__ == "__main__":
    app.run(debug=True)