from flask import Flask, render_template, request
from toudou.models import create_todo
from datetime import datetime


app = Flask(__name__)

@app.route("/")
def hello(name=None):
        return render_template("create.html", name=name)
@app.route("/create",methods=["POST"])
def create():
    donnees = request.form
    tache = donnees['tache']
    complete = bool(donnees['complete'])
    date = donnees['date']
    if date !="":
        date = datetime.strptime(date, "%Y-%m-%d")
    else:
        date = None
    create_todo(tache,complete,date)

    print(donnees)
    return "Creation du Toudou"

if __name__ == "__main__":
    app.run(debug=True)