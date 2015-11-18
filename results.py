#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
import databusa

if __name__ == "__main__":

    PARSER = argparse.ArgumentParser(description='Basket USA Fantasy League tool that helps points following')
    PARSER.add_argument('-l', default='', action="store_true", help='List players')
    PARSER.add_argument('-s', default='', action="store_true", help='Enter manually new results')
    PARSER.add_argument('-d', default='', action="store_true", help='Get results from Basket USA')
    PARSER.add_argument('-c', default='', help='Compare results with a date')
    PARSER.add_argument('-p', default='', action="store_true", help='Plot results')
    PARSER.add_argument('-t', default='', action="store_true", help='Get team of the weak')
    ARGS = PARSER.parse_args()
    
    
    R=databusa.Results.json_loader()

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
    elif ARGS.t != '':
        R.get_current_team_from_busa()
    else:
        PARSER.print_help()
