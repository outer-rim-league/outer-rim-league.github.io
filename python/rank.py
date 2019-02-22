from jutil import *
# from jutil_sci import *
from elopy import *
import pandas as pd
import numpy as np
# from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from jutil import *

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def read_tab(path='E:/Joe/Dropbox/projects/misc/xwing/league/outer-rim-league.github.io/python/games.tab'):
    return [x.split('\t') for x in f_readlines(path)]

def main():
    global wantedList

    wantedList = WantedList()

    weeks = [1,2]

    # # ranks = get_ratings()
    # for player in ranks:
    #     ranks[player] = 0


    i = 0

    get_sheet('1Fre58jzOAyedQGnWCrl3ZYjVwPbevlgcVPwV2CrmZ4w', 'Game Log!A1:J40')
    rank()

def rank():
    mwl = wantedList

    week_nums = list(set(mwl.df['Week Played'].values))

    for week_num in week_nums:

        # mwl.report_ranks()

        print(rsf('-- Week ~week_num --'))


        match_row_tpl = '~p1-12 ~p2-12 ~destr1-8 ~destr2-8 ~score1-8 ~score2-8 ~r1-15 ~r2-15'


        game_nums = mwl.iter_init(week_num)


        iterMax = 999
        for iter in np.arange(1,9,dtype=int):
        # for iter in range(iterMax):
            iter = int(iter)
            mwl.iter = iter
            iter_print_num = 2
            iter_print = iter <= iter_print_num

            if iter_print:
                print(rsf('\nRandom order #{iter}:'))
                p1, p2, destr1, destr2, score1, score2, r1, r2  = 'Player 1', 'Player 2', 'Destr 1', 'Destr 2', 'Score 1', 'Score 2', 'Rank 1', 'Rank 2'
                print(rsf(match_row_tpl))

            mwl.iter_add()
            game_nums_randSort = np.random.permutation(game_nums)
            if iter == 1:
                game_nums_randSort = game_nums  # debug

            for game_num in game_nums_randSort:

                p1, p2, destr1, destr2, game = mwl.get_game(game_num)
                game = game.to_dict()
                new_player = game['New player(s)?'] == 'Yes'

                if 'Juan' in p1:
                    _=0
                if new_player:
                    continue
                winner = 1 if (destr1 > destr2) else 2
                destr1 = float(destr1)
                destr2 = float(destr2)

                mov1 = destr1 - destr2


                ratio1 = destr1 / (destr1 + destr2)
                ratio2 = destr2 / (destr1 + destr2)
                score1 = (0.25 if winner == 1 else 0) + (0.75 * ratio1)
                score2 = (0.25 if winner == 2 else 0) + (0.75 * ratio2)

                # score2 = ((0.5 if winner == 2 else 0) + 0.75 * p2pts)*0.5

                pr1, pr2 = int(mwl.get_iter_rank(p1)), int(mwl.get_iter_rank(p2))
                mwl.iter_match(p1, p2, score1, score2)
                score1, score2 = round(score1, 2), round(score2, 2)
                destr1, destr2 = int(destr1), int(destr2)
                r1, r2 = int(mwl.get_iter_rank(p1)), int(mwl.get_iter_rank(p2))

                r1 = rsf('~pr1-4 > ~r1')
                r2 = rsf('~pr2-4 > ~r2')
                if iter_print:
                    print(rsf(match_row_tpl))

            mwl.iter_rank()

        left = iterMax - iter_print_num
        print(rsf('\n~left more random iterations..\n\nAveraged rantings:'))
        mwl.iter_finalize()

        print('')
        mwl.report_ranks()
        print('')

def get_sheet(sheet_id, range):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=range).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        f_clear('games.tab')
        for row in values:
            tab_row = '\t'.join(row)
            f_addline('games.tab', tab_row)
            # Print columns A and E, which correspond to indices 0 and 4.
            # print('%s, %s' % (row[0], row[4]))
            print(tab_row)


