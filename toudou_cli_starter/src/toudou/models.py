from __future__ import annotations

import os
import uuid

from dataclasses import dataclass
from datetime import datetime
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, String, Uuid, Boolean, DateTime, select, update, delete

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
def init_db():
    engine, metadata_obj, todosTable = init_connexion()
    os.makedirs(TODO_FOLDER, exist_ok=True)

    #if table_existante is None:
    metadata_obj.create_all(engine)
    #else:
        #print("La table existe déjà")

def create_todo(
    task: str,
    complete: bool = False,
    due: datetime | None = None
) -> None:
    engine, metadata_obj, todosTable = init_connexion()
    stmt = todosTable.insert().values(
        task=task,
        complete=complete,
        due=due
    )
    with engine.begin() as conn:
        result = conn.execute(stmt)

def get_todo(id: uuid.UUID) -> Todo:
    engine, metadata_obj, todosTable = init_connexion()
    stmt = select(todosTable).where(todosTable.c.id == id)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        row = result.fetchone()

    todo = creer_todo(row)
    return todo

def get_all_todos() -> list[Todo]:
    tab_todos = []
    engine, metadata_obj, todosTable = init_connexion()
    stmt = select(todosTable)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        rows = result.fetchall()
    for row in rows:
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
        engine, metadata_obj, todosTable = init_connexion()
        if due:
            smt = update(todosTable).where(todosTable.c.id == id).values(task=task,complete =complete, due=due)
        else:
            smt = update(todosTable).where(todosTable.c.id == id).values(task=task, complete=complete, due=due)
        with engine.begin() as conn:
            result = conn.execute(smt)

def delete_todo(id: uuid.UUID) -> None:
    engine, metadata_obj, todosTable = init_connexion()
    smt = delete(todosTable).where(todosTable.c.id == id)
    with engine.begin() as conn:
        result = conn.execute(smt)
def creer_todo(result: tuple) -> Todo :
    if result:
        id = result[0]
        task = result[1]
        completed = result[2]
        date = result[3]

        todo = Todo(id,task,completed,date)
        return todo
    else:
        print("Id inconnu")
def commit_and_close_connection(con :sqlite3.Connection):
    con.commit()
    con.close()

