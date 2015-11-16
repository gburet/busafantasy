#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import argparse
import colorama

######### PLACE YOUR CONFIG HERE ##########

RES_FILE    = "/home/gburet/.fantasy/res.txt"
PLAYER_NAME = "The Answer"


######### END OF CONFIG - START CODE ##########

LINE_LEN = 48

ENDC    = colorama.Style.RESET_ALL
RED     = colorama.Fore.RED     + colorama.Style.BRIGHT
GREEN   = colorama.Fore.GREEN + colorama.Style.BRIGHT

BACK_BLUE = colorama.Back.BLUE + colorama.Style.BRIGHT
BACK_CYAN = colorama.Back.CYAN + colorama.Style.BRIGHT

# Get last saved results
with open(RES_FILE) as f:
    lines = f.readlines()
RESULTS = {r.split(':')[0] : int(r.split(':')[1].strip()) for r in lines if ':' in r}

# Methods to sort players, get score difference, ...
def sort_players(dico):
    return sorted(dico, key=lambda x: dico[x], reverse=True)

def diff_score(val1, val2):
    if val1 > val2:
        return RED + " ({})".format(val2-val1) + ENDC
    else:
        return GREEN + " (+{})".format(val2-val1) + ENDC


# Print players in a given order
def print_players(players):
    print BACK_BLUE + ' '*LINE_LEN + ENDC
    for index, player in enumerate(players):
        info = BACK_BLUE + ' ' + ENDC + ' '
        res  = str(index+1) + ". " + player.ljust(16) + " : " + str(RESULTS[player])
        if player == PLAYER_NAME:
            res = BACK_CYAN + res + ENDC
        else:
            res += diff_score(RESULTS[player], RESULTS[PLAYER_NAME]) 
        info += res.ljust(LINE_LEN-2+2*6) + BACK_BLUE + ' ' + ENDC

        print info
    print BACK_BLUE + ' '*LINE_LEN + ENDC

# Print players in a given order
def print_players_and_evolution(players, dico):
    print BACK_BLUE + ' '*LINE_LEN + ENDC
    for index, player in enumerate(players):
        info = BACK_BLUE + ' ' + ENDC + ' '
        res  = str(index+1) + ". " + player.ljust(16) + " : " + str(dico[player])
        if player == PLAYER_NAME:
            res = BACK_CYAN + res + ENDC
        else:
            res += diff_score(dico[player], dico[PLAYER_NAME]) 
        res += "   (+{})".format(dico[player]-RESULTS[player])
        info += res.ljust(LINE_LEN-2+2*6) + BACK_BLUE + ' ' + ENDC

        print info
    print BACK_BLUE + ' '*LINE_LEN + ENDC



# Enter new values
def enter_players():
    new_results = {}
    for player in sort_players(RESULTS):
        print "Entrer le nouveau score de {}".format(player)
        score = int(raw_input())
        new_results[player] = score
    print ""
    print_players_and_evolution(sort_players(new_results), new_results)
    return new_results


def save_results(dico):
    print 'save results ? (y/n)'
    ans = raw_input()
    if ans == "y":
        with open(RES_FILE, 'w') as f:
            f.write('\n'.join(["{}:{}".format(k,d) for k,d in dico.iteritems()]))
        print "results saved !"
    else:
        print "results not saved"


if __name__ == "__main__":
    
    PARSER = argparse.ArgumentParser(description='Suivi des points pour la Fantasy League')
    PARSER.add_argument('-l', default='', action="store_true",
                        help='Liste les joueurs')
    PARSER.add_argument('-s', default='', action="store_true",
                        help='Entre de nouveaux résultats')
    ARGS = PARSER.parse_args()

    if ARGS.l != '':
        print_players(sort_players(RESULTS))
    elif ARGS.s != '':
        NEW = enter_players()
        save_results(NEW)
    else:
        PARSER.print_help()


