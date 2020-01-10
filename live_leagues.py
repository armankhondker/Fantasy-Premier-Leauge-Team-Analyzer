
import requests, traceback, re, getpass
from collections import OrderedDict

'''
Live Leagues aims to fill the gap caused by FPL being slow to update leagues for millions of users.
This script provides real time league positions (net of transfers), before fpl officially updates tables.

NOTE/
The script is computationally intensive when running on leagues with hundreds of thousands of users, as such it will only output the first 200 entries of any league and users will be prompted to process more. 
'''

credentials = {'password': None,
               'login': 'armankhondker@gmail.com',
               'redirect_uri': 'https://fantasy.premierleague.com/a/login',
               'app': 'plfpl-web'
               }

team_id = 351353

#Only ask for validation if team_id, email and password havn't been set
if team_id == None or credentials['login'] == None:
    while True:
        print ("Enter team ID: ", end = '')
        team_id = input()
        try:
            int(team_id)
        except:
            print("Your game id is an all integer code")
            continue
        
        print ("Email: ", end = '')
        email = input()
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        if match == None:
            print('Bad email please re-enter')
            continue
        credentials['login'] = email

        print ("Password: ", end = '')
        credentials['password'] = getpass.getpass()
        break

#getpass method stops password echoing in terminal, menaing it remains hidden. 
else:
    print ("Password: ", end = '')
    credentials['password'] = getpass.getpass()

#Establish session
session = requests.session()
session.post('https://users.premierleague.com/accounts/login/', data=credentials)

#Entry section
entry_api = 'https://fantasy.premierleague.com/api/entry/%s/' % team_id
get_data_entry = session.get(entry_api).json()

#Bootstrap API
bootstrap_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
get_data_bootstrap = requests.get(bootstrap_url).json()

league_map = OrderedDict()
player_map = OrderedDict()

sp = ' '

print ("\n\nClassic Leagues:\n")
print('{0: >44}'.format('Prev'), '{0:>10}'.format('Curr'), '{0: >10}'.format('Rank'), '{0: >12}'.format('Leader'))
print("League Name", '{0:>32}'.format('Rank'), '{0: >10}'.format('Rank'), '{0: >10}'.format('Diff'), '{0: >13}'.format("Points\n"))

for i in range (len(get_data_entry['leagues']['classic'])):
    league_id = get_data_entry['leagues']['classic'][i]['id']
    league_name = get_data_entry['leagues']['classic'][i]['name']
    previous_rank = get_data_entry['leagues']['classic'][i]['entry_last_rank']
    current_rank = get_data_entry['leagues']['classic'][i]["entry_rank"]
    rank_difference = previous_rank - current_rank

    league_api = 'https://fantasy.premierleague.com/api/leagues-classic/%s/standings/' % league_id
    get_data_league = session.get(league_api).json()

    league_leader = get_data_league['standings']['results'][0]['total']
    league_difference = league_leader - get_data_entry['summary_overall_points']

    #Create league hashmap. Value is a tuple of name and league id. 
    league_map[i] = (league_name, league_id)

    print ("(%d) %-35s %-10d %-10d %-10d %d (%d)" % (i, league_name, previous_rank, current_rank,
        rank_difference, league_leader, league_difference))


