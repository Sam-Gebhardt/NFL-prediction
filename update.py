"""
Update the database with the wins
and losses from the past week.
"""

import sqlite3
import bs4 as bs
import urllib.request
from globals import NFL_TEAMS
import time


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

        to_text = to_text[start:end]
        print(to_text)

        shift = 0
        if bye < (week + 1):
            shift = -10

        try:
            outcome = to_text[5 + (week * 11) + shift]
            total_wins = to_text[7 + (week * 11) + shift]
            print(f"{team}: {outcome}, {total_wins}")

            c.execute("""UPDATE season_2021 SET outcome = ?, wins = ? WHERE team = ? AND week = ?""",
                      (outcome, total_wins, team, week + 1))
        except IndexError:
            print(f"Failed to update: '{team}'")

        time.sleep(2)

    c.execute("""UPDATE season_2021 SET week = ? WHERE team = 'CURRENT_WEEK'""", (week + 1, ))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
