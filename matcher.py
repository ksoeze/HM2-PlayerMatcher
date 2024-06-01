#!/usr/bin/env python3

import fileinput
import csv
from io import StringIO

# BOSS_PLO_DEFAULT="PlayerGrid_PLO_DEF_BOSS.csv"
# IP_PLO_DEFAULT="PlayerGrid_PLO_DEF_IP.csv"
# BOSS_NL_DEFAULT="PlayerGrid_NL_DEF_BOSS.csv"
# IP_NL_DEFAULT="PlayerGrid_NL_DEF_IP.csv"

# BOSS_DEFAULT="Report_boss.csv"
# IP_DEFAULT="Report_ip.csv"
DEFAULT = "Report.csv"

NUM_COMPARE_PLAYERS = 20  # Number of players listed in each player entry
# 0 uses absolute values for adding up square error; 1 -> relativ differences (every stat is divided by the maximum value of all players)
ABSOLUTE_OR_RELATIV = 1
MIN_PLAYER_LINE_LENGTH = 10
DOT_LINE = "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"

# HM 2 seems to export first line with the stats description with faulty new lines
NUM_NEWLINES_TO_REPLACE = 19
# HM 3 correct again
NUM_NEWLINES_TO_REPLACE = 0

FAULTY_LINE_MAX_LENGTH = 80

DEFAULT_NICK_INDEX = 0
# 0        1        2        3        4        5        6        7        8          9        10        11        12        13        14        15        16        17        18        19        20       21      22        23      24        25      26       27        28
# player  site    hands      $       vpip     prf      3b       agg%     w$sf      wtsd     won@SD    F cbet    T cbet   R cbet   F vs Fcbet  Fvs Tcb   Fvs Rcb    Rvs Fcb   Rvs Tcb   RvsRcb    Squeeze  Rvs2R   CvsRs     Fvs3b   Cvs3b    Rvs3b    Fvs4b    Cvs4b     Rvs4b

# 0        1        2        3        4             5            6          7    8   9        10        11        12        13        14        15        16     17      18       19        20       21      22        23      24        25      26       27        28      29       30
# Player   site    hands  Net Won, Net bb Won, Net Won Hand,Net bb Won Hand,VPIP,PFR,3Bet,Postflop Agg,WWSF,WTSD,Won SD,Flop CBet,Turn CBet,River CBet,Fvs Fcb ,FvsTCBet,FRCBet,RvsFCBet,RvsTCBet,RvsRcb, Squeeze,Call2Raisers,R2Raisers,Fvs3Bet,Cvs3Bet,Raisevs3Bet,F24Bet,Cvs4Bet,Rvs4Bet
# HM 2
DEFAULT_INDEX_LIST = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28
]

# HM 3
DEFAULT_INDEX_LIST = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30
]

# HM 2
PRINT_INDEX_LIST = [
    0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17, 20, 22, 23, 25, 29
]
# HM 3
PRINT_INDEX_LIST = [
    0, 1, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 20, 23, 26, 28, 29, 31
]

DEFAULT_COMPARE_LIST = []
# HM2
SQR_STATS_LIST = [4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17, 20, 22, 23, 25]
# HM3
SQR_STATS_LIST = [7, 8, 9, 10, 11, 12, 14, 17, 23, 26]

ROUND_DECIMALS = 3


def replace_wrong_newlines_in_1st_line(
        filename, num=NUM_NEWLINES_TO_REPLACE
):  # bad / slow code for removing first x faulty newlines is line lenght < FAULTY_LINE_MAX_LENGTH
    with fileinput.FileInput(filename, inplace=True, backup=".bak") as csv:
        linecount = 0
        for line in csv:
            if linecount < num:
                if len(line) < 80:  # otherwise this was already done i guess
                    print(line.replace("\n", ""), end='')
                else:
                    print(line, end='')
            else:
                print(line, end='')
            linecount += 1
    return


