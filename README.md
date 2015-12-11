# Tournament Results Project
A Python module that uses a PostgreSQL database to manage a Swiss style tournament.
The module allows players to be registered, rounds of matches to be computed,
 match results to be recorded, and standings to be viewed.

## Swiss Style
The Swiss system allows all players to play in each round of a tournament, whilst
keeping a small number of rounds for the tournament. 
It achieves this by pairing players with identical or similar tournament scores in each round.
This allows a winner to be determined in fewer rounds.

The rules implemented in the pairing algorithm of this API are:
* Each player is paired with another player with the same score,
or as close as possible, in a round.
* Players can only play each other once in a tournament.
* All players play in each round, unless there is an odd number of players,
 in which case a player will receive a bye.
* A player can only have one bye in a tournament.
* A bye will be given to the lowest ranking player possible.
* A win scores one point and a draw scores half a point.
* In the case of a tied score at the end of a tournament, 
opponent match wins is tracked for each player, and can be
used to determine a winner.
* All decisions made by the algorithm are final.

## Prerequisites

The module requires **Python 2.7** and **PostgreSQL** to to be already installed.
The module also depeneds on the **psycopg2** Python module to access the PostgreSQL
database server.

## Installation
Clone this repository on the command line
```Shell
git clone https://github.com/iainbx/tournament-results.git
```

## Files
The repository contains the following files.
###tournament.sql
Contains the database schema used by the module.
###tournament.py
The Python module for managing a tournament.
###tournament_test.py
Unit tests and system tests for the tournament module.

## Usage
###Database Setup
To create the tournament database and its tables and views in PostgreSQL,
run the following psql command on the command line
```Shell
psql -f tournament.sql
```

###Unit Tests
Once the database has been successfully setup,
you can run the unit tests for the Python module with the following python command on the 
command line
```Shell
python tournament_test.py
```

###System Tests
You can also perform a system test that will play a tournament with random match results.
To do this, start the python interpreter with the *python* command on the command line.
Then enter the following commands in the python interpreter 
to simulate a 3 player tournament
```Python 
import tournament_test
tournament_test.simTournament(3)
``` 
Once the simulation has finished you can view the player standings in a pretty format
by using the psql command line interpreter. Start the psql interpreter in another 
command line window (or exit the python interpreter using Ctrl-D) by typing the *psql*
command on the command line. Then enter the following commands in the psql interpreter 
to connect to the tournament database and query the standings view
```PLpgSQL
\c tournament
select * from standings order by rank, opponent_wins desc;
```
you should see something like this, with the highest ranking player listed first
```
 id |   name    | wins | draws | opponent_wins | played | byes | rank
----+-----------+------+-------+---------------+--------+------+------
 81 | Player003 |    2 |     0 |             1 |      2 |    1 |    0
 79 | Player001 |    1 |     0 |             3 |      2 |    0 |    1
 80 | Player002 |    1 |     0 |             1 |      2 |    1 |    1
(3 rows)
```
To simulate a tournament with a random number of players and random match results, you can
call the simTournament() function without any arguments. 
So to simulate 3 random tournaments, you could do something like this in the python interpreter
```Python 
import tournament_test
for x in range(3):
    tournament_test.simTournament()

``` 
and you should see output similar to this
```Python
INFO:root:Simulating a tournament with 36 players...
INFO:root:Playing round 1
INFO:root:Playing round 2
INFO:root:Playing round 3
INFO:root:Playing round 4
INFO:root:Playing round 5
INFO:root:Playing round 6
INFO:root:After 6 rounds, Player030 wins tournament on omw's
INFO:root:Simulating a tournament with 63 players...
INFO:root:Playing round 1
INFO:root:Playing round 2
INFO:root:Playing round 3
INFO:root:Playing round 4
INFO:root:Playing round 5
INFO:root:Playing round 6
INFO:root:After 6 rounds, Player048 wins tournament on omw's
INFO:root:Simulating a tournament with 82 players...
INFO:root:Playing round 1
INFO:root:Playing round 2
INFO:root:Playing round 3
INFO:root:Playing round 4
INFO:root:Playing round 5
INFO:root:Playing round 6
INFO:root:Playing round 7
INFO:root:After 7 rounds, Player067 wins tournament
```
Note that the player and match data is removed from the database at the start of each
simulation, so the standings view will only show the results of the last tournament
simulated.

###Managing A Tournament
The tournament module contains the following functions for managing a tournament.

####registerPlayer(name)
Adds a player to the tournament by putting an entry in the players table.
An ID number is assigned to the player.
Different players may have the same names but will receive different ID numbers.

####countPlayers()
Returns the number of currently registered players.

####deletePlayers()
Clear out all the player records from the database.

####reportMatch(id1, id2, winner)
Stores the outcome of a single match between two players in the database.
Leave the winner argument blank to record a draw.
To record a bye for a player, set id1, id2 and winner to the ID of the player.

####deleteMatches()
Clear out all the match records from the database.

####playerStandings()
Returns a list of (id, name, wins, draws, played, byes, opponent_wins, rank)
for each player, sorted by rank ascending and opponent match wins descending.

####swissPairings()
Given the existing set of registered players and the matches they have played,
generates and returns a list of pairings according to the Swiss system. 
Each pairing is a tuple (id1, name1, id2, name2), giving the ID and name of 
the paired players. 
