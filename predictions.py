"""
For each team in the NFL
predict if they will win
their next game.
"""

import sqlite3
from globals import NFL_TEAMS, CONVERSION_CHART


def get_key(val: str) -> str:
    for key, value in CONVERSION_CHART.items():
        if val == value:
            return key


def tie_breaker(team1: str, team2: str, week: int) -> tuple:
    """Tie breakers are determined by the average opponents power in wins."""

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""SElECT avg(power) FROM season_2021 WHERE opponent = ? AND week < ?""", (get_key(team1), week))
    avg_1 = c.fetchall()[0][0]
    c.execute("""SElECT avg(power) FROM season_2021 WHERE opponent = ? AND week < ?""", (team2, week))
    avg_2 = c.fetchall()[0][0]

    winner, loser, outcome = team1, team2, "W"
    if avg_2 > avg_1:
        winner, loser, outcome = team2, team1, "L"

    return winner, loser, outcome


def prediction(c, conn, week: int) -> None:

    done = []  # prevent displaying the same results twice

    for team in NFL_TEAMS:

        # get team's power
        c.execute("""SELECT * FROM season_2021 WHERE week = ? AND team = ?""", (week, team))
        data = c.fetchall()[0]

        # get next opponent
        c.execute("""SELECT * FROM season_2021 WHERE week = ? AND team = ?""", (week, team))
        next_data = c.fetchall()[0]

        opponent = next_data[2]
        team_power = data[9]

        if opponent == "BYE":
            continue

        c.execute("""SELECT power FROM season_2021 WHERE week = ? AND team = ?""",
                  (week, CONVERSION_CHART[opponent]))
        opponent_power = c.fetchall()[0][0]

        opponent = CONVERSION_CHART[opponent]
        winner, loser, outcome = team, opponent, 'W'

        if opponent_power > team_power:
            winner, loser, outcome = opponent, team, 'L'
        elif opponent_power == team_power:
            result = tie_breaker(team, opponent, week)
            winner, loser, outcome = result[0], result[1], result[2]

        if opponent not in done:
            print(f"{winner} is predicted to beat {loser}")

        done.append(opponent)
        done.append(team)

        c.execute("""UPDATE season_2021 SET prediction = ? WHERE team = ? AND week = ?""", (outcome, team, week))


def main(week=None):

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    message = "(Already happened)"
    if not week:
        c.execute("""SELECT week FROM season_2021 WHERE team = 'CURRENT_WEEK'""")
        week = c.fetchall()[0][0]
        message = ""

    print(f"Week {week}{message}:\n")
    prediction(c, conn, week)

    conn.commit()
    conn.close()


if __name__ == "__main__":

    main()
