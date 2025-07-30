#!/bin/python/env
# -*- coding: utf-8 -*-

import json

from gamechanger_client import GameChangerClient


def main():
    team_id = '4ee72085-d55f-4976-a30b-1bfe03e32979'
    
    gamechanger = GameChangerClient()
    # gamechanger.teams.create_player(team_id='4ee72085-d55f-4976-a30b-1bfe03e32979', first_name='alan', last_name='nix jr', number='32', batting_side='right', throwing_hand='right')
    schedule = gamechanger.teams.schedule(team_id)
    print(json.dumps(schedule, indent=2))

    for event in schedule:
        gamechanger.teams.delete_event(team_id, event['event']['id'])

    players = gamechanger.teams.players(team_id)
    print(json.dumps(players, indent=2))

    for player in players:
        gamechanger.players.delete(player['id'])
    exit()



    gamechanger.teams.create_event(
        team_id='4ee72085-d55f-4976-a30b-1bfe03e32979',
        event_type='other',
        title='Test 2',
        start_time='2025-05-16T13:00:00-04:00',
        end_time='2025-05-16T14:00:00-04:00',
        arrive_time='2025-05-16T13:00:00-04:00',
        location='TBD',
        status='scheduled'
    )
    # gamechanger.teams.delete('4ee72085-d55f-4976-a30b-1bfe03e32979')

if __name__ == '__main__':
    main()
