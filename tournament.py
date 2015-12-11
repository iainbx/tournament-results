#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import logging
import math
import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM matches;")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(id) FROM players;")
    row = c.fetchone()
    conn.close()
    return row[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO Players (name) VALUES (%s);", (name,))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records.

    The list is sorted by rank ascending and opponent match wins descending.
    Rank is calulated as player matches - wins - draws / 2.
    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains
        (id, name, wins, draws, played, byes, opponent_wins, rank):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        draws: the number of matches the player has drawn
        played: the number of matches the player has played
        byes: the number of byes the player was given
        opponent_wins: the number of matches the players opponents have won
        rank: the ranking of the player = played - wins - draws/2
    """
    conn = connect()
    c = conn.cursor()
    sql = """SELECT id, name, wins, draws, opponent_wins, played, byes, rank
                FROM standings ORDER BY rank, opponent_wins DESC;"""
    c.execute(sql)
    standings = c.fetchall()
    conn.close()
    return standings


def reportMatch(player1, player2, winner=None):
    """Records the outcome of a single match between two players.

    Args:
      player1:  the id number of the player 1
      player2:  the id number of the player 2
      winner:   the id number of the player who won, or None for a draw
    """
    conn = connect()
    c = conn.cursor()
    sql = "INSERT INTO matches (player1,player2,winner) VALUES (%s,%s,%s);"
    c.execute(sql, (player1, player2, winner))
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Each player appears in only one pairing.
    Each player is paired with another player with an equal or nearly-equal
    win record, that is, a player adjacent to him or her in the standings.
    No player rematches are allowed.
    If there is an odd number of players, the lowest ranking player,
    that has not yet received a bye in a previous round, is given a bye.
    The bye player is added to the pairings list as a player who plays himself.
    If the lowest rank cannot be given a bye because it stops a complete set
    of pairings from being made, then the next lowest rank without a previous bye
    is attempted, and so on.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    # Create list for pairings.
    pairs = []

    player_count = countPlayers()

    # The number of pairs needed for a complete set that includes every player.
    # If there is a bye player, the bye player is added as a pair.
    all_paired_count = int(math.ceil(float(player_count)/2))

    # If odd number of players, then get a list of possible bye players,
    # from which to award a bye.
    # A possible bye player is a player that has not had a bye in a previous
    # round.
    # The list is sorted by rank.
    if player_count % 2 != 0:
        possible_bye_players = possibleByePlayers()

    # Get a list of possible pairings from the possible_pairings view,
    # sorted by rank.
    # Possible pairings only include players that have not played each other
    # in a previous round.
    possible_pairs = possiblePairings()

    logging.debug(
        "Started pairing %d players using %d possible pairings"
        % (player_count, len(possible_pairs)))

    # Try to find a complete set of pairings.
    # The while loop is only useful when there are an odd number of players.
    # If there are an odd number of players and an iteration cannot find
    # a complete set of pairs, the next available possible bye player
    # will be used as the bye player, and another pairing attempt will be 
    # made. 
    while len(pairs) < all_paired_count:
        # clear list of pairings
        del pairs[:]

        # If we have an odd number of players,
        # add lowest ranked possible bye player to pairs,
        # and remove bye player from possible bye player list.
        if player_count % 2 != 0:
            if len(possible_bye_players) > 0:
                bye_player = possible_bye_players.pop()
                pairs.append((
                    bye_player[0], bye_player[1],
                    bye_player[0], bye_player[1]))
                logging.debug("Added bye player %s to pairs" % bye_player[1])
            else:
                raise ValueError("No players are eligible for a bye.")

        # Add possible pairs to list, only adding each player once.
        if tryPairing(0, all_paired_count, pairs, possible_pairs):
            logging.debug("Finished pairing")
            # We have found all the pairs for the next round.
            return pairs
        elif player_count % 2 == 0:
            # Pairing failed and we have an even number of players,
            # so no point in looping, we are done.
            raise ValueError(
                "Pairing failed. Needed %d pairs, found %d"
                % (all_paired_count, len(pairs)))


def tryPairing(start, all_paired_count, pairs, possible_pairs):
    """Recursive function that attempts to find a complete set of pairs
        for a round, from a list of all possible pairs.

        Recursion is used since multiple attempts at pairing may be needed.
        As we get near the end of the possible pairs list we may find
        that a player cannot be paired because all of the possible players that
        the player can be paired with are already matched up with other players 
        in the pairs list. When this happens, recursion allows us to back up,
        remove the last pair added, and try again with a different possible pair.

    Args:
        start: position in list of possible pairs to start pairing.
        all_paired_count: number of pairs needed for a complete set.
        pairs: list of pairs that have been found so far.
        possible_pairs: list of possible pairs for inclusion in pairs.

    Returns:
        True: Found complete set of pairs.
        False: Unable to find complete set of pairs.

    """
    for i in range(start, len(possible_pairs)):
        (id1, name1, id2, name2) = possible_pairs[i]
        
        # If none of the players in the possiible pair have already been added
        # to the pairs list, then we can add the pair.
        if not any(id1 in (p[0], p[2]) or id2 in (p[0], p[2]) for p in pairs):
            # Add pair to pairs.
            pairs.append((id1, name1, id2, name2))
            logging.debug("Added pair (%s,%s) to pairs" % (name1, name2))

            if (len(pairs) == all_paired_count):
                # We have found all the pairs for the next round.
                return True
            # Try to find the next pair.
            if tryPairing(start+1, all_paired_count, pairs, possible_pairs):
                # We have found all the pairs for the next round.
                return True
            else:
                # Failed to find a complete set of pairs,
                # so remove last pair added, and move on to next possible pair.
                pairs.pop()
                logging.debug(
                    "Removed pair (%s,%s) from pairs" % (name1, name2))
    return False


def possibleByePlayers():
    """Get the list of players that have not had a bye.

    Returns:
      A list of tuples of players (id, name) ordered by rank.
    """
    conn = connect()
    c = conn.cursor()
    sql = """SELECT id, name FROM standings WHERE byes = 0
                ORDER BY rank, opponent_wins DESC;"""
    c.execute(sql)
    possible_bye_players = c.fetchall()
    conn.close()
    return possible_bye_players


def possiblePairings():
    """Get the list of possible pairings for a round.
        A possible pairing is two players that have not played each other in 
        a previous round.

    Returns:
      A list of tuples of possible player pairings (id1, name1, id2, name2)
      ordered by rank.
    """
    conn = connect()
    c = conn.cursor()
    sql = """SELECT id1, name1, id2, name2 FROM possible_pairings
                ORDER BY rank1, opponent_wins1 DESC,
                rank2, opponent_wins2 DESC;"""
    c.execute(sql)
    possible_pairs = c.fetchall()
    conn.close()
    return possible_pairs
