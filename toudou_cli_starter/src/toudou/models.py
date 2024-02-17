from __future__ import annotations

import os
import uuid

from dataclasses import dataclass
from datetime import datetime
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, String, Uuid, Boolean, DateTime

TODO_FOLDER = "db"
BASE_DE_DONNEES ="toudou.db"
NOM_TABLE = "TODOS"

@dataclass
class Todo:
    id: uuid.UUID
    task: str
    complete: bool
    due: datetime | None


def init_connexion() -> None:
    engine = create_engine("sqlite:///db/todos.db", echo=True)
    return engine

def init_db():
    os.makedirs(TODO_FOLDER, exist_ok=True)
    engine = init_connexion()
    metadata_obj = MetaData()
    todosTable= Table(
    NOM_TABLE,
    metadata_obj,
        Column("id", Uuid, primary_key=True, default=uuid.uuid4),
        Column("task", String, nullable=False),
        Column("complete", Boolean, nullable=False),
        Column("due", DateTime, nullable=True))
    metadata_obj.create_all(engine)


def create_todo(
    task: str,
    complete: bool = False,
    due: datetime | None = None
) -> None:
    todo = Todo(uuid.uuid4(), task=task, complete=complete, due=due)
    con = init_connexion()
    cur = con.cursor()
    if due is not None:
        due = datetime.strftime(due, "%Y-%m-%d")
    try:
        cur.execute("INSERT INTO TODOS (id, task, completed, date) VALUES (?, ?, ?, ?)",
        (str(todo.id), todo.task, todo.complete, due))
    except sqlite3.Error as e:
        print(f"Erreur:{e}")
    commit_and_close_connection(con)

def get_todo(id: uuid.UUID) -> Todo:
    con = init_connexion()
    cur = con.cursor()
    try:
        cur.execute(f"SELECT * FROM TODOS WHERE id ='{id}'")
    except sqlite3.Error as e:
        print(f"Erreur:{e}")
    result = cur.fetchone()
    con.close()
    todo = creer_todo(result)
    return todo

def get_all_todos() -> list[Todo]:
    tab_todos = []
    con = init_connexion()
    cur = con.cursor()
    try:
        cur.execute(f"SELECT * FROM TODOS")
    except sqlite3.Error as e:
        print(f"Erreur:{e}")
    result = cur.fetchall()
    con.close()
    for row in result:
        todo = creer_todo(row)
        if todo:
            tab_todos.append(todo)
    return tab_todos

def update_todo(
    id: uuid.UUID,
    task: str,
    complete: bool,
    due: datetime | None
) -> None:
    if get_todo(id):
        con = init_connexion()
        cur = con.cursor()
        if due:
            try:
                cur.execute(f"UPDATE TODOS SET task= '{task}', completed='{complete}',date='{due}'WHERE id = '{id}' ")
            except sqlite3.Error as e:
                print(f"Erreur:{e}")
        else:
            try:
                cur.execute(f"UPDATE TODOS SET task= '{task}', completed='{complete}' WHERE id = '{id}' ")
            except sqlite3.Error as e:
                print(f"Erreur:{e}")
        commit_and_close_connection(con)

def delete_todo(id: uuid.UUID) -> None:
    con = init_connexion()
    cur = con.cursor()
    try:
        cur.execute(f"DELETE FROM TODOS WHERE id ='{id}'")
    except sqlite3.Error as e:
        print(f"Erreur:{e}")
    commit_and_close_connection(con)
def creer_todo(result: tuple) -> Todo :
    if result:
        id = result[0]
        task = result[1]
        completed = result[2]
        date = result[3]

        if date:
            date = datetime.strptime(date, "%Y-%m-%d")

        todo = Todo(id,task,completed,date)
        return todo
    else:
        print("Id inconnu")
def commit_and_close_connection(con :sqlite3.Connection):
    con.commit()
    con.close()

