import click
from filesorter import *


@click.group()
def sort():
    pass


@sort.command()
@click.argument('source_path', type=click.Path(exists=True))
@click.argument('dest_path', type=click.Path(exists=True))
@click.option('--simulation', is_flag=True, type=click.BOOL, default=False)
def sortYear(source_path, dest_path, simulation=False):
    click.echo('Sorting by year ' + source_path + " "+dest_path)
    sortByYear(source_path, dest_path, simulation)


@sort.command()
@click.argument('source_path', type=click.Path(exists=True))
def list(source_path):
    print("Listing files in path {0}".format(source_path))
    listFiles(source_path)

@sort.command()
@click.argument('source_path', type=click.Path(exists=True))
def debug(source_path):
    debugFile(source_path)
    
if __name__ == '__main__':
    sort()
