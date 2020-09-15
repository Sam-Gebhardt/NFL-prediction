"""
Take the new data inputted from
scrape_data.py and calculate the
new ELO score for each team.
"""
import sqlite3
from initalize import NFL_TEAMS, CONVERSION_CHART


def main(week=None):

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    # c.execute("""SELECT * FROM season_2020 WHERE week = 1 ORDER BY win_rank DESC""")

    if not week:
        c.execute("""SELECT week FROM season_2020 WHERE team = 'CURRENT_WEEK'""")
        week = c.fetchall()[0][0]

    if week == 0:
        print("Must wait till week 2 or update the database.")
        return

    for team in NFL_TEAMS:

        c.execute("""SELECT * FROM season_2020 WHERE week = ? and team = ?""", (week, team))
        data = c.fetchall()[0]

        c.execute("""SELECT loss_rank, win_rank FROM season_2020 WHERE team = ? and week = ?""",
                  (CONVERSION_CHART[data[2]], week))
        ranks = c.fetchall()

        change = ranks[0][0]
        if data[5] == 'W':
            change = ranks[0][1]

        c.execute("""UPDATE season_2020 SET power = power + ? WHERE team = ? and week = ?""", (change, team, week))
        c.execute("""UPDATE season_2020 SET avg_power = power / week WHERE team = ? and week = ?""", (team, week))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
    print("Success!")
