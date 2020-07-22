"""
Display more complex stats.
"""

import sqlite3


def main():

    # conn = sqlite3.connect('NFL.db')
    # c = conn.cursor()

    pass


def graph_accuracy():
    pass


def team_accuracy(team: str):
    """Print accuracy of
    a specific team"""

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""SELECT week FROM season_2020 WHERE team = 'CURRENT_WEEK'""")
    week = c.fetchall()[0][0] + 1

    total, correct = 0, 0
    for i in range(1, week):
        c.execute("""SELECT prediction, outcome FROM season_2020 WHERE week = ? AND team = ?""", (i, team))
        data = c.fetchall()[0]

        for j in data:
            total += 1
            if j[0] == j[1]:
                correct += 1

    conn.close()

    print(f"{team}: {correct} correct out of {total} for {correct / total * 100}%")


def accuracy():
    """Print out the accuracy of the model"""

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""SELECT week FROM season_2020 WHERE team = 'CURRENT_WEEK'""")
    week = c.fetchall()[0][0] + 1

    total, correct = 0, 0
    for i in range(1, week):
        c.execute("""SELECT prediction, outcome FROM season_2020 WHERE week = ?""", (i, ))
        data = c.fetchall()[0]

        for j in data:
            total += 1
            if j[0] == j[1]:
                correct += 1

    conn.close()

    print(f"{correct} correct out of {total} for {correct / total * 100}%")

