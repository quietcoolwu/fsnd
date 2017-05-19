#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

from __future__ import absolute_import, unicode_literals

import bleach
import psycopg2


def connect(db_name="tournament"):
    """Connect to the PostgreSQL DB by db_name.
    Returns a DB connection and current cursor.

    Args:
      db_name: the existed DB's name, or raise SystemExit.
    """
    try:
        db = psycopg2.connect("dbname={}".format(db_name))
        cursor = db.cursor()
        return db, cursor
    except Exception as e:
        raise SystemExit("DB Connection Error: ", e)


def deleteMatches():
    """Remove all the match records from the database."""
    db, cursor = connect()

    query = r"TRUNCATE match CASCADE;"
    cursor.execute(query, None)

    db.commit()
    db.close()
    return


def deletePlayers():
    """Remove all the player records from the database."""
    db, cursor = connect()

    query = r"TRUNCATE players CASCADE;"
    cursor.execute(query, None)

    db.commit()
    db.close()
    return


def countPlayers():
    """Returns the number of players currently registered."""
    db, cursor = connect()

    query = r"SELECT COUNT(*) FROM players;"
    cursor.execute(query, None)
    result = cursor.fetchall()[0][0]

    db.close()
    return result


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL DB schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db, cursor = connect()

    query = r"INSERT INTO players (name) VALUES (%s);"
    # Use for cleaning data from external resource like HTML forms.
    name = bleach.clean(name)
    parameter = (name, )
    cursor.execute(query, parameter)

    db.commit()
    db.close()
    return


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db, cursor = connect()

    query = r"SELECT * FROM standings ORDER BY wins DESC, matches ASC;"
    cursor.execute(query, None)
    result = cursor.fetchall()

    db.close()
    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db, cursor = connect()

    query = r"INSERT INTO match(winner, loser) VALUES (%s, %s);"
    parameter = (winner, loser)
    cursor.execute(query, parameter)

    db.commit()
    db.close()
    return


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    total_players = len(standings)
    pairings = []

    for player in range(0, total_players, 2):
        pair = (standings[player][0], standings[player][1],
                standings[player + 1][0], standings[player + 1][1])
        pairings.append(pair)

    return pairings
