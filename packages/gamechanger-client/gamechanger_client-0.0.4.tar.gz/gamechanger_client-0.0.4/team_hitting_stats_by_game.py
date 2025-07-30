#!/bin/python/env
# -*- coding: utf-8 -*-

import json

from datetime import datetime

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

    # Get the team's schedule and filter by games with a start time
    schedule = gamechanger.teams.schedule(team_id)
    game_schedule = list(filter(lambda x: (x['event']['event_type'] == 'game'
                                           and x['event']['status'] == 'scheduled'
                                           and 'datetime' in x['event']['start'].keys()), schedule))
    i = 1
    print('\nSelect a game:')
    for game in game_schedule:
        game_date = datetime.fromisoformat(game['event']['start']['datetime'][:-1] + '+00:00')
        game_date = game_date.astimezone(tz=None).strftime('%Y-%m-%d %I:%M%p')
        print(f"[{i}] {game_date} {game['event']['title']}")
        i += 1
    event_index = int(input('Which game? '))
    event_id = game_schedule[event_index - 1]['event']['id']

    game_stats = gamechanger.teams.event_player_stats(team_id, event_id)

    for player in players:
        player_name = f'{player['first_name']} {player['last_name']} (#{player['number']})'

        stats = game_stats['player_stats']['players'].get(player['id'], {}).get('stats', {}).get('offense', {})
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
