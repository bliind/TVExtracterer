#!/usr/bin/env python
import re, sys, subprocess
from glob import glob

class TVExtracterer(object):
    def __init__(self):
        self.destDir = '/TV'

        self.logfile = '{}/newLog'.format(self.destDir)
        with open(self.logfile, 'r+') as stream:
            self.log = stream.read()

    def writeLog(self, directory):
        self.log += '\n{}'.format(directory)
        with open(self.logfile, 'w') as stream:
            stream.write(self.log)

    def cleanDirName(self, directory):
        # remove traiing slash
        if directory.endswith('/'):
            directory = directory[:-1]
        
        # get the directory name without path
        dirname = directory.split('/')[-1]

        return dirname

    def parseTitleAndEpisode(self, directory):
        # regex match the title and episode number
        match = re.match(r'(.+)([sS][0-9]{2}[eE][0-9]{2})', directory)
        if match and match.groups():
            title = match.groups()[0].replace('.', ' ').strip()
            title = self.checkTitle(title)
            ep = match.groups()[1]

            return (title, ep)

    def checkTitle(self, title):
        titles = {
            "Marvels Agents of S H I E L D": "Marvel's Agents of S.H.I.E.L.D.",
            "The Flash 2014": "The Flash (2014)",
            "DCs Legends of Tomorrow": "DC's Legends of Tomorrow"
        }

        try: return titles[title]
        except: return title

    def handleFiles(self, directory, destination):
        rarfile = glob('{}/*.rar'.format(directory))
        try:
            # try to unrar the file to its destination
            subprocess.check_output(['/usr/bin/unrar', 'e',rarfile[0], destination])
            return True
        except: pass

        vidTypes = ['mkv', 'avi', 'mp4']
        for vidType in vidTypes:
            vidfile = glob('{}/*.{}'.format(directory, vidType))
            try:
                # try to rsync the file to its destination
                subprocess.check_output(['/usr/bin/rsync', '-a', vidfile[0], destination])
                return True
            except: pass

    def loop(self, dirs):
        for directory in dirs:
            dirname = self.cleanDirName(directory)

            # check the log file for the dirname
            if dirname in self.log:
                continue

            # try to get title and series number or skip
            try:
                title, ep = self.parseTitleAndEpisode(dirname)
            except TypeError:
                print('Not processing {}'.format(dirname))
                self.writeLog(dirname)
                continue

            season = int(float(ep[1:3]))
            dest = '{}/{}/Season {}/'.format(self.destDir, title, season)

            # if files were extracted/moved successfully, write dirname to log
            print('Processing {}...'.format(dirname))
            print('  Destination: {}'.format(dest))
            if self.handleFiles(directory, dest):
                self.writeLog(dirname)

if __name__ == '__main__':
    e = TVExtracterer()

    # make a list of directories from the args
    dirs = list(sys.argv[1:])

    # kick off the loop
    e.loop(dirs)
