"""
For each team in the NFL
predict if they will win
their next game.
"""

import sqlite3
from initalize import NFL_TEAMS, CONVERSION_CHART
from sys import argv


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

        c.execute("""SELECT * FROM season_2020 WHERE week = ? AND team = ?""", (week, team))
        data = c.fetchall()[0]

        opponent = data[2]
        team_power = data[9]

        c.execute("""SELECT power FROM season_2020 WHERE week = ? AND team = ?""", (week, CONVERSION_CHART[opponent]))
        opponent_power = c.fetchall()[0][0]

        converted_opponent = CONVERSION_CHART[opponent]
        outcome = 'W'
        winner, loser = team, opponent

        if opponent_power > team_power:
            outcome = 'L'
            winner, loser = opponent, team

        if converted_opponent not in done and not silent:
            print(f"{winner} is predicted to beat {loser}")

        if verbose:
            done.append(converted_opponent)
            done.append(team)

        c.execute("""UPDATE season_2020 SET prediction = ? WHERE team = ? AND week = ?""", (outcome, team, week))

    conn.commit()
    conn.close()


if __name__ == "__main__":

    if len(argv) == 1:  # default case
        main()

    else:
        for i in range(1, len(argv)):
            if argv[i].startswith("--"):
                if argv[i][:7] == "--week=":

                    try:
                        week_num = int(argv[i][7:])
                        if week_num > 17 or week_num < 1:
                            print("Week must be a week of the season (1 - 17)")
                        main(argv[i][7:])

                    except ValueError:  # not a number
                        print("Week must be an integer")

            elif argv[i].startswith("-"):
                for flag in range(1, len(argv[i])):

                    if flag == 's':  # silent mode
                        main(silent=True)

                    elif flag == 'v':  # verbose
                        main(verbose=True)

