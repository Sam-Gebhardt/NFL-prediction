"""
Display more complex stats.
"""

import sqlite3


def graph_accuracy():
    pass


def accuracy():
    """Print out the accuracy of the model"""

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""SELECT week FROM season_2020 WHERE team = 'CURRENT_WEEK'""")
    week = c.fetchall()[0][0]

    total, correct = -1, -1
    for i in range(1, week + 1):
        per_week_total, per_week_correct = -1, -1
        c.execute("""SELECT prediction, outcome FROM season_2020 WHERE week = ?""", (i, ))
        data = c.fetchall()

        for j in data:
            if not j:
                continue

            total += 1
            per_week_total += 1
            if j[0] == j[1]:
                correct += 1
                per_week_correct += 1

        per_week_correct //= 2
        per_week_total //= 2
        print(f"Week {i}: {per_week_correct} correct out of {per_week_total}"
              f" for {per_week_correct / per_week_total * 100}%")

    correct //= 2
    total //= 2
    print(f"Overall: {correct} correct out of {total} for {correct / total * 100}%")

    conn.close()


if __name__ == "__main__":
    accuracy()
