#!/usr/bin/env python
#
# Test cases for tournament.py


import logging
import math
from random import randint
from tournament import *


logging.getLogger().setLevel(logging.INFO)


def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before"
                         " they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 8:
        raise ValueError("Each playerStandings row should have 8 columns.")
    [(id1, name1, wins1, draws1, omw1, matches1, byes1, rank1),
        (id2, name2, wins2, draws2, omw2, matches2, byes2, rank2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players names should appear in standings,"
                         " even if they have no matches played.")
    print ("6. Newly registered players appear in the standings "
           "with no matches.")


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, id1)
    reportMatch(id3, id4, id3)
    standings = playerStandings()
    for (i, n, w, d, o, m, b, r) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have 0 wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, id1)
    reportMatch(id3, id4, id3)
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def testByes():
    deleteMatches()
    deletePlayers()
    registerPlayer("Kirk")
    registerPlayer("Spock")
    registerPlayer("McCoy")
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For 3 players, swissPairings should return 2 pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    if pid1 != pid2 and pid3 != pid4:
        raise ValueError(
            "No bye was assigned by swissPairings in 3 player tournament.")
    print "9. Bye was assigined in a 3 player tournament."


def testDraws():
    deleteMatches()
    deletePlayers()
    registerPlayer("Kirk")
    registerPlayer("Spock")
    registerPlayer("McCoy")
    registerPlayer("Scotty")
    pairings = swissPairings()
    for (id1, name1, id2, name2) in pairings:
        reportMatch(id1, id2)
    standings = playerStandings()
    for (id, name, wins, draws, omw, matches, byes, rank) in standings:
        if draws != 1:
            raise ValueError("Each player should have 1 draw recorded.")
    print "10. After reporting drawn matches, player standings show draws."


def testOpponentWins():
    deleteMatches()
    deletePlayers()
    registerPlayer("Kirk")
    registerPlayer("Spock")
    registerPlayer("McCoy")
    registerPlayer("Scotty")
    pairings = swissPairings()
    for (id1, name1, id2, name2) in pairings:
        reportMatch(id1, id2, id1)
    standings = playerStandings()
    for (id, name, wins, draws, omw, matches, byes, rank) in standings:
        if wins + omw != 1:
            raise ValueError(
                "After 1 match a player should have a win or an opponent win.")
    print ("11. After 1 match, the player standings show that each player "
           "has a win or an opponent win.")


def simTournament(player_count=None):
    """Simulate playing a complete tournament of log2(player count) rounds.

    Args:
        player_count:
        2 to 999 starts a tournament with that number of players.
        None starts a tournament with a random number of players
        between 2 and 99
    """
    if player_count is None:
        player_count = randint(2, 99)

    if player_count < 2 or player_count > 999:
        raise ValueError("Player count should be between 2 and 999")

    logging.info("Simulating a tournament with %s players..." % player_count)

    deleteMatches()
    deletePlayers()

    # Create a list of player names whose length equals player_count
    players = ["Player{0:03d}".format(x) for x in range(1, player_count+1)]

    for player in players:
        registerPlayer(player)

    # play log2(player count) rounds
    rounds = int(math.ceil(math.log(len(players), 2)))

    for x in range(rounds):
        logging.info("Playing round %d" % (x+1,))
        simRound()

    total_byes = 0

    standings = playerStandings()
    for i, (id, n, wins, draws, omw, matches, byes, r) in enumerate(standings):
        total_byes += byes
        if matches != rounds:
            raise ValueError(
                "Each player should have %d matches recorded." % rounds)
        if byes > 1:
            raise ValueError("A player should not have more than 1 bye.")
        if wins + draws > rounds:
            raise ValueError(
                "Each player cannot have more wins + draws than rounds.")
        if i == 0 and wins + draws == 0:
            raise ValueError(
                "Top ranked player should at least have 1 win or draw.")
        elif i > 0 and wins == rounds:
            raise ValueError(
                "Lower rankings should have less than %d wins." % rounds)

    if player_count % 2 != 0 and total_byes != rounds:
        raise ValueError(
            "The number of byes awarded in the tournament should be %d."
            % rounds)

    (id1, name1, wins1, draws1, omw1, matches1, byes1, rank1) = standings[0]
    (id2, name2, wins2, draws2, omw2, matches2, byes2, rank2) = standings[1]
    if rank1 < rank2:
        logging.info("After %d rounds, %s wins tournament" % (rounds, name1))
    elif omw1 > omw2:
        logging.info(
            "After %d rounds, %s wins tournament on omw's" % (rounds, name1))
    else:
        logging.info("After %d rounds, tournament tied" % rounds)


def simRound():
    """Simulate playing a single round of a tournament,
        with random match results.
    """
    pairings = swissPairings()
    for (id1, name1, id2, name2) in pairings:
        if id1 == id2:
            # bye, so just report it
            reportMatch(id1, id2, id1)
            logging.debug("%s got a bye" % name1)
        else:
            # randomly select winner or draw
            x = randint(0, 9)
            if x < 4:
                # id1 wins
                reportMatch(id1, id2, id1)
                logging.debug("%s beats %s" % (name1, name2))
            elif x > 4:
                # id2 wins
                reportMatch(id1, id2, id2)
                logging.debug("%s beats %s" % (name2, name1))
            else:
                # draw
                reportMatch(id1, id2)
                logging.debug("%s draws with %s" % (name1, name2))


def simTournaments():
    """Simulate playing tournaments with random number of players
        and random match results until interrupted.
    """
    x = 0
    while True:
        x += 1
        logging.info("Starting tournament %d" % x)
        simTournament()


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testByes()
    testDraws()
    testOpponentWins()
    print "Success!  All tests pass!"
