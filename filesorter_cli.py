import click
from filesorter import *


@click.group()
def sort():
    pass


@sort.command()
@click.argument('source_path', type=click.Path(exists=True))
@click.argument('dest_path', type=click.Path(exists=True))
def sortYear(source_path, dest_path):
    click.echo('Sorting by year ' + source_path + " "+dest_path)
    sortByYear(source_path, dest_path)


@sort.command()
@click.argument('source_path', type=click.Path(exists=True))
def list(source_path):
    listFiles(source_path)


if __name__ == '__main__':
    sort()
