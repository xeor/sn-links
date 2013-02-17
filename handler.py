#!/usr/bin/env python

'''
This is a simple little script that tries to grab every urls from all the SecurityNow episodes and display them in a simple list.
The reason for its existence is for all us people listening but who are not getting an option to write down the links.
It uses the transcript provided from http://www.grc.com/sn/sn-123.txt where 123 is the epoisode number.

This script works without any database, just a dump of text files.
'''

import time
import urllib2
import os
import re
import glob

MYDIR = os.path.abspath(os.path.dirname(__file__))


class SN(object):
    txt_url = 'http://www.grc.com/sn/sn-%.3d.txt'
    dump_folder = '%s/sn-txt' % MYDIR
    markup = ''  # We will store all our markup here..

    def dumper(self):
        # Find the last episode number we have, and make the next one our start
        try:
            num = int(re.findall(r'[0-9]+', sorted(glob.glob('%s/sn-*.txt' % self.dump_folder))[-1])[0]) + 1
        except IndexError:
            # Probably empty folder, start at 1
            num = 1

        while True:
            file_path = '%s/sn-%.3d.txt' % (self.dump_folder, num)
            cur_url = self.txt_url % num

            if os.path.isfile(file_path):
                num += 1
                continue

            print 'Trying to grab', cur_url

            try:
                text = urllib2.urlopen(cur_url).read()
            except urllib2.HTTPError:
                print 'HTTP error, aborting, probably 404, means we are at the last episode.'
                # Hopefully a 404 :)
                break

            with open(file_path, 'w') as fp:
                print 'Writing episode to %s' % file_path
                fp.write(text)
            time.sleep(1)
            num += 1

    def _get_links(self, raw_txt, episode_num):
        all_links = []

        all_links += re.findall(r'bit.ly/[a-zA-Z0-9-]+', raw_txt)
        all_links += re.findall(r'[a-zA-Z0-9-]{3,30}\.[a-zA-Z]{2,5}/[^ \n\r]+', raw_txt)

        final_list = []
        for link in all_links:
            # Lowercase domain names

            parts = link.split('/')
            parts[0] = parts[0].lower()
            link = '/'.join(parts)

            link = re.sub(r'[\.,]+$', '', link)  # Take away ending . or ,
            link = re.sub(r'[\[\]]', '', link)   # Take away [, ] characters, which are some times put around the links in the text
            if link in [
                'creativecommons.org/licenses/by-nc-sa/2.5/', 'grc.com/securitynow.htm', 'grc.com/feedback', 'twit.tv/sn',
                'grc.com/sn/SN-%s.mp3' % str(episode_num), 'grc.com/sn', 'grc.com/sn/feedback', 'twitter.com/SGgrc',

                ]:
                # Some links are too generic, skip them..
                continue
            final_list.append(link)
        return list(set(final_list))

    def _create_list(self, episode_num, links):
        if not links:
            return None

        cur_episode_markup = '### Episode %s\n\n' % str(episode_num)

        links = ['* [%s](http://%s)' % (l, l) for l in links]
        cur_episode_markup += '\n'.join(links)

        self.markup += '%s\n\n' % cur_episode_markup

    def write_markdown(self):
        links_md = '%s/links.md' % MYDIR
        gen_info = '## SecurityNow links (newest on top)\n\n'

        with open(links_md, 'w') as fp:
            print 'writing to', links_md
            fp.write(gen_info + self.markup)

    def handler(self):
        # Loop trough what we got in a reversed sorted by number fashion. (number are part of filename, so little hackish)
        for txt in sorted(glob.glob('%s/sn-*.txt' % self.dump_folder), reverse=True, key=lambda x: int(re.sub(r'[^0-9]', '', x))):
            episode_num = re.findall(r'[0-9]+', txt.split('/')[-1])[0]
            with open(txt, 'r') as fp:
                raw_txt = fp.read()
                links = self._get_links(raw_txt, episode_num)
                self._create_list(episode_num, links)

if __name__ == '__main__':
    sn = SN()
    sn.dumper()
    sn.handler()
    sn.write_markdown()
