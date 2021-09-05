"""
Run before the season starts to create the database,
make a table for the season and fill it with the
schedule for the upcoming season.
"""

import sqlite3
import urllib.request
import bs4 as bs
import time
import re
from globals import *


if __name__ == "__main__":  # avoids circular imports
    import predictions
    import calc_elo


def get_schedule(c, conn) -> None:

    for team in NFL_TEAMS:

        source = urllib.request.urlopen(f'https://www.espn.com/nfl/team/schedule/_/name/{team}/season/2021').read()
        soup = bs.BeautifulSoup(source, features='lxml')

        table = soup.find_all('span')
        to_text = [i.text for i in table]
        start, end = 0, len(to_text)

        for i in range(len(to_text)):

            if to_text[i] == '1':
                start = i

        to_text = to_text[start:end]
        bye, shift = 0, 0

        for i in range(0, 18):  # populate table with schedule

            opponent = re.sub("[*]", "", to_text[4 + (i * 6) + shift]).strip()

            if not bye and to_text[(i * 6) + 1].isnumeric():
                shift = -5
                opponent = "BYE"
                bye = i + 1

            c.execute("""INSERT INTO season_2021 (week, team, opponent) VALUES (?, ?, ?)""",
                      (i + 1, team, opponent))
            print(i + 1, team, opponent)

        c.execute("""UPDATE season_2021 SET bye = ? WHERE team = ? """, (bye, team))
        time.sleep(3)

    conn.commit()


def get_team_name(name: str) -> str:
    """Returns the team name """

    names = name.split('\n')
    rank = []

    for i in names:
        i = re.sub("[0-9.*]", "", i)
        start, middle = i.find('('), i.find("via")

        if middle != -1:  # pick was traded 2+ times
            end = i.find(')')
            i = i[middle + 4:end]
        elif start != -1:  # pick was traded 1 time
            i = i[start + 5:middle]
        
        rank.append(i.strip())

    return rank


def draft_order(c, conn) -> None:

    source = urllib.request.urlopen('https://www.espn.com/nfl/draft2021/story/_/id/31106459/'
                                    'nfl-draft-order-2021-picks-including-all-259-picks-seven-rounds')

    soup = bs.BeautifulSoup(source, features='lxml')
    table = soup.find_all("p")
    ranking = []

    for i in table:

        if i.text[:2] == "1.":
            ranking = get_team_name(i.text)
            break

    if len(ranking) != 32:
        print("Fatal error: Scraping preseason rankings failed")
        exit(1)

    for j in range(len(ranking)):

        if "San Fran" in ranking[j]:
            ranking[j] = "San Francisco 49ers"

        c.execute("""UPDATE season_2021 SET loss_rank = ?, win_rank = ?, power = ?, avg_power = ? 
                    WHERE week = ? AND team = ?""", (j - 32, j + 1, j - 16, j - 16, 1, CONVERT[ranking[j]]))

    conn.commit()
    c.execute("""SELECT opponent FROM season_2021 WHERE team = ?""", ("nyj", ))
    jets = c.fetchall()

    c.execute("""SELECT opponent FROM season_2021 WHERE team = ?""", ("lac", ))
    chargers = c.fetchall()

    """Since there are 2 teams in LA/NY need to
    have 2 unique locations for both: LA 2 and NY 2"""
    for i in range(len(jets)):

        if jets[i][0] != "BYE":
            
            c.execute("""UPDATE season_2021 SET opponent = ? WHERE team = ? AND week = ?""",
                    ("New York 2", CONVERSION_CHART[jets[i][0]], i + 1))

        if chargers[i][0] != "BYE":

            c.execute("""UPDATE season_2021 SET opponent = ? WHERE team = ? AND week = ?""",
                  ("Los Angeles 2", CONVERSION_CHART[chargers[i][0]], i + 1))

    print("Success!")

    conn.commit()


def main():
    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS season_2021 (week int, team text, opponent text, loss_rank int, 
                win_rank int, outcome text, prediction text, wins int, bye int,  power int, avg_power int, 
                UNIQUE(week, team))""")

    """Table data:
    week: The week of the NFL season
    team: The team
    opponent: The opponent of team column
    loss_rank: points lost if an opponent losses to team column
    win_rank: Points gained if an opponent beats team
    outcome: Did the team win or lose?
    prediction: Are they predicted to win or lose?
    wins: total team wins
    bye: the week the team has a bye
    power: current ELO
    avg_power: power per week (used to negate difference caused by bye-week)"""

    try:
        # dummy team that holds the current week on the NFL season
        c.execute("""INSERT INTO season_2021 (week, team) VALUES (?, ?)""", (1, "CURRENT_WEEK"))

    except sqlite3.IntegrityError:  # Already been initialized
        print("Database already initialized.")
        return

    get_schedule(c, conn)
    draft_order(c, conn)

    conn.close()
    

def mid_season_init(week: int):  # untested: test once season starts
    """Create the database after the season has already started"""

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""UPDATE season_2021 SET week = ? WHERE team = 'CURRENT_WEEK'""", (week, ))

    for team in NFL_TEAMS:

        source = urllib.request.urlopen(f'https://www.espn.com/nfl/team/schedule/_/name/{team}/season/2021').read()
        soup = bs.BeautifulSoup(source, features='lxml')

        table = soup.find_all('span')
        to_text = [i.text for i in table]

        for i in range(0, 18):

            possible_bye = False
            if 12 > i > 2:
                possible_bye = True

            delta = 6
            if week > i + 1:  # if the week has been played, delta is 11 due to increased data from ESPN
                delta = 11

            second = False
            start = 0
            end = len(to_text)

            for j in range(len(to_text)):
                # cleanse irreverent data

                if to_text[j] == "1":
                    start = j
                    second = True

                elif second and to_text[j] == "WK":
                    end = j
                    break

            to_text = to_text[start:end]

            shift = 0
            if possible_bye:
                shift = -10

            outcome = to_text[5 + (i * delta) + shift]   # 5
            total_wins = to_text[7 + (i * delta) + shift]  # 7

            pattern = re.compile(r"\d+-\d+")
            match = pattern.search(total_wins)

            if len(outcome) > 1 or not match:
                outcome = to_text[5 + (week * 11)]
                total_wins = to_text[7 + (week * 11)]
                # assume the team is on bye and fix it if they aren't

            c.execute("""UPDATE season_2021 SET outcome = ?, wins = ? WHERE team = ? AND week = ?""",
                      (outcome, total_wins, team, week + 1))

            time.sleep(2)

    conn.commit()
    conn.close()

    for i in range(1, week + 1):  # update elo based on played weeks
        calc_elo.main(i)


if __name__ == "__main__":
    main()
