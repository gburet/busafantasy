#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import shutil
import getpass
import colorama
import BeautifulSoup as bs
from requests import session
import datetime
import base64
import plotly.plotly as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt

import config


try:
    from config import PASSWORD
    PASSWORD = base64.b64decode(PASSWORD)
except ImportError:
    PASSWORD = getpass.getpass()
    with open('config.py', 'a') as CONFIG_FILE:
        CRYPTED_PWD = base64.b64encode(PASSWORD)
        PWD_LINE = 'PASSWORD="{0}"'.format(CRYPTED_PWD)
        CONFIG_FILE.write(PWD_LINE)

DATE_LABEL   = "Date"
PLAYER_LABEL = "Players"

LINE_LEN = 48

ENDC    = colorama.Style.RESET_ALL
RED     = colorama.Fore.RED     + colorama.Style.BRIGHT
GREEN   = colorama.Fore.GREEN + colorama.Style.BRIGHT

BACK_BLUE = colorama.Back.BLUE + colorama.Style.BRIGHT
BACK_CYAN = colorama.Back.CYAN + colorama.Style.BRIGHT



def diff_score(val1, val2):
    if val1 > val2:
        return RED + " ({})".format(val2-val1) + ENDC
    else:
        return GREEN + " (+{})".format(val2-val1) + ENDC

def enter_date():
    print "Enter new date "
    new_date = raw_input()
    return new_date


class Color(object):
    COLORS = 'rgbkycm'
    INDEX  = 0

    @classmethod
    def get_color(cls):
        color = cls.COLORS[cls.INDEX]
        cls.INDEX = (cls.INDEX + 1) % len(cls.COLORS)
        return color


class Result(object):

    def __init__(self, player_name, player_result):
        self.player_name = player_name
        self.player_result = player_result

    def get_player_name(self):
        return self.player_name

    def get_player_result(self):
        return self.player_result


class DailyResults(object):

    def __init__(self, results, date):
        self.date = date
        self.results = [Result(name, results[name]) for name in results]

    def get_player_names(self):
        return [r.get_player_name() for r in self.results]

    def get_player_names_sorted(self):
        sorted_results = sorted(self.results, key=lambda x: x.get_player_result(), reverse=True)
        return [s.get_player_name() for s in sorted_results]

    def get_results(self):
        return {r.get_player_name() : r.get_player_result() for r in self.results}

    def get_date(self):
        return self.date

    def get_score_for_player(self, player_name):
        return self.get_results().get(player_name)


