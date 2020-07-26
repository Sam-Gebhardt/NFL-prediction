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
from sys import argv

if __name__ == "__main__":  # avoids circular imports
    import predictions


NFL_TEAMS = 'ne', 'mia', 'nyj', 'buf', 'bal', 'pit', 'cin', 'cle', 'hou', 'ind', 'ten', 'jax', "kc", "lac", "den",\
           "lv", 'ari', 'lar', 'sea', 'sf', 'dal', 'phi', 'wsh', 'nyg', 'chi', 'min', 'gb', 'det', 'no', 'car',\
           'atl', 'tb'

# abbreviations of each nfl team

CONVERSION_CHART = {
    'Arizona ': 'ari', 'Atlanta ': 'atl', 'Baltimore ': 'bal', 'Buffalo ': 'buf', 'Carolina ': 'car', 'Chicago ': 'chi',
    'Cincinnati ': 'cin', 'Cleveland ': 'cle', 'Dallas ': 'dal', 'Denver ': 'den', 'Detroit ': 'det',
    'Green Bay ': 'gb', 'Houston ': 'hou', 'Indianapolis ': 'ind', 'Jacksonville ': 'jax', 'Kansas City ': 'kc',
    'Los Angeles ': 'lar', 'Los Angeles 2 ': 'lac', 'Miami ': 'mia', 'Minnesota ': 'min', 'New England ': 'ne',
    'New Orleans ': 'no', 'New York ': 'nyg', 'New York 2 ': 'nyj', 'Las Vegas ': 'lv', 'Philadelphia ': 'phi',
    'Pittsburgh ': 'pit', 'San Francisco ': 'sf', 'Seattle ': 'sea', 'Tampa Bay ': 'tb', 'Tennessee ': 'ten',
    'Washington ': 'wsh'
                    }

CONVERT_BACKWARDS = {'ari': 'Arizona Cardinals', 'atl': 'Atlanta Falcons', 'bal': 'Baltimore Ravens',
                     'buf': 'Buffalo Bills', 'car': 'Carolina Panthers', 'chi': 'Chicago Bears',
                     'cin': 'Cincinnati Bengals', 'cle': 'Cleveland Browns', 'dal': 'Dallas Cowboys',
                     'den': 'Denver Broncos', 'det': 'Detroit Lions', 'gb': 'Green Bay Packers',
                     'hou': 'Houston Texans', 'ind': 'Indianapolis Colts', 'jax': 'Jacksonville Jaguars',
                     'kc': 'Kansas City Chiefs', 'Los Angeles Chargers': 'lac', 'lar': 'Los Angeles Rams',
                     'mia': 'Miami Dolphins', 'min': 'Minnesota Vikings', 'ne': 'New England Patriots',
                     'no': 'New Orleans Saints', 'nyg': 'New York Giants', 'nyj': 'New York Jets',
                     'lv': 'Las Vegas Raiders', 'phi': 'Philadelphia Eagles', 'pit': 'Pittsburgh Steelers',
                     'sf': 'San Francisco 49ers', 'sea': 'Seattle Seahawks', 'tb': 'Tampa Bay Buccaneers',
                     'ten': 'Tennessee Titans', 'wsh': 'Washington Redskins'}

CONVERT = {'Arizona Cardinals': 'ari', 'Atlanta Falcons': 'atl', 'Baltimore Ravens': 'bal', 'Buffalo Bills': 'buf',
           'Carolina Panthers': 'car', 'Chicago Bears': 'chi', 'Cincinnati Bengals': 'cin', 'Cleveland Browns': 'cle',
           'Dallas Cowboys': 'dal', 'Denver Broncos': 'den', 'Detroit Lions': 'det', 'Green Bay Packers': 'gb',
           'Houston Texans': 'hou', 'Indianapolis Colts': 'ind', 'Jacksonville Jaguars': 'jax',
           'Kansas City Chiefs': 'kc', 'Los Angeles Chargers': 'lac', 'Los Angeles Rams': 'lar',
           'Miami Dolphins': 'mia', 'Minnesota Vikings': 'min', 'New England Patriots': 'ne',
           'New Orleans Saints': 'no', 'New York Giants': 'nyg', 'New York Jets': 'nyj', 'Las Vegas Raiders': 'lv',
           'Philadelphia Eagles': 'phi', 'Pittsburgh Steelers': 'pit', 'San Francisco 49ers': 'sf',
           'Seattle Seahawks': 'sea', 'Tampa Bay Buccaneers': 'tb', 'Tennessee Titans': 'ten',
           'Washington Redskins': 'wsh'}

# not sure which dict i'll need later, so ill keep them all for now
# converts name to abbreviations
# NFL_TEAMS and CONVERSION_CHART are imported by other files