def read_csv_file(filename):
    info_line = ""
    player_list = []
    players = ""
    with open(filename, "r") as csv:
        info_line = csv.readline()
        players = csv.read()
    player_list = players.split("\n")
    player_list = [
        player_line for player_line in player_list if len(player_line) > 10
    ]
    return (info_line, player_list)


def column_str(string, width=15):
    spaces = width - len(string)
    if spaces < 0:
        print("\n Choose bigger column width! \n")
        spaces = 0
    string_start = " " * (spaces + 1)
    return string_start + string + "|"


def output_line(item_list, print_index=PRINT_INDEX_LIST, column_width={}):
    line = ""
    for index in range(0, len(item_list)):
        if index in print_index:
            if column_width == {}:
                line += column_str(item_list[index])
            else:
                line += column_str(item_list[index], column_width[index] + 1)
    return line


def round_value(string):
    try:
        value = float(string)
        if value < 1 and value > 0:
            return "{0:.3f}".format(value)
        elif value < 100 and value > 0:
            return "{0:.1f}".format(value)
        else:
            return "{0:.0f}".format(value)
    except:
        return string


def print_player(info_line,
                 nick,
                 player_info,
                 match_list,
                 rank_dict,
                 num_players=NUM_COMPARE_PLAYERS,
                 index_list=PRINT_INDEX_LIST):
    column_width = {}
    # print(info_line)
    # print(nick)
    # print(player_info)
    # for item in match_list:
    #     print(item)

    full_info_line = info_line + ["Comp Val"]
    full_player_info = player_info + [""]
    full_match_list = [
        item + [str(rank_dict[item[DEFAULT_NICK_INDEX]])]
        for item in match_list
    ]

    full_info_line = [round_value(item) for item in full_info_line]
    full_player_info = [round_value(item) for item in full_player_info]
    for i in range(0, len(full_match_list)):
        for j in range(0, len(full_match_list[i])):
            full_match_list[i][j] = round_value(full_match_list[i][j])

    # print(full_info_line)
    # print(full_player_info)
    # for item in full_match_list:
    #     print(item)

    for i in index_list:
        if i >= len(full_info_line):
            continue
        column_width[i] = len(full_info_line[i])
        column_width[i] = len(full_player_info[i]) if len(
            full_player_info[i]) > column_width[i] else column_width[i]
        for line in full_match_list:
            column_width[i] = len(
                line[i]) if len(line[i]) > column_width[i] else column_width[i]

    print(DOT_LINE)
    print(output_line(full_info_line, index_list, column_width))
    print(DOT_LINE)
    full_player_info[0] = ">" + full_player_info[0]
    print(output_line(full_player_info, index_list, column_width))
    print(DOT_LINE)
    for i in range(0, num_players):
        print(output_line(full_match_list[i], index_list, column_width))
    print(DOT_LINE)
    print("")


def text2val(string):
    try:
        value = float(string)
    except:
        print(
            "WARNING: Could not convert {} to float value...asume na and set value to 0.5".
            format(string))
        value = 0.5
    return value


def sort_func(match_entry, player_entry, compare_list):
    value = 0
    for index in compare_list:
        value += abs(
            text2val(player_entry[index]) - text2val(match_entry[index]))
    return value


def sort_matches_rank(player_infos,
                      match_list,
                      compare_list=DEFAULT_COMPARE_LIST):

    match_nicks = {item[DEFAULT_NICK_INDEX]: []
                   for item in match_list}  # dic and list of values
    for compare in compare_list:
        sorted_match_list = sorted(
            match_list, key=lambda x: sort_func(x, player_infos, compare))
        for index in range(0, len(sorted_match_list)):
            match_nicks[sorted_match_list[index][DEFAULT_NICK_INDEX]].append(
                index)

    for key in match_nicks:
        match_nicks[key] = sum(match_nicks[key])

    return match_nicks


