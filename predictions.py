"""
For each team in the NFL
predict if they will win
their next game.
"""

import sqlite3
from initalize import NFL_TEAMS, CONVERSION_CHART


def main():

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""SELECT week FROM season_2020 WHERE team = 'CURRENT_WEEK'""")

    week = c.fetchall()[0][0] + 1
    print(f"Week {week}:\n")
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

        if converted_opponent not in done:
            print(f"{winner} is predicted to beat {loser}")

        done.append(converted_opponent)
        done.append(team)

        c.execute("""UPDATE season_2020 SET outcome = ? WHERE team = ? AND week = ?""", (outcome, team, week))

    conn.commit()
    conn.close()


if __name__ == "__main__": 
    main()