class Player():
    def __init__(self, list, name):
        self.list = list
        self.df = list.df
        self.name = name
        self.elo = self.list.elo
        self.elo.addPlayer(name)
        self.eloPlayer = self.elo.getPlayer(name)
        self.opps = []
        self.bounties = {'factions_played':[], 'factions_won':[], 'formats_played':[], 'formats_won':[], 'games':[]}
        # self.rating = self.eloPlayer.rating
        _=0
        pass

    def report(self):
        self.bounties = {'factions_played': [], 'factions_won': [], 'formats_played': [], 'formats_won': [],
                         'games': []}
        self.opps = []
        self.games = []
        for game, row in self.df.iterrows():
            p1, p2, format = row['Player 1'], row['Player 2'], row['Format']
            if self.name in [p1, p2]:
                self.bounties['games'].append(row)
                self.games.append(row)
                is_p1 = (self.name == p1)
                opp = p2 if is_p1 else p1
                faction = row['Faction'] if is_p1 else row['Faction.1']
                p1_dest = row['Pts Destroyed']
                p2_dest = row['Pts Destroyed.1']
                winner = (p1_dest >= p2_dest) if is_p1 else (p2_dest >= p1_dest)

                if not faction in self.bounties['factions_played']:
                    self.bounties['factions_played'].append(faction)
                if winner and (not faction in self.bounties['factions_won']):
                    self.bounties['factions_won'].append(faction)

                if not format in self.bounties['formats_played']:
                    self.bounties['formats_played'].append(format)
                if winner and (not format in self.bounties['formats_won']):
                    self.bounties['formats_won'].append(format)

                # print row
                if not opp in self.opps:
                    self.opps.append(opp)

        rating = int(self.eloPlayer.rating)
        num_opps = len(self.opps)
        num_games = len(self.games)

        factions_played = len(self.bounties['factions_played'])
        factions_won = len(self.bounties['factions_won'])
        formats_played = len(self.bounties['formats_played'])
        formats_won = len(self.bounties['formats_won'])

        factions = f'{factions_played} / {factions_won}'
        formats = f'{formats_played} / {formats_won}'

        factions_played = min(3,factions_played)
        factions_won = min(3,factions_won)
        formats_played = min(3,formats_played)
        formats_won = min(3,formats_won)

        game_credits = min(10, len(self.bounties['games']))

        credits = factions_played + factions_won + formats_played + formats_won + game_credits

        new_player = 'yes' in str(row['New player(s)?']).lower()
        if new_player:
            credits += 1

        # if

        if 'Juan B' in self.name:
            _ =0

        if not (num_games >= 3): #  ((num_games >= 3) and (num_opps >= 2)):  #(num_opps >= 2): #
            rating = 0


        # header, col_widths =  self.players[0].rank_cols, self.players[0].rank_widths

        self.rank_cols = 'Name', 'Notoriety', 'Change', 'Games', 'Opponents', 'Credits (Bounties)', 'Factions (Flew/Won)', 'Formats (Flew/Won)'
        self.rank_widths = 12, 12, 12, 12, 12, 20, 20, 20

        return (self.name, rating, [self.rating_delta, num_games, num_opps, credits, factions, formats])
        # print rsf('{self.name}-12 {rating}-8 {num_opps}-8')



        # _=0