class Results(object):

    DATE_LABEL   = "Date"
    PLAYER_LABEL = "Players"

    def __init__(self):
        self.all_daily_results = {}

    @classmethod
    def json_loader(cls, path=None):
        if path is None:
            path = config.RES_FILE

        with open(path) as json_file:
            data = json_file.read()
        all_results = json.loads(data)

        inst = cls()
        for result in all_results:
            inst.all_daily_results[result] = DailyResults(all_results[result][cls.PLAYER_LABEL],
                                                          all_results[result][cls.DATE_LABEL])

        return inst

    def get_player_names_sorted(self):
        last_date_index = self.get_last_date_index()
        return self.all_daily_results[last_date_index].get_player_names_sorted()

    def get_last_date_index(self):
        return str(max([int(s) for s in self.all_daily_results.keys()]))

    def get_index_date_with_date(self, date):
        for date_index in self.all_daily_results:
            if date == self.all_daily_results[date_index].get_date():
                return date_index
        return None

    def get_last_sunday_index(self):
        """
        @return: index of the last sunday index in res file
        """
        today = datetime.date.today()
        last_sunday = today - datetime.timedelta(days=-today.weekday(), weeks=1) + datetime.timedelta(days=6, weeks=0)
        last_sunday_str = '{0}/{1}/{2}'.format(last_sunday.day, last_sunday.month ,last_sunday.year)
        return str([key for key in self.all_daily_results.keys()
                    if self.all_daily_results[key].get_date() == last_sunday_str][0])

    # Print players in a given order
    def get_player_evolution(self, player_name):
        evolution = {}
        for date_id in self.all_daily_results:
            score = self.all_daily_results[date_id].get_score_for_player(player_name)
            if score:
                evolution[date_id] = score
        return evolution

    # Print players in a given order
    def print_results(self, date_index=None):
        if date_index is None:
            date_index = self.get_last_date_index()
        print BACK_BLUE + ' '*LINE_LEN + ENDC
        daily_results = self.all_daily_results[date_index]
        for player_id, player_name in enumerate(daily_results.get_player_names_sorted()):
            res  = str(player_id+1) + ". " + player_name.ljust(16) + " : " + str(daily_results.get_score_for_player(player_name))
            if player_name == config.PLAYER_NAME:
                res = BACK_CYAN + res + ENDC
            else:
                res += diff_score(daily_results.get_score_for_player(player_name),
                                  daily_results.get_score_for_player(config.PLAYER_NAME))
            print res
        print BACK_BLUE + ' '*LINE_LEN + ENDC

    # Print players in a given order
    def print_players_and_evolution(self, old_index):
        current_results = self.all_daily_results[self.get_last_date_index()]
        old_results     = self.all_daily_results[old_index]

        print BACK_BLUE + ' '*LINE_LEN + ENDC
        for player_id, player_name in enumerate(current_results.get_player_names_sorted()):
            info = BACK_BLUE + ' ' + ENDC + ' '
            res  = str(player_id+1) + ". " + player_name.ljust(16) + " : " + str(current_results.get_score_for_player(player_name))
            if player_name == config.PLAYER_NAME:
                res = BACK_CYAN + res + ENDC + "      "
            else:
                res += diff_score(current_results.get_score_for_player(player_name),
                                  current_results.get_score_for_player(config.PLAYER_NAME))
            res += "   (+{})".format(current_results.get_score_for_player(player_name) - old_results.get_score_for_player(player_name))
            info += res.ljust(LINE_LEN-2+2*6) + BACK_BLUE + ' ' + ENDC

            print info
        print BACK_BLUE + ' '*LINE_LEN + ENDC


    # Enter new values
    def enter_players(self):
        new_date = enter_date()

        new_results = {}
        for player in self.get_player_names_sorted():
            print "Enter new score for {}".format(player)
            score = int(raw_input())
            new_results[player] = score
        print ""

        last_index = self.get_last_date_index()

        self.all_daily_results[str(int(last_index)+1)] = DailyResults(new_results, new_date)

        self.print_players_and_evolution(last_index)
        return new_results


    def save_results(self):
        print 'save results ? (y/n)'
        ans = raw_input()
        if ans == "y":
            dico = {}
            for key in self.all_daily_results:
                dico[key] = {self.DATE_LABEL   : self.all_daily_results[key].get_date(),
                             self.PLAYER_LABEL : self.all_daily_results[key].get_results()}

            shutil.copy(config.RES_FILE, config.BACKUP_RES_FILE)
            with open(config.RES_FILE, 'w') as f:
                f.write(json.dumps(dico))

            print "results saved !"
        else:
            print "results not saved"

    def get_buddy_team(self, team_name):
        """
        Explore weekly rankings to get buddies teams
        return team
        """
        payload = {'logmod': '1',
                   'FrmEma': config.EMAIL,
                   'FrmPas': PASSWORD}
        current_week = datetime.date.today().isocalendar()[1]
        busa_week = current_week - 19  # Magic

        if team_name == self.get_current_player_name_from_busa():
            return self.get_current_team_from_busa()

        with session() as c_session:
            c_session.post('http://fantasy.2ics.net/asp/mai_utilisateurs/log_mod.asp', data=payload)
            page_index = 0
            while True:
                weekly_ranking_url = '{0}{1}{2}{3}'.format('http://fantasy.2ics.net/asp/mai_classement/cla_sem_lst.asp?perid=',
                                                            busa_week,
                                                            '&rchmod=0&rchmot=&rchmoi=&rchann=&rchsec=0&rchzon=0&rchpos=',
                                                            page_index)
                c_ranking = c_session.get(weekly_ranking_url)
                c_ranking_html = c_ranking.text
                print 'Browsing busa ranking page {0}...'.format(page_index)
                if 'pts' in c_ranking_html:  # Ensure ranking page is available
                    if team_name in c_ranking_html:
                        c_ranking_parsed = bs.BeautifulSoup(c_ranking_html)
                        teams = [team.text.split('. ')[1]
                                 for team in c_ranking_parsed.findAll('span', attrs={'class': 'equipe-nom'})]
                        rosters = [elt.text.replace('&nbsp;', '')
                                   for elt in c_ranking_parsed.findAll('li') if elt.text.startswith('&nbsp')]

                        result = {team: rosters[6 * index: 6 * (index + 1)] for index, team in enumerate(teams)}

                        print BACK_BLUE + '\n'.join(result.get(team_name, [])) + ENDC
                        break
                    else:
                        page_index += 1
                        continue
                else:
                    print '{0} team not found'.format(team_name)
                    break

    @staticmethod
    def get_current_team_from_busa():
        """
            Get current team
            return a dict
        """
        payload = {'logmod': '1',
                   'FrmEma': config.EMAIL,
                   'FrmPas': PASSWORD}
        with session() as c_session:
            c_session.post('http://fantasy.2ics.net/asp/mai_utilisateurs/log_mod.asp', data=payload)
            roster = c_session.get('http://fantasy.2ics.net/asp/mai_rosters/ros_lst.asp')
            roster_html = roster.text

        # Parse html page
        roster_parsed = bs.BeautifulSoup(roster_html)

        # Get current player name
        players = roster_parsed.findAll('span', attrs={'class': 'nom'})
        evals = roster_parsed.findAll('span', attrs={'class': 'annexe'})

        res = ['{}: {}'.format(player.text.replace('&nbsp;', ' ').ljust(24, ' '), c_eval.text)
              for player, c_eval in zip(players, evals)]

        print BACK_BLUE + '\n'.join(res) + ENDC

    @staticmethod
    def get_current_player_name_from_busa():
        """
            Get current player team name
            return a string
        """
        payload = {'logmod': '1',
                   'FrmEma': config.EMAIL,
                   'FrmPas': PASSWORD}
        with session() as c_session:
            c_session.post('http://fantasy.2ics.net/asp/mai_utilisateurs/log_mod.asp', data=payload)
            roster = c_session.get('http://fantasy.2ics.net/asp/mai_rosters/ros_lst.asp')
            roster_html = roster.text

        # Parse html page
        roster_parsed = bs.BeautifulSoup(roster_html)

        # Get current player name
        player_name = roster_parsed.findAll('li', attrs={'class': 'team'})

        if player_name:
            return player_name[0].text

    def get_results_from_busa(self):
        """
            Get teams, rankings, points from busa
            Return a dict
        """
        payload = {'logmod': '1',
                   'FrmEma': config.EMAIL,
                   'FrmPas': PASSWORD}

        with session() as c_session:
            c_session.post('http://fantasy.2ics.net/asp/mai_utilisateurs/log_mod.asp', data=payload)
            ranking = c_session.get('http://fantasy.2ics.net/asp/mai_ligues/lig_fic.asp?ligid=4441')
            ranking_html = ranking.text

        # Parse html page
        ranking_parsed = bs.BeautifulSoup(ranking_html)

        # Build rankings, points and team_name
        rankings = [int(elt.text.split('(')[1].replace('e)', ''))
                    for elt in ranking_parsed.findAll('span', attrs={'class': 'equipe-points'})]
        points = [(int(elt.text.split(' ')[0])) for elt in ranking_parsed.findAll('span', attrs={'class': 'equipe-points'})]
        team_name = [team.text.split('. ')[1] for team in ranking_parsed.findAll('span', attrs={'class': 'equipe-nom'})]

        # Fill dict returned
        data = {team : point for team, point, _ in zip(team_name, points, rankings)}

        last_index = self.get_last_date_index()

        # Get current date
        d = datetime.datetime.now()
        c_date = '{0}/{1}/{2}'.format(d.day, d.month, d.year)

        # Fill current results in all_daily_results dict
        index = str(int(last_index)+1)
        for key, value in self.all_daily_results.iteritems():
            # Override a daily result with same date
            if c_date == self.all_daily_results[key].date:
                index = key
                break

        self.all_daily_results[index] = DailyResults(data, c_date)
        self.print_players_and_evolution(last_index)


    # Print players in a given order
    def compare_results_with_date(self, date):
        date_index = self.get_index_date_with_date(date)
        if date_index:
            self.print_players_and_evolution(date_index)
        else:
            print "No results for this date: {}".format(date)


    def weekly_ranking(self):
        """
        return: current week ranking
        """



    def plot_results(self):
        """
        Plot historical ranking
        """
        #plots = []
        plots_py = []
        player_names = self.get_player_names_sorted()
        for name in player_names:
            player_evolution = self.get_player_evolution(name)
            indexes    = [int(i) for i in player_evolution]
            indexes_py = [str(self.all_daily_results[d].get_date()) for d in player_evolution.keys()]
            indexes.sort()
            indexes_py.sort()
            y_axis_data = [player_evolution[str(i)] for i in indexes]
            #plots.extend(plt.plot(indexes, y_axis_data, Color.get_color(), label=name))
            plots_py.append(go.Scatter(x=indexes_py, y=y_axis_data, mode='lines+markers', name=name))

            layout = go.Layout(
                title='Basket USA Fantasy historic',
                xaxis=dict(title='',
                           titlefont=dict(family='Courier New, monospace', size=18, color='#7f7f7f')
                           ),
                yaxis=dict(title='Pts',
                           titlefont=dict(family='Courier New, monospace', size=18, color='#7f7f7f')
                           )
            )

        fig = go.Figure(data=plots_py, layout=layout)
        py.plot(fig, filename='busa')
        #plt.legend(handles=plots, bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
        #plt.show()
