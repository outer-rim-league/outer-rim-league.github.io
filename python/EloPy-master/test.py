from elopy import *

elo = Implementation()

elo.addPlayer("Hank")
elo.addPlayer("Bill", rating=900)

print elo.getPlayerRating("Hank"), elo.getPlayerRating("Bill")

elo.recordMatch("Hank", "Bill", winner="Hank")

print elo.getRatingList()

elo.recordMatch("Hank", "Bill", winner="Bill")

print elo.getRatingList()

elo.recordMatch("Hank", "Bill", draw=True)

print elo.getRatingList()

elo.removePlayer("Hank")

print elo.getRatingList()