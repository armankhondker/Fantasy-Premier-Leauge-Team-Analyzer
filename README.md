# Fantasy Premier Leauge Team Analyzer and Visualizer

A collection of tools for [/r/FantasyPL](https://www.reddit.com/r/FantasyPL/) to help FPL Managers rise to the top of the FPL ranks! Created and developed with Python!
Join over 7,000,000 managers playing the #1 fantasy sports game in the world at: https://www.fantasy.premierleauge.com 

These FPL python script provides FPL managers with a command line interface to seamlessly:
1. **Check their gameweek scores** and league ranks
2. **Check live league positions** and table rankings (Used to help with @OfficialFPL being slow to update millions of leagues during gameweeks and help fill in the gap for enthusiastic FPL mangers)
3. **Plan for future gameweeks** by analyzing current team selections, captaincy choice, transfers made, and chips available


## Gameweek Checker

The Gameweek Checker script helps FPL managers by allowing them to follow their team's progress during the current gameweek. The Gameweek Checker Script will correctly display real time points, prices changes, and classic and head-to-head league ranks. 

## Live League Rank

The Live League Rank script helps FPL managers by providing real time league positions and changes in ranking. Additionally, the Live League Rank scrript provides every player's captaincy choice, transfer hits, and net points. The Live League Rank script lets you dive deeper into details of a specific league. 

## Team Analyzer

The Team Analyzer script helps FPL mangagers by allowing them to plan for future gameweeks. Furthermore, the team analyzer script will display the current gameweek team selections, transfers made, free transfers reamining, team value, and chips available. 

## Technolgies Used

* Python
* Fantasy Premier League Official API 

# Helpul Tips

Users are required to know their **unique fpl entry id** to use this project. The id can be retreived on the fpl site by clicking "my team", "view gameweek history", and looking at the url.
Example: https://fantasy.premierleague.com/entry/{team-id}/history

These scripts assume you have Python 3 and the requests package installed. Users can install this package by running:
```pip install requests``` on MacOS


