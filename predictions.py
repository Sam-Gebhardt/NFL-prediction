"""
Predict if each team will win their next game.
"""

# pylint: disable=line-too-long, pointless-string-statement

import sqlite3
from globals import NFL_TEAMS, YEAR, ABBREV_TO_FULL


def tie_breaker(cursor: sqlite3.Cursor, team1: str, team2: str, week: int) -> tuple:
    """Tie breakers are determined by the average opponents power in wins."""

    cursor.execute("""SElECT avg(power) FROM season_2021 WHERE opponent = ? AND week < ?""",
                  (team1, week))
    avg_1 = cursor.fetchall()[0][0]

    cursor.execute("""SElECT avg(power) FROM season_2021 WHERE opponent = ? AND week < ?""",
                  (team2, week))
    avg_2 = cursor.fetchall()[0][0]

    winner, loser, outcome = team1, team2, "W"
    if avg_2 > avg_1:
        winner, loser, outcome = team2, team1, "L"

    return winner, loser, outcome


def prediction(cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """
    Predict which team will win each game this week
    """

    cursor.execute(f"""SELECT week FROM season_{YEAR} WHERE team = 'CURRENT_WEEK'""")
    week = cursor.fetchall()[0][0]

    print(f'Predictions for Week {week}\n')

    # prevent displaying the same results twice
    seen = set()
    # easy conversion from W -> L and L -> W
    outcomes = {'W': 'L', 'L': 'W'}

    for team in NFL_TEAMS:

        # Only want to print once
        if team in seen:
            continue

        cursor.execute(f"""SELECT opponent, power, avg_power, bye FROM season_{YEAR}
                        WHERE week = ? AND team = ?""", (week, team, ))
        team1 = cursor.fetchall()[0]
        opponent = team1[0]

        if team1[3] == week:
            print(f'{team} is on bye')
            continue

        cursor.execute(f"""SELECT power, avg_power FROM season_{YEAR} WHERE week = ? AND team = ?""",
                        (week, team1[0], ))
        team2 = cursor.fetchall()[0]

        if team1[2] > team2[1]:
            outcome, winner, loser = 'W', team, opponent
        elif team1[2] < team2[1]:
            outcome, winner, loser = 'L', opponent, team
        # unlikely case of a tie
        else:
            outcome, winner, loser = tie_breaker(cursor, team1, team2, week)

        print(f'The {ABBREV_TO_FULL[winner].split(" ")[-1]} should beat the {ABBREV_TO_FULL[loser].split(" ")[-1]}')
        # print(f'The {ABBREV_TO_FULL[winner]} should beat the {ABBREV_TO_FULL[loser]}')

        seen.add(team)
        seen.add(team1[0])

        # update team1
        cursor.execute(f"""UPDATE season_{YEAR} SET prediction = ? WHERE team = ? AND week = ?""",
                       (outcome, team, week))
        # update team2
        cursor.execute(f"""UPDATE season_{YEAR} SET prediction = ? WHERE team = ? AND week = ?""",
                       (outcomes[outcome], opponent, week))

    conn.commit()


def main() -> None:
    """
    Driver code
    """

    conn = sqlite3.connect('NFL.db')
    cursor = conn.cursor()

    prediction(cursor, conn)

    conn.close()


if __name__ == "__main__":

    main()
