import configparser
import csv
import logging

from net.ba_api import BlueAllianceAPI

def main():
    logging.basicConfig(level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read('config/ba_secret.ini')
    auth_key = config['blue_alliance']['auth_key']
    api = BlueAllianceAPI(auth_key)

    # 1) Get the list of all events:
    all_events_list = []
    events_raw = api.get_data("/events/2019/simple")
    for event_raw in events_raw:
        all_events_list.append(event_raw["key"])
    logging.info("Number of events: {}".format(len(all_events_list)))

    all_data = {}
    # 2) Iterate over the events:
    event = all_events_list[0]
    for event in all_events_list:
        # Short circuit for testing:
        #if event != "2019mimid":
        #    continue
        # 2a) Fetch raw stats:
        statuses = api.get_data("/event/{}/teams/statuses".format(event))
        if statuses is None or len(statuses.keys()) == 0:
            logging.warn("No data for {}".format(event))
            continue
        # 2b) Add the raw stats to our data:
        teams = statuses.keys()
        logging.info("Found {} teams for {} statuses".format(len(teams), event))
        for team in teams:
            # Big test to make sure we have a ranking.
            if statuses[team] == None or statuses[team]["qual"] == None or statuses[team]["qual"]["ranking"] == None or statuses[team]["qual"]["ranking"]["rank"] == None:
                continue
            ad_key = "{}.{}".format(team, event)
            if ad_key in all_data:
                logging.warn("{} is already in the hash. May be duplicate or error...".format(ad_key))
            all_data[ad_key] = {}
            all_data[ad_key]["team"] = team
            all_data[ad_key]["event"] = event
            all_data[ad_key]["rank"] = statuses[team]["qual"]["ranking"]["rank"]
            #Ranking score, Cargo, Hatch Panel, HAB Climb, Sandstorm Bonus
            all_data[ad_key]["ranking_score"] = statuses[team]["qual"]["ranking"]["sort_orders"][0]
            all_data[ad_key]["cargo"] = statuses[team]["qual"]["ranking"]["sort_orders"][1]
            all_data[ad_key]["hatch"] = statuses[team]["qual"]["ranking"]["sort_orders"][2]
            all_data[ad_key]["hab"] = statuses[team]["qual"]["ranking"]["sort_orders"][3]
            all_data[ad_key]["sandstorm"] = statuses[team]["qual"]["ranking"]["sort_orders"][4]
        # 2c) Fetch oprs:
        oprs = api.get_data("/event/{}/oprs".format(event))
        if oprs is None or len(oprs.keys()) == 0:
            logging.warn("No data for {}".format(event))
            continue
        teams = oprs["ccwms"].keys()
        logging.info("Found {} teams for {} oprs".format(len(teams), event))
        for team in teams:
            ad_key = "{}.{}".format(team, event)
            if ad_key not in all_data:
                logging.warn("{} is not in the hash. May be duplicate or error...".format(ad_key))
                continue
            all_data[ad_key]["ccwms"] = oprs["ccwms"][team]
            all_data[ad_key]["dprs"] = oprs["dprs"][team]
            all_data[ad_key]["oprs"] = oprs["oprs"][team]

    # For turning array of hashes into CSV:
    # https://stackoverflow.com/a/3087011/978509
    #print(all_data)
    first = next(iter(all_data))
    keys = all_data[first].keys()
    with open('data/world_2019_04_19.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_data.values())

if __name__ == "__main__":
    main()
