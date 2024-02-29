from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def hello(name=None):
        return render_template("create.html", name=name)
@app.route("/create",methods=["POST"])
def create():
    donnees = request.form
    tache = donnees['tache']
    complete = donnees['complete']
    print(donnees)
    return "Creation du Toudou"

if __name__ == "__main__":
    app.run(debug=True)