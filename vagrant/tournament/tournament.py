#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import bleach
import psycopg2


def run_query(statement, params=None):
    '''Helper method to run queries'''
    conn = connect()
    cur = conn.cursor()
    cur.execute(statement, params)
    conn.commit()
    conn.close()


def run_query_one(statement, params=None):
    '''Helper method to run queries that return one result'''
    conn = connect()
    cur = conn.cursor()
    cur.execute(statement, params)
    result = cur.fetchone()[0]
    conn.close()
    return result


def run_query_args(statement, params=None):
    '''Helper function for queries that return multiple columns'''
    conn = connect()
    cur = conn.cursor()
    cur.execute(statement, params)
    results = cur.fetchall()
    conn.close()
    return results


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    run_query("DELETE FROM match")


def deletePlayers():
    """Remove all the player records from the database."""
    run_query("DELETE FROM players")


def countPlayers():
    """Returns the number of players currently registered."""
    return run_query_one("SELECT COUNT(*) FROM players")


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    scrubbed_name = bleach.clean(name)
    run_query("INSERT INTO players (name) VALUES (%s)", (scrubbed_name, ))


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
    return run_query_args(
        "SELECT * FROM standings ORDER BY wins DESC, matches ASC")


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    run_query("INSERT INTO match(winner, loser) VALUES (%s, %s)",
              (winner, loser))


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
        pair = ((standings[player][0], standings[player][1],
                 standings[player + 1][0], standings[player + 1][1]))
        pairings.append(pair)

    return pairings
