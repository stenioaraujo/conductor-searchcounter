import sqlite3

import click

from conductor_searchcounter.counter import SearchCounter
from conductor_searchcounter.dao import DAOSqlite


@click.group()
@click.option("--database", required=True,
              help="Path to the sqlite database that will be used "
              "for persistence. The file does not need to exist",
              metavar="FILENAME", type=click.Path(), show_default=True)
@click.pass_context
def cli(ctx, database):
    ctx.ensure_object(dict)

    ctx.obj["DATABASE"] = database


@cli.command(short_help="Add a search to the collection")
@click.option("--term", "terms", required=True, multiple=True,
              help="Terms to be used when creating a search")
@click.pass_context
def increment(ctx, terms):
    with sqlite3.connect(ctx.obj["DATABASE"]) as conn:
        dao = DAOSqlite(conn)
        sc = SearchCounter(terms, dao)

        sc.increment()


@cli.command(short_help="Query the collection to return the number of "
             "searches made in the past minute")
@click.pass_context
def num_last_minute(ctx):
    with sqlite3.connect(ctx.obj["DATABASE"]) as conn:
        dao = DAOSqlite(conn)
        sc = SearchCounter([], dao)

        click.echo(sc.num_last_minute())


@cli.command(short_help="Query the number of searches made in the last "
             "seconds")
@click.argument("seconds", type=int)
@click.pass_context
def num_arbitrary_lookback(ctx, seconds):
    with sqlite3.connect(ctx.obj["DATABASE"]) as conn:
        dao = DAOSqlite(conn)
        sc = SearchCounter([], dao)

        click.echo(sc.num_arbitrary_lookback(seconds))


@cli.command(short_help="Query the most commonly searched term in the past "
             "seconds")
@click.argument("seconds", type=int)
@click.pass_context
def most_common_term(ctx, seconds):
    with sqlite3.connect(ctx.obj["DATABASE"]) as conn:
        dao = DAOSqlite(conn)
        sc = SearchCounter([], dao)

        most_common = sc.most_common_term(seconds)
        if most_common:
            click.echo(most_common)


def main():
    try:
        cli(obj={}, auto_envvar_prefix='CONDUCTOR_SEARCHCOUNTER')
    except Exception as e:
        click.echo(e, err=True)


if __name__ == "__main__":
    main()