def process_league(ID):

    #Orderd dict for sorting efficiency
    user_map = OrderedDict()
    page_num = 1
    limit_page = 4

    league_api = 'https://fantasy.premierleague.com/api/leagues-classic/%s/standings/?page_new_entries=1&page_standings=%s&phase=1' % ( league_map[ID][1], page_num)
    get_data_league = session.get(league_api).json()
    gameweek = get_data_entry["current_event"]
    
    while True:
        for i in range(len(get_data_league["standings"]["results"])):
            team_id = get_data_league["standings"]["results"][i]["entry"]
            #User id
            user_id = (get_data_league["standings"]["results"][i]["entry_name"] + ' - ' + get_data_league["standings"]["results"][i]["player_name"])
            #gw_Team API
            gw_team_api = 'https://fantasy.premierleague.com/api/entry/%s/event/%s/picks/' % (team_id, gameweek)
            get_gw_team = session.get(gw_team_api).json()
            #get old gw points - costly try and find improvement in future
            gw_team_old_api = 'https://fantasy.premierleague.com/api/entry/%s/event/%s/picks/' % (team_id, gameweek - 1 if gameweek > 0 else gameweek)
            get_gw_old_team = session.get(gw_team_old_api).json()

            speed_gw_points = 0
            #Captain points(already doubled), Name, triple (boolean)
            captain_id_name = [None, None, False]

            for pl in range(len(get_gw_team['picks'])):
                id = get_gw_team['picks'][pl]['element']
                multi = get_gw_team['picks'][pl]['multiplier']

                if multi > 0 and id in player_map:
                    gw_points = player_map[id][0]
                    if multi == 2:
                        #Mark as captain
                        gw_points *= 2
                        captain_id_name[0], captain_id_name[1] = gw_points, player_map[id][1]
                    elif multi == 3:
                        #Mark as Tripple captain
                        gw_points *= 3
                        captain_id_name[0], captain_id_name[1], captain_id_name[2] = gw_points, player_map[id][1], True

                    speed_gw_points += gw_points
        
                elif multi > 0:
                    for j in range(len(get_data_bootstrap['elements'])):
                        if get_data_bootstrap['elements'][j]['id'] == id:
                            gw_points = get_data_bootstrap['elements'][j]['event_points']
                            player_map[id] = (gw_points, get_data_bootstrap['elements'][j]['web_name'])
                            if multi == 2:
                                #Mark as captain
                                gw_points *= 2
                                captain_id_name[0], captain_id_name[1] = gw_points, player_map[id][1]
                            elif multi == 3:
                                #Mark as Triple captain
                                gw_points *= 3
                                captain_id_name[0], captain_id_name[1], captain_id_name[2] = gw_points, player_map[id][1], True

                            speed_gw_points += gw_points
                            break
                
                #Captain didn't play, was substituted and Vice didn't play.
                elif get_gw_team['picks'][pl]['is_captain'] and captain_id_name[0] == None:
                    if id in player_map:
                        captain_id_name[0], captain_id_name[1] = 0, player_map[id][1]
                    #Player is not in player map. Need to find in bootstrap. 
                    else:
                        for j in range(len(get_data_bootstrap['elements'])):
                            if get_data_bootstrap['elements'][j]['id'] == id:
                                player_map[id] = (0, get_data_bootstrap['elements'][j]['web_name'])
                                break
                        captain_id_name[0], captain_id_name[1] = 0, player_map[id][1]
                        
            #Have Team name + person name of as key. Value is a tuple:
            #(gw-1 points + gw points - hits, gw points - hits, previous rank, hits)
            user_map[user_id] = (speed_gw_points + get_gw_old_team["entry_history"]["total_points"] - get_gw_team["entry_history"]["event_transfers_cost"], speed_gw_points - get_gw_team["entry_history"]["event_transfers_cost"], get_data_league["standings"]["results"][i]["rank"], -get_gw_team["entry_history"]["event_transfers_cost"], captain_id_name) 


        #Only print first 200 entries. Then ask if wnat to keep going 
        if page_num == limit_page or len(get_data_league['standings']['results']) == 0:
            #Ask if keep going, as there exsits a next page.
            if len(get_data_league['standings']['results']) != 0 and page_num == limit_page:
                print('\nEnter any key to process another 200 players; or enter -1 to see output: ')
                try:
                    temp = int(input())
                    if temp == -1:
                        break
                    else:
                        page_num += 1
                        limit_page += 4
                        league_api = 'https://fantasy.premierleague.com/api/leagues-classic/%s/standings/?page_new_entries=1&page_standings=%s&phase=1' % (league_map[ID][1], page_num)
                        get_data_league = session.get(league_api).json()
                        
                except:
                    page_num += 1
                    limit_page += 4
                    league_api = 'https://fantasy.premierleague.com/api/leagues-classic/%s/standings/?page_new_entries=1&page_standings=%s&phase=1' % (league_map[ID][1], page_num)
                    get_data_league = session.get(league_api).json()
                    
            else:
                break

        else:
            page_num += 1
            league_api = 'https://fantasy.premierleague.com/api/leagues-classic/%s/standings/?page_new_entries=1&page_standings=%s&phase=1' % (league_map[ID][1], page_num)
            get_data_league = session.get(league_api).json()
            

    #Perform sorting: Use selection sort as stable and exploit psuedo ordered property of league table. Faster than python nlogn library quicksort.
    user_list = list(user_map.items())
    for k in range(1, len(user_list)):
        key = user_list[k]
        w = k - 1
        while w >= 0 and key[1][0] > user_list[w][1][0]: 
            user_list[w + 1] = user_list[w]
            w -= 1
        user_list[w + 1] = key


    print()
    print('{0: >49}'.format('Curr'), '{0:>9}'.format('Prev'), '{0: >9}'.format('Rank'), '{0: >43}'.format('Net'))
    print('{0: <41}'.format('Name'), '{0:>7}'.format('Rank'), '{0: >9}'.format('Rank'), '{0: >9}'.format('Diff'), '{0: >11}'.format('Captain'), '{0: >24}'.format('Hits'), '{0: >10}'.format("Points\n"))

    for i in range(len(user_list)):
        print ("%-44s %-9d %-9d %-8d %-27s %-7d %d (%d)" % (user_list[i][0], i + 1, user_list[i][1][2], user_list[i][1][2] - (i + 1), ((user_list[i][1][4][1] +' ('+str(user_list[i][1][4][0]) +')' + '(TC)') if user_list[i][1][4][2] else user_list[i][1][4][1] +' ('+str(user_list[i][1][4][0]) +')'), user_list[i][1][3], user_list[i][1][0], user_list[i][1][1]))

    
while True:
    print("\nEnter the ID (left of name) of the league you want live standings or -1 to exit:")
    try:
        ID = int(input())
        if ID == -1: 
            break
        elif ID not in league_map:
            continue
        else:
            process_league(ID)
            print()
    except:
        continue



