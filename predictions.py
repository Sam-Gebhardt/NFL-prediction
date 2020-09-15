"""
For each team in the NFL
predict if they will win
their next game.
"""

import sqlite3
from initalize import NFL_TEAMS, CONVERSION_CHART
# from sys import argv


def main(week=None, silent=False, verbose=False):

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    message = "(Already happened)"
    if not week:
        c.execute("""SELECT week FROM season_2020 WHERE team = 'CURRENT_WEEK'""")
        week = c.fetchall()[0][0] + 1
        message = ""

    print(f"Week {week}{message}:\n")
    done = []  # prevent displaying the same results twice

    for team in NFL_TEAMS:

        # get team's power
        c.execute("""SELECT * FROM season_2020 WHERE week = ? AND team = ?""", (week - 1, team))
        data = c.fetchall()[0]

        # get next opponent
        c.execute("""SELECT * FROM season_2020 WHERE week = ? AND team = ?""", (week, team))
        next_data = c.fetchall()[0]

        opponent = next_data[2]
        team_power = data[9]

        c.execute("""SELECT power FROM season_2020 WHERE week = ? AND team = ?""",
                  (week - 1, CONVERSION_CHART[opponent]))
        opponent_power = c.fetchall()[0][0]

        converted_opponent = CONVERSION_CHART[opponent]
        outcome = 'W'
        winner, loser = team, opponent

        if opponent_power > team_power:
            outcome = 'L'
            winner, loser = opponent, team

        if converted_opponent not in done and not silent:
            print(f"{winner} is predicted to beat {loser}")

        if not verbose:
            done.append(converted_opponent)
            done.append(team)

        c.execute("""UPDATE season_2020 SET prediction = ? WHERE team = ? AND week = ?""", (outcome, team, week))

    conn.commit()
    conn.close()


if __name__ == "__main__":

    main()
