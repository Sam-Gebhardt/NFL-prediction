"""
Run before the season starts to create the database,
make a table for the season and fill it with the
schedule for the upcoming season.
"""

# pylint: disable=line-too-long, pointless-string-statement

from time import sleep
import sqlite3
import re
import urllib.request
import bs4 as bs
from globals import FULL_TO_ABBREV, NFL_TEAMS, YEAR, CITY_T0_ABBREV


"""
Table data:
    week: The week of the NFL season
    team: The team
    opponent: The opponent of team column
    loss_rank: points lost if an opponent losses to team column
    win_rank: Points gained if an opponent beats team
    prediction: Are they predicted to win or lose?
    outcome: Did the team win or lose?
    bye: the week the team has a bye
    wins: total team wins
    power: current ELO
    avg_power: power per week (used to negate difference caused by bye-week)
"""


def fix_two_team_problem(cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """
    Both LA and NY have two teams which makes matching the city name
    to team name impossible.

        "New York" -> "Jets"
        "New York" -> "Rams"

    Iterate through each LA/NY teams schedule and modify the opponents
    to have the correct team abbrev
    """

    teams = 'lac', 'lar', 'nyg', 'nyj'
    for team in teams:

        cursor.execute(f"""SELECT week, opponent FROM season_{YEAR} WHERE
                        team = ?""", (team, ))
        out = cursor.fetchall()

        for week, opponent in out:
            if opponent == "BYE WEEK":
                continue

            """
            If a New York team plays a LA team it might not be
            able to tell which team is correct. Notify the user to
            manually update the entry if it is wrong
            """
            if (team[0:2] == 'ny' and opponent[0:2] == 'la') or \
               (team[0:2] == 'la' and opponent[0:2] == 'ny') or \
               (team[0:2] == opponent[0:2]) :

                print(f'** {team} might need manual correction at week {week} **')

            cursor.execute(f"""UPDATE season_{YEAR} SET opponent = ? WHERE week = ? AND team = ?""",
                            (team, week, opponent, ))

        conn.commit()


def get_schedule(cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """
    Get the schedule for the season and put it into the database
    """
    for team in NFL_TEAMS:

        source = urllib.request.urlopen(f'https://www.espn.com/nfl/team/schedule/_/name/{team}/season/{YEAR}').read()
        soup = bs.BeautifulSoup(source, features='lxml')

        table = soup.find_all('td', class_='Table__TD')

        # Hold in a list as it allows filtering out the preseason games
        # The order of games depends on if the preseason has started yet
        schedule = []
        for i in table:
            schedule.append(i.text)

        start, end = 0, len(schedule) - 1
        for index, item in enumerate(schedule):
            if "Regular" in item:
                start = index

            if "Preseason" in item and index != 0:
                end = index

        schedule =  schedule[start:end]
        # print(schedule)

        index = 1
        for i in schedule:

            # remove '@ ' or 'vs'
            # * marks a neutral field game
            i = i[2:].replace('*', '').strip()

            # Deleted first 2 chars: BYE WEEK -> E WEEK
            if i == "E WEEK":
                cursor.execute(f"""INSERT INTO season_{YEAR} (week, team, opponent) VALUES (?, ?, ?)""",
                                (index, team, "BYE WEEK"))
                cursor.execute(f"""UPDATE season_{YEAR} SET bye = ? WHERE team = ?""",
                                (index, team, ))

                print(index, team, "BYE_WEEK")
                index += 1

            if i in CITY_T0_ABBREV:
                cursor.execute(f"""INSERT INTO season_{YEAR} (week, team, opponent) VALUES (?, ?, ?)""",
                                (index, team, CITY_T0_ABBREV[i], ))
                print(index, team, CITY_T0_ABBREV[i])
                index += 1

        sleep(3)

    conn.commit()


def draft_order(cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> None:
    """
    Get the draft order to determine initial power rankings for the season
    """

    url = f'https://www.nfl.com/news/{YEAR}-nfl-draft-order-for-all-seven-rounds'
    source = urllib.request.urlopen(url)

    soup = bs.BeautifulSoup(source, features='lxml')
    table = soup.find_all(['div', 'p'], class_='nfl-c-body-part nfl-c-body-part--text')

    pos = 0
    for index, item in enumerate(table):
        if "Round 1" in item.text:
            pos = index + 1

    order = re.split('<br/>|<p>', str(table[pos]))
    fixed_order = []

    for index, item in enumerate(order):

        # accounts for trading of picks
        if 'from' in item:
            pattern = 'from [A-z]+ {1}[A-z]+( {1}[A-z49]+)?'
        else:
            pattern = '[A-z]+ {1}[A-z]+( {1}[A-z49]+)?'

        team = re.search(pattern, item)
        if team:
            # remove 'from' and 'through' to account for trades
            fixed_order.append(team[0].replace('from', '').replace('through', '').strip())

    index = 1
    for item in fixed_order:

        # Remove false positive regex matches
        if 'div' in item or 'class' in item:
            continue

        cursor.execute(f"""UPDATE season_{YEAR} SET loss_rank = ?, win_rank = ?, power = ?, avg_power = ?
                        WHERE week = ? AND team = ?""", (index - 33, index, index - 16, index - 16, 1,
                        FULL_TO_ABBREV[item]))

        index += 1


    conn.commit()


def main() -> None:
    """
    Driver code
    """

    conn = sqlite3.connect('NFL.db')
    cursor = conn.cursor()

    # Make sure Table hasn't already been created
    # try:

    #     cursor.execute(f"""CREATE TABLE IF NOT EXISTS season_{YEAR} (week int, team text, opponent text,
    #                     loss_rank int, win_rank int, outcome text, prediction text, wins int, bye int,
    #                     power int, avg_power int, UNIQUE(week, team))""")

    #     # dummy team that holds the current week on the NFL season
    #     cursor.execute(f"""INSERT INTO season_{YEAR} (week, team) VALUES (?, ?)""", (1, "CURRENT_WEEK"))

    # except sqlite3.IntegrityError:  # Already been initialized
    #     print("Database already initialized.")
    #     return

    # get_schedule(cursor, conn)
    # draft_order(cursor, conn)
    fix_two_team_problem(cursor, conn)

    conn.close()

    print(f"Database initialized for {YEAR} season")


if __name__ == "__main__":
    main()


"""
Notes:
Winning against #1 = +32
losing against #1 = -1

Winning against #32 = +1
losing against #1 = -32

"""