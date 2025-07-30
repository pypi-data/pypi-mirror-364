#!/bin/python/env
# -*- coding: utf-8 -*-

import json

from gamechanger_client import GameChangerClient


def main():
    gamechanger = GameChangerClient()

    teams = gamechanger.me.teams()

    # Allow user to select a team
    i = 1
    print('Select a team:')
    for team in teams:
        print(f"[{i}] {team['name']}")
        i += 1
    team_index = int(input('Which team? '))
    team_id = teams[team_index - 1]['id']
    team_name = teams[team_index - 1]['name']
    team_public_id = teams[team_index - 1]['public_id']

    important_stats = ['GP', 'PA', 'AB', 'AVG', 'OBP', 'OPS', 'SLG', 'H', '1B', '2B', '3B', 'HR', 'RBI', 'R', 'BB', 'SO', 'HBP', 'QAB', 'QAB%', 'PA/BB', 'BB/K', 'C%', 'HARD', 'BA/RISP']
    player_stats = []

    players = gamechanger.teams.public_players(team_public_id)
    season_stats = gamechanger.teams.season_stats(team_id)

    for player in players:
        player_name = f'{player['first_name']} {player['last_name']} (#{player['number']})'

        stats = season_stats['stats_data']['players'].get(player['id'], {}).get('stats', {}).get('offense', {})
        stat_line = [player_name]

        if stats:
            for stat in important_stats:
                try:
                    stat_line.append(round(stats[stat], 3))
                except:
                    stat_line.append('?')

        player_stats.append(stat_line)

    with open(f'{team_name}_hitting.csv', 'a') as team_stats:
        team_stats.write(f'Name,{','.join(important_stats)}\n')
        for stat_line in player_stats:
            team_stats.write(f'{','.join(map(str, stat_line))}\n')


if __name__ == '__main__':
    main()
