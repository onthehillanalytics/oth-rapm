"""
Python class for implementing Gramacy, Jensen, and Taddy (2013)'s RAPM model

Jordan Navin, On The Hill Analytics

created: 03-30-2021
"""

from oth_db_tools import Connection
import pandas as pd


class RAPMModel:

    def __init__(self):
        self.raw_data = None

    def get_raw_data(self, strength='5x5'):
        """
        gets raw goal data of a certain strength to train RAPM model
        :param strength: string; 5x5, 5x4, 4x5, etc. indicating on ice strength situation referencing home team first.
                         Default is 5x5.
        :return: self
        """
        q = f"""SELECT * FROM game_events WHERE "Strength" = '{strength}' AND "Event" = 'GOAL'"""
        with Connection('oth_hockey_main') as con:
            self.raw_data = pd.read_sql(q, con)

        return self

    def clean_for_modeling(self):
        """ prepares raw data for modeling"""

        # take only the columns from the raw data we need
        cols_to_keep = ['Ev_Team',
                        'Away_Team',
                        'Home_Team',
                        'awayPlayer1_id',
                        'awayPlayer2_id',
                        'awayPlayer3_id',
                        'awayPlayer4_id',
                        'awayPlayer5_id',
                        'awayPlayer6_id',
                        'homePlayer1_id',
                        'homePlayer2_id',
                        'homePlayer3_id',
                        'homePlayer4_id',
                        'homePlayer5_id',
                        'homePlayer6_id'
                        ]
        tmp = self.raw_data[cols_to_keep]

        # grab unique teams and players because modeling strategy requires variables for all unique
        #  teams (xt) and players (xp)
        teams = tmp['Home_Team'].unique()
        players = pd.Series(tmp[['awayPlayer1_id',
                                 'awayPlayer2_id',
                                 'awayPlayer3_id',
                                 'awayPlayer4_id',
                                 'awayPlayer5_id',
                                 'awayPlayer6_id',
                                 'homePlayer1_id',
                                 'homePlayer2_id',
                                 'homePlayer3_id',
                                 'homePlayer4_id',
                                 'homePlayer5_id',
                                 'homePlayer6_id']].values.flat).unique()
        # initialize data frames for each component of the design matrix X
        # teams
        xt = pd.DataFrame(index=range(0, len(tmp)), columns=teams)
        # players
        xp = pd.DataFrame(index=range(0, len(tmp)), columns=players)
        # NOTE: 1 for home team goal, -1 for away team goal
        y = pd.DataFrame(index=range(0, len(tmp)), columns=['scoring_team'])
        # now, loop through every goal and prepare the dfs
        for i in range(0, tmp.shape[0]):
            goal = tmp.loc[tmp.index == i, :]
            # do y first
            # if goal scoring team (Ev_Team) is the home team, they get a 1
            if goal['Ev_Team'].values[0] == goal['Home_Team'].values[0]:
                y.loc[y.index == i, 'scoring_team'] = 1
            # if its the away team they get a -1
            else:
                y.loc[y.index == i, 'scoring_team'] = -1

if __name__ == '__main__':
    print(RAPMModel().get_raw_data().clean_for_modeling())
