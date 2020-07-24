"""
Display more complex stats.
"""

import sqlite3
from sys import argv


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


# TODO refactor accuracy functions into 1 or call the other

def main():

    if len(argv) == 1:
        print("Must pass flag")
        return

    if argv[1].startswith('-'):

        if argv[1][1:] == "help" or argv[1][1:] == 'h':
            print("\nDisplay useful stats about the prediction:\n\n-help: Displays flags and their output\n-a: Display "
                  "accuracy of the model\n-accuracy='team': Display accuracy of a specific team\n-v: Display a visual "
                  "graph of rankings\n")

        elif argv[1][1:] == 'a':
            accuracy()

        elif "accuracy" in argv[1][1:]:
            team_accuracy(argv[1][10:])

        elif argv[1][1:] == 'v':
            graph_accuracy()

        else:
            print(f"Unknown flag: {argv[1][1:]}")


if __name__ == "__main__":
    main()
