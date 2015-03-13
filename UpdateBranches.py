#!/usr/bin/env python
__author__ = 'nbaker'
import requests
import json
if __name__ == '__main__':
    unmerged_pulls = []
    errored_pulls = []
    headers = {'content-type': 'application/json',
               "Content-Type": "application/json",
                "Accept": "application/json"}
    params = {'per_page':1000}
    repos_request = requests.get('https://api.github.com/orgs/pentaho/repos', auth=('buildguy', 'S6ddxtky'), headers=headers)

    repos = repos_request.json()
    urls = [rep["url"] for rep in repos]
    for url in urls:
        print "processing: "+url

        params = {
            "title": "Auto-Merge refreshing development branch",
            "body": "Merge of master into future-develop",
            "head": "master",
            "base": "future-develop"
        }
        url = url + "/pulls"
        response = requests.post(url, auth=('buildguy', 'S6ddxtky'),
                                 data=json.dumps(params))

        print response.text
        pull = response.json()
        if "errors" in pull:
            errored_pulls.append( url + str(pull["errors"]) )
        else:

            commit_message = {"commit_message" : "Auto Merge of master into future-develop"}
            pull_url = pull["url"] + "/merge"
            response = requests.put(pull_url, auth=('buildguy', 'S6ddxtky'), data=json.dumps(params))
            print response.text
            merge_result = response.json()
            if "merged" not in merge_result or merge_result["merged"] is False:
                print "not mergable or merge failed: "+pull_url
                unmerged_pulls.append(pull_url)

    print "\n\nerrored:"
    for errored in errored_pulls: print errored

    print "\n\nUnmerged:"
    for unmerged in unmerged_pulls: print unmerged