def main():
    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS season_2020 (week int, team text, opponent text, loss_rank int, 
                win_rank int, outcome text, wins int, bye int,  power int, avg_power int, UNIQUE(week, team))""")

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
        c.execute("""INSERT INTO season_2020 (week, team) VALUES (?, ?)""", (0, "CURRENT_WEEK"))

    except sqlite3.IntegrityError:  # Already been initialized
        print("Database already initialized.")
        return

    # dummy team that holds the current week on the NFL season

    for team in NFL_TEAMS:
        source = urllib.request.urlopen(f'https://www.espn.com/nfl/team/schedule/_/name/{team}/season/2020').read()

        soup = bs.BeautifulSoup(source, features='lxml')

        table = soup.find_all('span')
        to_text = [i.text for i in table]

        second = False
        start = 0; end = len(to_text)
        for i in range(len(to_text)):
            # cleanse irreverent data

            if not second and to_text[i] == "tickets":
                start = i + 1
                second = True

            elif second and to_text[i] == "WK":
                end = i
                break

        to_text = to_text[start:end]
        shift = 0; bye = False
        for i in range(0, 17):  # populate table with schedule

            opponent = to_text[4 + (i * 6) + shift]

            if not bye and to_text[(i * 6) + 1].isnumeric():  # means its bye week
                shift = -5
                bye = i + 1
                opponent = "BYE WEEK"

            c.execute("""INSERT INTO season_2020 (week, team, opponent) VALUES (?, ?, ?)""",
                      (i + 1, team, opponent))
            c.execute("""UPDATE season_2020 SET bye = ? WHERE team = ? """, (bye, team))

        time.sleep(3)

    conn.commit()
    # Update the ranks based on the draft order of the last season
    source = urllib.request.urlopen('https://www.espn.com/nfl/draft2020/story/_/id/28886588/2020-nfl-draft-order-'
                                    'all-255-picks-seven-rounds-date-location')

    soup = bs.BeautifulSoup(source, features='lxml')
    table = soup.find_all("h2")
    ranking = []
    for i in table:

        if "Round" in i.text:
            continue

        if "from" in i.text:  # Pick was traded, get original team
            ranking.append(i.text[-5:-1])
            continue

        out = re.sub(r"[0-9.()-]", "", i.text)
        out = out[1:-1]
        ranking.append(out)

    for j in range(len(ranking)):

        if len(ranking[j]) == 4:

            team = ranking[j][1:].lower()
            c.execute("""UPDATE season_2020 SET loss_rank = ?, win_rank = ?, power = ?, avg_power = ? 
                         WHERE week = ? AND team = ?""", (j - 32, j + 1, j - 16, j - 16, 1, team))
            continue

        if "San Fran" in ranking[j]:
            ranking[j] = "San Francisco 49ers"

        c.execute("""UPDATE season_2020 SET loss_rank = ?, win_rank = ?, power = ?, avg_power = ? 
                    WHERE week = ? AND team = ?""", (j - 32, j + 1, j - 16, j - 16, 1, CONVERT[ranking[j]]))

    conn.commit()
    c.execute("""SELECT opponent FROM season_2020 WHERE team = ?""", ("nyj", ))
    jets = c.fetchall()

    c.execute("""SELECT opponent FROM season_2020 WHERE team = ?""", ("lac", ))
    chargers = c.fetchall()

    # jets = new york 2; chargers = los angeles 2
    for i in range(len(jets)):
        if jets[i][0] == "BYE WEEK":
            continue

        c.execute("""UPDATE season_2020 SET opponent = ? WHERE team = ? AND week = ?""",
                  ("New York 2 ", CONVERSION_CHART[jets[i][0]], i + 1))

    for i in range(len(chargers)):
        if chargers[i][0] == "BYE WEEK":
            continue

        c.execute("""UPDATE season_2020 SET opponent = ? WHERE team = ? AND week = ?""",
                  ("Los Angeles 2 ", CONVERSION_CHART[chargers[i][0]], i + 1))

    print("Success!")

    conn.commit()
    conn.close()

    predictions.main()


if __name__ == "__main__":

    if len(argv) == 1:  # default behavior
        main()

    elif len(argv) > 2:
        print("Can't pass multiple flags at the same time.")

    elif argv[1] == "--help":
        print("Create the initial database and populate it with the schedule for the year: \n\n--help: Shows usage and "
              "flags \n--week='current': If initializing after the first week of the season where 'current' is the "
              "last full week played \n--reset: Delete database and all data\n")

    elif argv[1][0:7] == "--week=":
        pass

    elif argv[1] == "--reset":
        pass

    else:
        print(f"Unknown flag: {argv[1]}")
