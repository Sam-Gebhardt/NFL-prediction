"""
Take the new data inputted from
scrape_data.py and calculate the
new ELO score for each team.
"""
import sqlite3
from globals import NFL_TEAMS, CONVERSION_CHART


def bye_week_power(team: str, week: int) -> None:
    """Power doesn't change over a bye week, so copy
       the data from last week into this week"""

    conn = sqlite3.connect("NFL.db")
    c = conn.cursor()

    c.execute("""SELECT * FROM season_2021 WHERE team = ? AND week = ?""", (team, week - 1))
    data = c.fetchall()[0]

    c.execute("""UPDATE season_2021 SET power = ? WHERE team = ? and week = ?""", (data[9], team, week))
    c.execute("""UPDATE season_2021 SET avg_power = ? WHERE team = ? AND week = ?""", (data[10], team, week))

    conn.commit()
    conn.close()


def calc_rankings(week: int) -> None:
    """Find the loss/win rank and update the db
    ***Power is updated AFTER the week happens***
    ***Win/loss rank are updated AFTER the week***
    """

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM season_2021 WHERE week = ? ORDER BY power DESC""", (week, ))
    ranking = c.fetchall()

    for i in range(len(ranking)):
        # print(f"{ranking[i][1]}/{week + 1}: {-(i + 1)} and {32 - i}")

        c.execute("""UPDATE season_2021 SET win_rank = ? WHERE team = ? AND week = ?""",
                  (32 - i, ranking[i][1], week))

        c.execute("""UPDATE season_2021 SET loss_rank = ? WHERE team = ? AND week = ?""",
                  (-(i + 1), ranking[i][1], week))

    conn.commit()
    conn.close()


def main(week=None):

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    if not week:
        c.execute("""SELECT week FROM season_2021 WHERE team = 'CURRENT_WEEK'""")
        week = c.fetchall()[0][0]

    if week == 0:
        print("Must wait till week 2 or update the database.")
        return

    for team in NFL_TEAMS:

        c.execute("""SELECT * FROM season_2021 WHERE week = ? AND team = ?""", (week, team))
        data = c.fetchall()[0]

        if data[2] == "BYE":
            conn.commit()
            bye_week_power(team, week)
            continue

        c.execute("""SELECT * FROM season_2021 WHERE week = ? AND team = ?""", (week - 1, team))
        past = c.fetchall()[0]

        c.execute("""SELECT loss_rank, win_rank FROM season_2021 WHERE team = ? AND week = ?""",
                  (CONVERSION_CHART[data[2]], week - 1))
        ranks = c.fetchall()

        change = ranks[0][0]
        if data[5] == 'W':
            change = ranks[0][1]

        power = past[10] + change
        c.execute("""UPDATE season_2021 SET power = ? WHERE team = ? and week = ?""", (power, team, week))
        c.execute("""UPDATE season_2021 SET avg_power = ? WHERE team = ? AND week = ?""", ((power / week), team, week))

    conn.commit()
    conn.close()
    calc_rankings(week)


if __name__ == "__main__":
    main()

    print("Success!")

