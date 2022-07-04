"""
Update the database with the wins and losses from the past
week (scraped from ESPN). Recalculates the ELO of each team
based on win or lose.

Note: Should only be ran once a week
"""

import sqlite3
import urllib.request
import time
import bs4 as bs
from globals import NFL_TEAMS


def main():

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""SELECT week FROM season_2021 WHERE team = 'CURRENT_WEEK'""")
    week = c.fetchall()[0][0]

    for team in NFL_TEAMS:

        c.execute("""SELECT bye FROM season_2021 WHERE team = ? and week = ?""", (team, 1))
        bye = c.fetchall()[0][0]

        source = urllib.request.urlopen(f'https://www.espn.com/nfl/team/schedule/_/name/{team}/season/2021').read()
        soup = bs.BeautifulSoup(source, features='lxml')

        table = soup.find_all('span')
        to_text = [i.text for i in table]

        start = 0
        end = len(to_text)

        for i in range(len(to_text)):

            if to_text[i] == "1":
                start = i
                break

        to_text = to_text[start:end]

        shift = 0
        if bye < (week + 1):
            shift = -10

        try:
            outcome = to_text[5 + (week - 1) * 11 + shift]
            total_wins = to_text[7 + (week - 1) * 11 + shift].split("-")[0]
            print(f"{team}: {outcome}, {total_wins}")

            c.execute("""UPDATE season_2021 SET outcome = ?, wins = ? WHERE team = ? AND week = ?""",
                      (outcome, total_wins, team, week))

        except IndexError:
            print(f"Failed to update: '{team}'")

        time.sleep(2)

    c.execute("""UPDATE season_2021 SET week = ? WHERE team = 'CURRENT_WEEK'""", (week + 1, ))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()


"""



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
        current_week = c.fetchall()[0]

        if current_week[2] == "BYE":
            conn.commit()
            bye_week_power(team, week)
            continue

        c.execute("""SELECT * FROM season_2021 WHERE week = ? AND team = ?""", (week - 1, team))
        past_week = c.fetchall()[0]
        print("past:",past_week)

        c.execute("""SELECT loss_rank, win_rank FROM season_2021 WHERE team = ? AND week = ?""",
                  (CONVERSION_CHART[past_week[2]], week - 1))
        opponent_ranks = c.fetchall()


        change = opponent_ranks[0][0]
        if past_week[5] == 'W':
            change = opponent_ranks[0][1]

        power = past_week[10] + change
        c.execute("""UPDATE season_2021 SET power = ? WHERE team = ? and week = ?""", (power, team, week))
        c.execute("""UPDATE season_2021 SET avg_power = ? WHERE team = ? AND week = ?""", ((power / week), team, week))

    conn.commit()
    conn.close()
    calc_rankings(week)


if __name__ == "__main__":
    main()

    print("Success!")

"""