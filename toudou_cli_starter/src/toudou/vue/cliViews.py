import click
import uuid

from datetime import datetime
from sqlalchemy.exc import OperationalError
import toudou.models as models
import toudou.services as services


@click.group()
def cli():
    pass
@cli.command()
def init_db():
    models.init_db()

@cli.command()
@click.option("-t", "--task", prompt="Your task", help="The task to remember.")
@click.option("-d", "--due", type=click.DateTime(formats=["%Y-%m-%d"]), default=None, help="Due date of the task.")
def create(task: str, due: datetime):
    try:
        models.create_todo(task, due=due)
    except OperationalError as e:
        print(str(e))



@cli.command()
@click.option("--id", required=True, type=click.UUID, help="Todo's id.")
def get(id: uuid.UUID):
    try:
        click.echo(models.get_todo(id))
    except OperationalError as e:
        print(str(e))
    except ValueError as ve:
        print(str(ve))


@cli.command()
@click.option("--as-csv", is_flag=True, help="Ouput a CSV string.")
def get_all(as_csv: bool):
    try:
        if as_csv:
            click.echo(services.export_to_csv().getvalue())
        else:
            click.echo(models.get_all_todos())
    except OperationalError as e:
        print(str(e))


@cli.command()
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    try:
        services.import_from_csv(csv_file)
    except Exception as e:
        print(str(e))


@cli.command()
@click.option("--id", required=True, type=click.UUID, help="Todo's id.")
@click.option("-c", "--complete", required=True, type=click.BOOL, help="Todo is done or not.")
@click.option("-t", "--task", prompt="Your task", help="The task to remember.")
@click.option("-d", "--due",type=click.DateTime(formats=["%Y-%m-%d"]), default=None, help="Due date of the task.")
def update(id: uuid.UUID, complete: bool, task: str, due: datetime):
    try:
        models.update_todo(id, task, complete, due)
    except OperationalError as e:
        print(str(e))
    except ValueError as ve:
        print(str(ve))


@cli.command()
@click.option("--id", required=True, type=click.UUID, help="Todo's id.")
def delete(id: uuid.UUID):
    try:
        models.delete_todo(id)
    except OperationalError as e:
        print(str(e))
    except ValueError as ve:
        print(str(ve))
