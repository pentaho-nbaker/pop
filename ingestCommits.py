import os

__author__ = 'nbaker'

from git import Repo
from BranchDiffAnalyzer import BranchDiffAnalyzer
from lxml import html
import requests
import tempfile
import shutil

stable = "origin/master"
active = "origin/future-develop"
analyzers = [BranchDiffAnalyzer()]
if __name__ == '__main__':


    repos_dir = tempfile.mkdtemp()
    print repos_dir
    page = requests.get('http://10.100.8.139/newbackups/pentaho/latest/')
    directory = html.fromstring(page.text)
    anchors = directory.xpath('//a')
    anchors = [a.attrib["href"][0:-1] for a in anchors if a.attrib["href"].find(".git") > -1]
    names = [a[:-4] for a in anchors]
    for index, anchor in enumerate(anchors):
        print anchor
        name = names[index]
        repo = Repo.clone_from("http://10.100.8.139/newbackups/pentaho/latest/%s" % anchor, os.path.join(repos_dir, name))

            # repo = Repo("/Users/nbaker/IdeaProjects/Platform/" )
        for x in analyzers:
            x.analyze(name, repo, stable, active)

    shutil.rmtree(repos_dir)
