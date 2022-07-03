"""
Holds a tuple of all NFL teams abbreviations and dicts of commonly needed conversions
"""

NFL_TEAMS = ('ne', 'mia', 'nyj', 'buf', 'bal', 'pit', 'cin', 'cle', 'hou', 'ind', 'ten', 'jax',
'kc', 'lac', 'den', 'lv', 'ari', 'lar', 'sea', 'sf', 'dal', 'phi', 'wsh', 'nyg',\
'chi', 'min', 'gb', 'det', 'no', 'car', 'atl', 'tb')


CITY_T0_ABBREV = {
    'Arizona': 'ari', 'Atlanta': 'atl', 'Baltimore': 'bal', 'Buffalo': 'buf', 'Carolina': 'car',
    'Chicago': 'chi', 'Cincinnati': 'cin', 'Cleveland': 'cle', 'Dallas': 'dal', 'Denver': 'den',
    'Detroit': 'det', 'Green Bay': 'gb', 'Houston': 'hou', 'Indianapolis': 'ind',
    'Jacksonville': 'jax', 'Kansas City': 'kc', 'Los Angeles': 'lar', 'Los Angeles 2': 'lac',
    'Miami': 'mia', 'Minnesota': 'min', 'New England': 'ne', 'New Orleans': 'no',
    'New York': 'nyg', 'New York 2': 'nyj', 'Las Vegas': 'lv', 'Philadelphia': 'phi',
    'Pittsburgh': 'pit', 'San Francisco': 'sf', 'Seattle': 'sea', 'Tampa Bay': 'tb',
    'Tennessee': 'ten', 'Washington': 'wsh'
                    }

ABBREV_TO_FULL = {
    'ari': 'Arizona Cardinals', 'atl': 'Atlanta Falcons', 'bal': 'Baltimore Ravens',
    'buf': 'Buffalo Bills', 'car': 'Carolina Panthers', 'chi': 'Chicago Bears',
    'cin': 'Cincinnati Bengals', 'cle': 'Cleveland Browns', 'dal': 'Dallas Cowboys',
    'den': 'Denver Broncos', 'det': 'Detroit Lions', 'gb': 'Green Bay Packers',
    'hou': 'Houston Texans', 'ind': 'Indianapolis Colts', 'jax': 'Jacksonville Jaguars',
    'kc': 'Kansas City Chiefs', 'Los Angeles Chargers': 'lac', 'lar': 'Los Angeles Rams',
    'mia': 'Miami Dolphins', 'min': 'Minnesota Vikings', 'ne': 'New England Patriots',
    'no': 'New Orleans Saints', 'nyg': 'New York Giants', 'nyj': 'New York Jets',
    'lv': 'Las Vegas Raiders', 'phi': 'Philadelphia Eagles', 'pit': 'Pittsburgh Steelers',
    'sf': 'San Francisco 49ers', 'sea': 'Seattle Seahawks', 'tb': 'Tampa Bay Buccaneers',
    'ten': 'Tennessee Titans', 'wsh': 'Washington Football Team'
                    }

FULL_TO_ABBREV = {
    'Arizona Cardinals': 'ari', 'Atlanta Falcons': 'atl', 'Baltimore Ravens': 'bal',
    'Buffalo Bills': 'buf', 'Carolina Panthers': 'car', 'Chicago Bears': 'chi',
    'Cincinnati Bengals': 'cin', 'Cleveland Browns': 'cle', 'Dallas Cowboys': 'dal',
    'Denver Broncos': 'den', 'Detroit Lions': 'det', 'Green Bay Packers': 'gb',
    'Houston Texans': 'hou', 'Indianapolis Colts': 'ind', 'Jacksonville Jaguars': 'jax',
    'Kansas City Chiefs': 'kc', 'Los Angeles Chargers': 'lac', 'Los Angeles Rams': 'lar',
    'Miami Dolphins': 'mia', 'Minnesota Vikings': 'min', 'New England Patriots': 'ne',
    'New Orleans Saints': 'no', 'New York Giants': 'nyg', 'New York Jets': 'nyj',
    'Las Vegas Raiders': 'lv', 'Philadelphia Eagles': 'phi', 'Pittsburgh Steelers': 'pit',
    'San Francisco 49ers': 'sf', 'Seattle Seahawks': 'sea', 'Tampa Bay Buccaneers': 'tb',
    'Tennessee Titans': 'ten', 'Washington Football Team': 'wsh'
        }
