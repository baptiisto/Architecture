from __future__ import annotations

import os
import uuid

from dataclasses import dataclass
from datetime import datetime
from toudou import config
from sqlalchemy import create_engine, MetaData, Table, Column, String, Uuid, Boolean, DateTime, select, update, delete
from sqlalchemy.exc import OperationalError

TODO_FOLDER = "db"
NOM_TABLE = "TODOS"
STR_OPERATIONAL_ERROR = "Table Todos Inconnu"

engine = create_engine(config["DATABASE_URL"], echo=config["DEBUG"])
metadata_obj = MetaData()

todosTable = Table(
    NOM_TABLE,
    metadata_obj,
    Column("id", Uuid, primary_key=True, default=uuid.uuid4()),
    Column("task", String, nullable=False),
    Column("complete", Boolean, nullable=False),
    Column("due", DateTime, nullable=True)
)
@dataclass
class Todo:
    id: uuid.UUID
    task: str
    complete: bool
    due: datetime | None


def init_db() -> None:
    """
    Cette fonction crée la table Todos dans la base de données
    """

    os.makedirs(TODO_FOLDER, exist_ok=True)
    metadata_obj.create_all(engine)

def create_todo(
    task: str,
    complete: bool = False,
    due: datetime | None = None
) -> None:
    """
    creé une Todo à partir des informations données par l'utilisateur

    :param task: (str)tache de la date du toudou
    :param complete: (boolean) indique si la tache est fini ou non
    :param due: (datetime) indique la date de l'évenement
    """

    try:
        stmt = todosTable.insert().values(
            task=task,
            complete=complete,
            due=due
        )
        with engine.begin() as conn:
            result = conn.execute(stmt)
    except OperationalError:
        raise (OperationalError(STR_OPERATIONAL_ERROR,params=None, orig=None))


def get_todo(id: uuid.UUID) -> Todo | str:
    """
    Récupere une Todo dans la base de données à partir de l'id fournit par l'utilisateur

    :param id: l'id de la Todo qu'on veut récupérer
    :return: (TODO) todo correspondant à l'iut ou (STR) si il y a une erreur
    """

    try:
        count_rows(id)
    except OperationalError:
        raise (OperationalError(STR_OPERATIONAL_ERROR, params=None, orig=None))
    except ValueError as ve:
        raise ValueError("Id inconnu")

    stmt = select(todosTable).where(todosTable.c.id == id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        row = result.fetchone()

    todo = creer_todo(row)
    return todo


def get_all_todos() -> list[Todo]| str:
    """
    Recupere toutes les Todos sur la base de données

    :return: list[Todo]  liste de tous les Todos
    """

    tab_todos = []
    stmt = select(todosTable)
    try:
        with engine.connect() as conn:
            result = conn.execute(stmt)
            rows = result.fetchall()
        for row in rows:
            todo = creer_todo(row)
            if todo:
                tab_todos.append(todo)
        return tab_todos
    except OperationalError:
        raise (OperationalError(STR_OPERATIONAL_ERROR,params=None, orig=None))

def update_todo(
    id: uuid.UUID,
    task: str,
    complete: bool,
    due: datetime | None
) -> None | str:
    """
    changer des champs d'un todo doné par l'utilisateur

    :param id: (uuid.UUID) id du Todo à mettre à jour
    :param task:(STR) tache du Todo à mettre à jour
    :param complete: (bool) indique si la tache terminée
    :param due: (datetime) date quand la tache doit etre faite
    """

    try:
        count_rows(id)
    except OperationalError:
        raise (OperationalError(STR_OPERATIONAL_ERROR, params=None, orig=None))
    except ValueError as ve:
        raise ValueError("Id inconnu")

    if due:
        smt = update(todosTable).where(todosTable.c.id == id).values(task=task,complete =complete, due=due)
    else:
        smt = update(todosTable).where(todosTable.c.id == id).values(task=task, complete=complete, due=due)
    with engine.begin() as conn:
        result = conn.execute(smt)

def delete_todo(id: uuid.UUID) -> None:
    """
    Enleve une Todo donné par l'utilisateur dans la base de données

    :param id: (uuid.UUID) id du Todo qui doit etre suprimé de la base de données
    """

    try:
        count_rows(id)
    except OperationalError:
        raise (OperationalError(STR_OPERATIONAL_ERROR, params=None, orig=None))
    except ValueError as ve:
        raise ValueError("Id inconnu")

    smt = delete(todosTable).where(todosTable.c.id == id)
    with engine.begin() as conn:
        result = conn.execute(smt)

def creer_todo(result: tuple) -> Todo :
    """
    Crée un Todo a partir des resultats de la requete sur la base de données

    :param result: (tuple) contient des champs d'une Todo
    """

    if result:
        id = result[0]
        task = result[1]
        completed = result[2]
        date = result[3]

        todo = Todo(id,task,completed,date)
        return todo

def count_rows(id:uuid.UUID) -> int:
    """
    Effectue un SELECT sur la table spécifiée et retourne le nombre de lignes résultantes.
.
    :return:
    - int: Le nombre de lignes résultantes de la requête SELECT.

    :raises:
    - OperationalError: Table inexistante.
    - ValueError : Id inconnu dans la base de données
    """

    stmt = select(todosTable).where(todosTable.c.id == id)
    try:
        with engine.connect() as connection:
            result = connection.execute(stmt)
            rows = result.fetchall()
            if not rows:
                raise ValueError("ID Inconnu")
            return len(rows)
    except OperationalError as e:
        raise (OperationalError(STR_OPERATIONAL_ERROR))