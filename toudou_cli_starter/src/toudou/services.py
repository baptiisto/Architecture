import csv
import dataclasses
import io

from datetime import datetime

from toudou.models import create_todo, get_all_todos, Todo


def export_to_csv() -> io.StringIO:
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output,
        fieldnames=[f.name for f in dataclasses.fields(Todo) if f.name != 'id']
    )
    csv_writer.writeheader()
    for todo in get_all_todos():
        todo_dict = {f.name: getattr(todo, f.name) for f in dataclasses.fields(Todo) if f.name != 'id'}
        csv_writer.writerow(todo_dict)
    return output


def import_from_csv(csv_file:io.TextIOWrapper) -> None:
        csv_file.seek(0)
        csv_reader = csv.DictReader(
            csv_file,
            fieldnames=["task", "complete", "due"]
        )
        for row in csv_reader:
            print(row)
            create_todo(
                task=row["task"],
                due=datetime.fromisoformat(row["due"]) if row["due"] else None,
                complete=row["complete"] == "True"
            )
def get_string_csv():
    csv_data = export_to_csv()
    csv_data.seek(0)
    csv_data = csv_data.read()

    return csv_data