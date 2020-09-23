"""
Take the new data inputted from
scrape_data.py and calculate the
new ELO score for each team.
"""
import sqlite3
from initalize import NFL_TEAMS, CONVERSION_CHART


def calc_rankings(week: int) -> None:
    """Find the loss/win rank and update the db
    *Power is updated AFTER the week happens*"""

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()
    week -= 1
    c.execute("""SELECT * FROM season_2020 WHERE week = 1 ORDER BY power DESC""")
    ranking = c.fetchall()
    for i in range(len(ranking)):
        # print(f"{ranking[i][1]}/{week + 1}: {-(i + 1)} and {32 - i}")
        c.execute("""UPDATE season_2020 SET win_rank = ? WHERE team = ? AND week = ?""",
                  (32 - i, ranking[i][1], week + 1))

        c.execute("""UPDATE season_2020 SET loss_rank = ? WHERE team = ? AND week = ?""",
                  (-(i + 1), ranking[i][1], week + 1))

    conn.commit()
    conn.close()


def main(week=None):

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    if not week:
        c.execute("""SELECT week FROM season_2020 WHERE team = 'CURRENT_WEEK'""")
        week = c.fetchall()[0][0]
        calc_rankings(week)

    if week == 0:
        print("Must wait till week 2 or update the database.")
        return

    for team in NFL_TEAMS:

        c.execute("""SELECT * FROM season_2020 WHERE week = ? AND team = ?""", (week, team))
        data = c.fetchall()[0]

        c.execute("""SELECT * FROM season_2020 WHERE week = ? AND team = ?""", (week - 1, team))
        past = c.fetchall()[0]

        c.execute("""SELECT loss_rank, win_rank FROM season_2020 WHERE team = ? AND week = ?""",
                  (CONVERSION_CHART[data[2]], week))
        ranks = c.fetchall()

        change = ranks[0][0]
        if data[5] == 'W':
            change = ranks[0][1]

        power = past[10] + change
        c.execute("""UPDATE season_2020 SET power = ? WHERE team = ? and week = ?""", (power, team, week))
        c.execute("""UPDATE season_2020 SET avg_power = ? WHERE team = ? AND week = ?""", ((power / week), team, week))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
    print("Success!")
