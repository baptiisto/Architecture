from __future__ import annotations

import os
import uuid

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, String, Uuid, Boolean, DateTime, select, update, delete
from sqlalchemy.exc import OperationalError

TODO_FOLDER = "db"
BASE_DE_DONNEES ="toudous.db"
NOM_TABLE = "TODOS"
STR_OPERATIONAL_ERROR = "Table Todos Inconnu"


@dataclass
class Todo:
    id: uuid.UUID
    task: str
    complete: bool
    due: datetime | None

def init_connexion() -> tuple:
    """
        Initialise Les objets nécessaires pour les opérations sur la base de données .

        :return:
        tuple : Un tuple contenant les objets suivants :
            - (Engine)engine : objet pour se connecter  à la base de données.
            - (MetaData)metadata_obj :  représente le schéma de la base de données.
            - (Table) todosTable :   table todos, elle a comme colonne (id,task,complete,due)
    """

    engine = create_engine(f"sqlite:///{TODO_FOLDER}/{BASE_DE_DONNEES}", echo=True)
    metadata_obj = MetaData()

    todosTable = Table(
        NOM_TABLE,
        metadata_obj,
        Column("id", Uuid, primary_key=True, default=uuid.uuid4()),
        Column("task", String, nullable=False),
        Column("complete", Boolean, nullable=False),
        Column("due", DateTime, nullable=True)
    )
    return engine,metadata_obj,todosTable
def init_db() -> None:
    """
    Cette fonction crée la table Todos dans la base de données
    """

    engine, metadata_obj, todosTable = init_connexion()
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

    engine, metadata_obj, todosTable = init_connexion()
    try:
        stmt = todosTable.insert().values(
            task=task,
            complete=complete,
            due=due
        )
        with engine.begin() as conn:
            result = conn.execute(stmt)
    except OperationalError:
        print(STR_OPERATIONAL_ERROR)


def get_todo(id: uuid.UUID) -> Todo | str:
    """
    Récupere une Todo dans la base de données à partir de l'id fournit par l'utilisateur

    :param id: l'id de la Todo qu'on veut récupérer
    :return: (TODO) todo correspondant à l'iut ou (STR) si il y a une erreur
    """

    engine, metadata_obj, todosTable = init_connexion()
    try:
        count_rows(id)
    except OperationalError:
        return STR_OPERATIONAL_ERROR
    except ValueError as ve:
        return str(ve)

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
    engine, metadata_obj, todosTable = init_connexion()
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
        return STR_OPERATIONAL_ERROR

def update_todo(
    id: uuid.UUID,
    task: str,
    complete: bool,
    due: datetime | None
) -> None:
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
        print(STR_OPERATIONAL_ERROR)
        return None
    except ValueError as ve:
        print(str(ve))
        return None

    engine, metadata_obj, todosTable = init_connexion()
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
        print(STR_OPERATIONAL_ERROR)
        return None
    except ValueError as ve:
        print(str(ve))
        return None

    engine, metadata_obj, todosTable = init_connexion()
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

    engine, metadata_obj, todosTable = init_connexion()
    stmt = select(todosTable).where(todosTable.c.id == id)
    try:
        with engine.connect() as connection:
            result = connection.execute(stmt)
            rows = result.fetchall()
            if not rows:
                raise ValueError("ID Inconnu")
            return len(rows)
    except OperationalError as e:
        raise e