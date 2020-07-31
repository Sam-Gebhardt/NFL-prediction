"""
Display more complex stats.
"""

import sqlite3
from sys import argv


def graph_accuracy():
    pass


def accuracy(team=""):
    """Print out the accuracy of the model"""

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""SELECT week FROM season_2020 WHERE team = 'CURRENT_WEEK'""")
    week = c.fetchall()[0][0] + 1

    name = ""
    if name:
        name = f"{team}: "

    total, correct = 0, 0
    for i in range(1, week):
        c.execute("""SELECT prediction, outcome FROM season_2020 WHERE week = ?""", (i, ))

        if team:
            c.execute("""SELECT prediction, outcome FROM season_2020 WHERE week = ? AND team = ?""", (i, team))

        data = c.fetchall()[0]

        for j in data:
            total += 1
            if j[0] == j[1]:
                correct += 1

    conn.close()
    print(f"{name}{correct} correct out of {total} for {correct / total * 100}%")


# TODO refactor accuracy functions into 1 or call the other

def main():

    v, a = False, False
    t_a = ""

    if len(argv) == 1:  # default behavior is just accuracy
        accuracy()
        return

    for i in argv:

        if argv.index(i) == 0:
            continue

        if len(i) > 1 and i[0:2] == "--":

            if "accuracy" in i:
                t_a = i[10:]
            else:
                print(f"Unknown long flag: {i[2:]}")
                return

        elif i.startswith('-'):

            for flag in i[1:]:

                if flag == 'h':
                    print("\nDisplay useful stats about the prediction:\n\n-help: Displays flags and their output\n-a: "
                          "Display accuracy of the model\n-accuracy='team': Display accuracy of a specific team\n-v: "
                          "Display a visual graph of rankings\n")

                elif flag == 'a':
                    a = True

                elif flag == 'v':  # visual
                    v = True

                else:
                    print(f"Unknown flag: {flag}")
                    return

    if a:
        accuracy()

    if v:
        graph_accuracy()

    if t_a:
        accuracy(t_a)


if __name__ == "__main__":
    main()
