from util.string_util import StringUtil
import os
import json
import requests
import logging

class BlueAllianceAPI():
    def __init__(self, auth_key):
        self.auth_key = auth_key

    def _fetch(self, path):
        url = 'https://www.thebluealliance.com/api/v3' + path
        headers = {'X-TBA-Auth-Key': self.auth_key}
        r = requests.get(url, headers=headers)
        if r.status_code >= 400:
            raise Exception(r)
        data = r.json()
        return data

    def get_data(self, path):
        logging.info("Getting data: " + path)
        # 1) Make a key for the path:
        key = StringUtil.hash_string(path)
        logging.debug("Key: " + key)
        # 2) Make a filename from the key:
        filename = key + ".json"
        # 3) Make a filepath from the filename:
        filepath = os.path.join("data", "network", filename)
        if os.path.isfile(filepath):
            logging.info("Using cache")
            # Return the data from the file:
            with open(filepath) as f:
                data = json.load(f)
            return data
        else:
            logging.info("Fetching raw")
            # Fetch
            data = self._fetch(path)
            with open(filepath, 'w') as outfile:  
                json.dump(data, outfile)
            return data
