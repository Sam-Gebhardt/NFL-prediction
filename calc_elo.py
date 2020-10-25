"""
Take the new data inputted from
scrape_data.py and calculate the
new ELO score for each team.
"""
import sqlite3
from initalize import NFL_TEAMS, CONVERSION_CHART


def bye_week_power(team: str, week: int) -> None:
    conn = sqlite3.connect("NFL.db")
    c = conn.cursor()

    c.execute("""SELECT * FROM season_2020 WHERE team = ? AND week = ?""", (team, week - 1))
    data = c.fetchall()[0]

    c.execute("""UPDATE season_2020 SET power = ? WHERE team = ? and week = ?""", (data[9], team, week))
    c.execute("""UPDATE season_2020 SET avg_power = ? WHERE team = ? AND week = ?""", (data[10], team, week))

    conn.commit()
    conn.close()


def calc_rankings(week: int) -> None:
    """Find the loss/win rank and update the db
    ***Power is updated AFTER the week happens***
    ***Win/loss rank are updated AFTER the week***
    """

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM season_2020 WHERE week = ? ORDER BY power DESC""", (week, ))
    ranking = c.fetchall()
    for i in range(len(ranking)):
        # print(f"{ranking[i][1]}/{week + 1}: {-(i + 1)} and {32 - i}")
        c.execute("""UPDATE season_2020 SET win_rank = ? WHERE team = ? AND week = ?""",
                  (32 - i, ranking[i][1], week))

        c.execute("""UPDATE season_2020 SET loss_rank = ? WHERE team = ? AND week = ?""",
                  (-(i + 1), ranking[i][1], week))

    conn.commit()
    conn.close()


def main(week=None):

    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()

    if not week:
        c.execute("""SELECT week FROM season_2020 WHERE team = 'CURRENT_WEEK'""")
        week = c.fetchall()[0][0]

    if week == 0:
        print("Must wait till week 2 or update the database.")
        return

    for team in NFL_TEAMS:

        c.execute("""SELECT * FROM season_2020 WHERE week = ? AND team = ?""", (week, team))
        data = c.fetchall()[0]

        if data[2] == "BYE WEEK":
            conn.commit()
            bye_week_power(team, week)
            continue

        c.execute("""SELECT * FROM season_2020 WHERE week = ? AND team = ?""", (week - 1, team))
        past = c.fetchall()[0]

        c.execute("""SELECT loss_rank, win_rank FROM season_2020 WHERE team = ? AND week = ?""",
                  (CONVERSION_CHART[data[2]], week - 1))
        ranks = c.fetchall()

        change = ranks[0][0]
        if data[5] == 'W':
            change = ranks[0][1]

        power = past[10] + change
        c.execute("""UPDATE season_2020 SET power = ? WHERE team = ? and week = ?""", (power, team, week))
        c.execute("""UPDATE season_2020 SET avg_power = ? WHERE team = ? AND week = ?""", ((power / week), team, week))

    conn.commit()
    conn.close()
    calc_rankings(week)


if __name__ == "__main__":
    # main()
    conn = sqlite3.connect('NFL.db')
    c = conn.cursor()
    c.execute("""SELECT team FROM season_2020 WHERE week = ? ORDER  BY avg_power DESC""", (6, ))
    order = c.fetchall()

    for i in range(len(order)):
        win = 32 - i
        loss = -(i + 1)
        # print(order[i][0], 32 - i, -(i + 1))
        c.execute("""UPDATE season_2020 SET loss_rank = ? WHERE team = ? and week = ?""", (loss, order[i][0], 6))
        c.execute("""UPDATE season_2020 SET loss_rank = ? WHERE team = ? and week = ?""", (loss, order[i][0], 6))
        conn.commit()

    week = 7
    for i in NFL_TEAMS:
        c.execute("""SELECT power, avg_power FROM season_2020 WHERE week = ? and team = ?""", (week - 1, i))
        power = c.fetchall()

        c.execute("""SELECT opponent, outcome FROM season_2020 WHERE week = ? and team = ?""", (week, i))
        opp = c.fetchall()[0]

        if opp[0] == "BYE WEEK":
            c.execute("""UPDATE season_2020 SET power = ? WHERE week = ? and team = ?""", (power[0][0], week, i))
            c.execute("""UPDATE season_2020 SET avg_power = ? WHERE week = ? and team = ?""", (power[0][1], week, i))
            continue

        c.execute("""SELECT loss_rank, win_rank FROM season_2020 WHERE week = ? and team = ?""",
                  (week - 1, CONVERSION_CHART[opp[0]]))
        ranks = c.fetchall()

        if opp[1] == "W":
            delta_power = power[0][0] + ranks[0][1]
            delta_avg_power = (power[0][1] + ranks[0][1]) / week
            c.execute("""UPDATE season_2020 SET power = ? WHERE week = ? and team = ?""", (delta_power, week, i))
            c.execute("""UPDATE season_2020 SET avg_power = ? WHERE week = ? and team = ?""", (delta_avg_power, week, i))

        else:
            delta_power = power[0][0] + ranks[0][0]
            delta_avg_power = (power[0][1] + ranks[0][0]) / week
            c.execute("""UPDATE season_2020 SET power = ? WHERE week = ? and team = ?""", (delta_power, week, i))
            c.execute("""UPDATE season_2020 SET avg_power = ? WHERE week = ? and team = ?""", (delta_avg_power, week, i))
        print("")

    conn.commit()
    conn.close()
    """Starting at week 4, re calc power, avg power and loss/win rank"""
    print("Success!")

