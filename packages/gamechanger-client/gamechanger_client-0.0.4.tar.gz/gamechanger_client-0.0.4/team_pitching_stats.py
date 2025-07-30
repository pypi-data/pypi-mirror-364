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

    important_stats = ['IP', 'ERA', 'WHIP', 'BF', 'P/BF', 'P/IP', 'H', '2B', '3B', 'HR', 'SO', 'BB', 'HBP', 'BAA', 'S%']
    player_stats = []

    players = gamechanger.teams.public_players(team_public_id)
    season_stats = gamechanger.teams.season_stats(team_id)

    for player in players:
        stat_line = f'{player['first_name']} {player['last_name']} (#{player['number']})'

        stats = season_stats['stats_data']['players'].get(player['id'], {}).get('stats', {}).get('defense', {})

        if stats:
            for stat in important_stats:
                try:
                    stat_line += f',{round(stats[stat], 3)}'
                except:
                    continue

            player_stats.append(stat_line)

    with open(f'{team_name}_pitching.csv', 'a') as team_stats:
        team_stats.write(f'Name,{','.join(important_stats)}\n')
        for stat_line in player_stats:
            team_stats.write(f'{stat_line}\n')


if __name__ == '__main__':
    main()
