#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import shutil
import getpass
import argparse
import colorama
import BeautifulSoup as bs
from requests import session
import matplotlib.pyplot as plt


######### PLACE YOUR CONFIG HERE ##########

EMAIL       = "hayato11@hotmail.fr"
PLAYER_NAME = "The Answer"

RES_FILE           = "/home/gburet/.fantasy/res.txt"
BACKUP_RES_FILE    = "/home/gburet/.fantasy/backup_res.txt"


######### END OF CONFIG - START CODE ##########

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
        return self.get_results().get(player_name, None)


class Results(object):
    
    DATE_LABEL   = "Date"
    PLAYER_LABEL = "Players"
    
    def __init__(self):
        self.all_daily_results = {}

    @classmethod
    def json_loader(cls, path=RES_FILE):
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
            info = BACK_BLUE + ' ' + ENDC + ' '
            res  = str(player_id+1) + ". " + player_name.ljust(16) + " : " + str(daily_results.get_score_for_player(player_name))
            if player_name == PLAYER_NAME:
                res = BACK_CYAN + res + ENDC
            else:
                res += diff_score(daily_results.get_score_for_player(player_name), daily_results.get_score_for_player(PLAYER_NAME)) 
            info += res.ljust(LINE_LEN-2+2*6) + BACK_BLUE + ' ' + ENDC
    
            print info
        print BACK_BLUE + ' '*LINE_LEN + ENDC
    
     
    # Print players in a given order
    def print_players_and_evolution(self, old_index):
        current_results = self.all_daily_results[self.get_last_date_index()]
        old_results     = self.all_daily_results[old_index]
        
        print BACK_BLUE + ' '*LINE_LEN + ENDC
        for player_id, player_name in enumerate(current_results.get_player_names_sorted()):
            info = BACK_BLUE + ' ' + ENDC + ' '
            res  = str(player_id+1) + ". " + player_name.ljust(16) + " : " + str(current_results.get_score_for_player(player_name))
            if player_name == PLAYER_NAME:
                res = BACK_CYAN + res + ENDC + "      "
            else:
                res += diff_score(current_results.get_score_for_player(player_name), 
                                  current_results.get_score_for_player(PLAYER_NAME))
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
           
            shutil.copy(RES_FILE, BACKUP_RES_FILE)
            with open(RES_FILE, 'w') as f:
                f.write(json.dumps(dico))

            print "results saved !"
        else:
            print "results not saved"
    
    def get_results_from_busa(self):
        """
            Get teams, rankings, points from busa
            Return a dict
        """
        password = getpass.getpass()
        payload = {'logmod': '1',
                   'FrmEma': EMAIL,
                   'FrmPas': password}
    
        with session() as c_session:
            c_session.post('http://fantasy.2ics.net/asp/mai_utilisateurs/log_mod.asp', data=payload)
            response = c_session.get('http://fantasy.2ics.net/asp/mai_ligues/lig_fic.asp?ligid=4441')
            c_classement_html = response.text
    
        # Parse html
        data_html = bs.BeautifulSoup(c_classement_html)
    
        # Build rankings, points and team_name
        rankings = [int(elt.text.split('(')[1].replace('e)', ''))
                    for elt in data_html.findAll('span', attrs={'class': 'equipe-points'})]
        points = [(int(elt.text.split(' ')[0])) for elt in data_html.findAll('span', attrs={'class': 'equipe-points'})]
        team_name = [team.text.split('. ')[1] for team in data_html.findAll('span', attrs={'class': 'equipe-nom'})]
    
        # Build result dictionary
        data = {team : point for team, point, _ in zip(team_name, points, rankings)}
    
        last_index = self.get_last_date_index()
        self.all_daily_results[str(int(last_index)+1)] = DailyResults(data, None)
        self.print_players_and_evolution(last_index)
        

    # Print players in a given order
    def compare_results_with_date(self, date):
        date_index = self.get_index_date_with_date(date)
        if date_index:
            self.print_players_and_evolution(date_index)
        else:
            print "No results for this date: {}".format(date)
     
    # Print players in a given order
    def plot_results(self):
        plots = []
        player_names = self.get_player_names_sorted()
        for name in player_names:
            player_evolution = self.get_player_evolution(name)
            indexes          = [int(i) for i in player_evolution]
            indexes.sort()
            plots.extend(plt.plot(indexes, [player_evolution[str(i)] for i in indexes], Color.get_color(), label=name))

        plt.legend(handles=plots, bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
        plt.show()


if __name__ == "__main__":
    
    PARSER = argparse.ArgumentParser(description='Basket USA Fantasy League tool that helps points following')
    PARSER.add_argument('-l', default='', action="store_true", help='List players')
    PARSER.add_argument('-s', default='', action="store_true", help='Enter manually new results')
    PARSER.add_argument('-d', default='', action="store_true", help='Get results from Basket USA')
    PARSER.add_argument('-c', default='', help='Compare results with a date')
    PARSER.add_argument('-p', default='', action="store_true", help='Plot results')
    ARGS = PARSER.parse_args()
 
    R=Results.json_loader()

    if ARGS.l != '':
        R.print_results()
    elif ARGS.s != '':
        R.enter_players()
        R.save_results()
    elif ARGS.d != '':
        R.get_results_from_busa()
        R.save_results()
    elif ARGS.c != '':
        R.compare_results_with_date(ARGS.c)
    elif ARGS.p != '':
        R.plot_results()
    else:
        PARSER.print_help()

