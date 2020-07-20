"""
Take the new data inputted from
scrape_data.py and calculate the
new ELO score for each team.
"""
import sqlite3
from initalize import NFL_TEAMS, CONVERSION_CHART


def main():

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    # c.execute("""SELECT * FROM season_2020 WHERE week = 1 ORDER BY win_rank DESC""")

    c.execute("""SELECT week FROM season_2020 WHERE team = 'CURRENT_WEEK'""")
    week = c.fetchall()[0][0] + 1

    if week == 1:
        print("Must wait till week 2 or update the database.")
        return

    for team in NFL_TEAMS:

        c.execute("""SELECT * FROM season_2020 WHERE week = ? and team = ?""", (week - 1, team))
        data = c.fetchall()[0]

        c.execute("""SELECT loss_rank, win_rank FROM season_2020 WHERE team = ? and week = ?""",
                  (CONVERSION_CHART[data[2]], week))
        ranks = c.fetchall()

        # print(f"{data} ------ {ranks}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
    # conn = sqlite3.connect('NFL.db')
    # c = conn.cursor()
    # c.execute("""SELECT * FROM season_2020 WHERE week = ? ORDER BY power DESC""", (1, ))
    # out = c.fetchall()
    # for i in out:
    #     print(i)

    # conn.close()