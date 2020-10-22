# NFL-prediction
Scrape game data from ESPN and use a basic ELO model to try and predict the winners of NFL games.

## Methodology

Originally, I created this model in hopes of using it to help make educated bets on NFL games, but I quickly realized the complexity of that task is a little outside of my mathematical knowledge. So now, I do it just for fun.

The model uses a basic weighted ELO to predict the winners of each NFL match ups every-week. Each time a time wins or looses their opponents power is added or subtracted from the original teams power. For example, say the Seahawks have the best record in the NFL at 6 - 1 and have played against above average teams. They would have a power somewhere in the mid 20s (max is 32 due to the fact that there are that many teams in the NFL). On the other hand, say the Charger are tied with the same record at 6 - 1, but they have played below average teams for the most part. Then their power would somewhere in around 10. Basically, strength of schedule and quality of wins/losses attempt to predict the winning team.

An important factor to consider is that at some point sports come down to luck and randomness, so an accurate model is impossible.

## Accuracy

Overall, the model hovers around 60% accuracy. I'm tracking the 2020 season here.

## Usage

The program is broken up into separate files for ease of use. In order to use the model to:

1. Before the season starts, run initalize.py which uses draft order to rank the teams and create predictions for Week 1.
2. Run update.py to scrape data in relation to wins and losses
3. Run calc_elo.py to update ELO scores of each team
4. Run predictions which outputs the predicted winners of each game