def sort_matches_square(player_infos, match_list, sqr_stats=SQR_STATS_LIST):
    match_nicks = {item[DEFAULT_NICK_INDEX]: []
                   for item in match_list}  # dic and list of square values
    max_values = {}
    for index in sqr_stats:
        max_values[index] = max([text2val(item[index]) for item in match_list])

    for match_entry in match_list:
        value = 0
        for index in sqr_stats:
            if ABSOLUTE_OR_RELATIV == 0:
                value += (text2val(player_infos[index]) - text2val(
                    match_entry[index]))**2  # std methode
            else:
                value += ((text2val(player_infos[index]) - text2val(
                    match_entry[index])) / max_values[index])**2  # normalise
        match_nicks[match_entry[DEFAULT_NICK_INDEX]] = round(
            value, ROUND_DECIMALS)
    return match_nicks


def process_lists(info_line_list, boss_plr_info_list, ip_plr_info_list):
    # ceate match dictionaries

    ip_player_matches = {}
    ip_player_infos = {}

    for player in ip_players:
        ip_player_matches[player] = boss_plr_info_list
        for player_infos in ip_plr_info_list:
            if player == player_infos[DEFAULT_NICK_INDEX]:
                ip_player_infos[player] = player_infos
                break

    # SORT BY CRITERIAS:

    ip_sort_dic = {}

    for player in ip_players:
        #        player_sort_dic=sort_matches_rank(ip_player_infos[player],ip_player_matches[player]) # sort by individual stats "rankings"
        player_sort_dic = sort_matches_square(
            ip_player_infos[player],
            ip_player_matches[player])  # sort by square differences
        ip_sort_dic[player] = player_sort_dic
        ip_player_matches[player] = sorted(
            ip_player_matches[player],
            key=lambda x: player_sort_dic[x[DEFAULT_NICK_INDEX]])

    # Print
    for nick in ip_players:
        print_player(info_line_list, nick, ip_player_infos[nick],
                     ip_player_matches[nick], ip_sort_dic[nick])


if __name__ == '__main__':

    # read files (when more stats read all files)

    # default_info_line,boss_default_plr_list=read_csv_file(BOSS_DEFAULT)
    # default_info_line,ip_default_plr_list=read_csv_file(IP_DEFAULT)

    # replace_wrong_newlines_in_1st_line(DEFAULT)

    default_info_line, boss_default_plr_list = read_csv_file(DEFAULT)
    default_info_line, ip_default_plr_list = read_csv_file(DEFAULT)

    boss_default_plr_list = [line[1:-1] for line in boss_default_plr_list]
    ip_default_plr_list = [line[1:-1] for line in ip_default_plr_list]

    boss_default_plr_list = boss_default_plr_list[:-2]
    ip_default_plr_list = ip_default_plr_list[:-2]

    ip_players = [
        player.split("\",\"")[DEFAULT_NICK_INDEX]
        for player in ip_default_plr_list
    ]
    boss_players = [
        player.split("\",\"")[DEFAULT_NICK_INDEX]
        for player in boss_default_plr_list
    ]

    # append only relevant entries and combine multiple reports

    ip_plr_info_list = []
    boss_plr_info_list = []

    info_line_list = []
    for i in range(0, len(default_info_line.split(","))):
        if i in DEFAULT_INDEX_LIST:
            info_line_list.append(default_info_line.split(",")[i])

    boss_plr_info_list = []
    for line_index in range(0, len(boss_default_plr_list)):
        default_line_split = boss_default_plr_list[line_index].split("\",\"")
        plr_list = []
        for i in range(0, len(default_line_split)):
            if i in DEFAULT_INDEX_LIST:
                plr_list.append(default_line_split[i])
        boss_plr_info_list.append(plr_list)

    ip_plr_info_list = []
    for line_index in range(0, len(ip_default_plr_list)):
        default_line_split = ip_default_plr_list[line_index].split("\",\"")
        plr_list = []
        for i in range(0, len(default_line_split)):
            if i in DEFAULT_INDEX_LIST:
                plr_list.append(default_line_split[i])
        ip_plr_info_list.append(plr_list)

    process_lists(info_line_list, boss_plr_info_list, ip_plr_info_list)