class WantedList():

    def __init__(self):
        self.df = pd.read_csv('games.tab', sep='\t')



        players1 = list(self.df['Player 1'].values)
        players2 = list(self.df['Player 2'].values)
        players = sorted(set(players1 + players2))
        self.elo = Implementation()
        self.elo.k_factor = 50
        self.players=[]
        for name in players:
            self.addPlayer(name)
            # self.elo.addPlayer(player)

    def addPlayer(self, name):
        self.players.append(Player(self, name))
        # self.elo.addPlayer(player)

    def get_rank(self, player):
        return self.elo.getPlayerRating(player)
    def get_game(self,game_num):
        row = self.df.loc[game_num]
        return row['Player 1'], row['Player 2'], row['Pts Destroyed'], row['Pts Destroyed.1'], row

    def iter_init(self, week_num):
        '''ran at the start of a week before permutaion loop'''

        self.iterDicts = []
        week_game_nums = self.df[self.df['Week Played'] == week_num].index.values
        return week_game_nums

    def get_player(self, name):
        for player in self.players:
            if name == player.name:
                return player
            _=0

    def get_iter_rank(self, player):
        return self.iterElo.getPlayerRating(player)

    def report_ranks(self):

        # tpl= '{name}-12 {rating}-12 {delta}-12 {games}-8 {opps}-8 '
        #
        # name, rating, delta, games, opps = 'Name', 'Notoriety', 'Change', 'Games', 'Opponents'
        # f_writeline('./ranks.tab','\t'.join([name, rating, delta, games, opps]))

        # print rsf(tpl)
        reports = [player.report() for player in self.players]

        reports = sorted(reports, key=lambda x:int(x[1])*-1 + x[2][3]*-0.01)  # rank by credits after notoriety

        # for name, rating, delta, games, opps in reports:

        header, col_widths =  self.players[0].rank_cols, self.players[0].rank_widths

        for val, col_width in zip(header, col_widths):
            print(('%-' + str(col_width) + 's') % str(val), end=' ')

        print('')
        f_clear('./ranks.tab')
        for name, rating, row in reports:

            # for player in self.elo.players:
            #     rating = int(player.rating)
            #     row = [str(x) for x in [name, rating, delta, games, opps]]

            if rating == 0:
                rating = '--'
                row[0] = '--'
            row = [name] + [rating] + row
            row = [str(x) for x in row]
            f_addline('./ranks.tab', '\t'.join(row))

            if 'Juan' in name:
                _=0

            for val, col_width in zip(row, col_widths):
                print(('%-' + str(col_width) + 's') % str(val), end=' ')

            print('')


            # print rsf(tpl)

    def iter_add(self):
        '''ran at the start of a permutation'''

        self.iterElo = copy.deepcopy(self.elo)

        # if self.iter>1:
        #     print '!should be 1000 now for week 1!'
        # self.report_ranks()
        # if self.iter>1:
        #     _=0

    def iter_match(self, p1, p2, s1, s2):
        '''ran for each match inside a permutation'''

        players = [x.name for x in self.iterElo.players]
        for p in [p1,p2]:
            if not p in players:
                rating = 1000
                # if p in self.elo.players:
                #     rating = self.elo.getPlayerRating(p)
                self.elo.addPlayer(p, rating)
                self.iterElolo.addPlayer(p, rating)

        self.iterElo.recordMatchMoV(p1,p2,s1,s2)

    def iter_rank(self):
        '''ran at the conclusion of each permutation'''

        iterRanks = OrderedDict()
        for player in self.iterElo.players:
            iterRanks[player.name] = player.rating

        self.iterDicts.append(copy.copy(iterRanks))

    def iter_finalize(self):
        '''ran at the conclusion of each week'''

        new_ratings = OrderedDict()
        for iterDict in self.iterDicts:
            for name in iterDict:
                if name not in new_ratings:
                    new_ratings[name] = []

                new_ratings[name].append(iterDict[name])

        for name, ranks in list(new_ratings.items()):
            player = self.elo.getPlayer(name)
            new_rating = np.mean(ranks)
            old_rating = player.rating
            self.get_player(name).rating_delta = int(new_rating - old_rating)
            player.rating = new_rating

            _=0



# def print_ratings(*args):
#     get_ratings(*args, pr=True)
#
# def get_ratings(pr=False):
#
#     ranks = OrderedDict()
#     for player in elo.players:
#         name, rating = player.name, player.rating
#         rating = rating
#         _=0
#
#         if pr:print rsf('~name-10~rating-5  '),
#         ranks[name] = rating
#
#     if pr:print ''
#
#     return ranks
#
#     # print int(i.getPlayerRating("Hank")), i.getPlayerRating("Bill")

if __name__ == '__main__':
    main()