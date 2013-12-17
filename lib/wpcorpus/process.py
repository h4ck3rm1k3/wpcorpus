#
# This file is part of wpcorpus
#
# Copyright (c) 2013 by Pavlo Baron (pb at pbit dot org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
logging.getLogger('pika').setLevel(logging.DEBUG)

from wpcorpus.pages import extract_text
import os
import re
import glob
import gc
import sys
from wpcorpus.rabbit import Publisher
from wpcorpus.props import Props
import pickle

from wpcorpus.config import BASE_PATH

TMPF = "/tmp/wiki"


def worker(filename, nr):
    # filename is an xml file
    import wpcorpus.process

    outfilename = "%s/corpus/text/%s.txt" % (BASE_PATH, nr)
    print (outfilename)
    f = open(outfilename, "a")
    pos = f.tell()

    p = Props()
    p.backpressure = 100
    p.exchange = "wikiindex"
    queue = Publisher(p)
    queue.start(p.exchange)

    # 
    for cat, _title, text in extract_text(filename):
        t = text.encode("ascii", "ignore")
        l = len(t)
        queue.publish(pickle.dumps((cat, outfilename, pos, l)))
        f.write(t)
        pos += l

    queue.publish(pickle.dumps("flush"))
    f.close()
    queue.close()

def report_done(nr):
    f = open("%s%s.d" % (TMPF, nr), "w")
    f.write("1")
    f.close()

def main():
    if len(sys.argv) > 1 :
        filename = sys.argv[1]
        nr = sys.argv[2]
    else:
        print ("expecting args: filename nr")
        return 

#    filename = "%s/lib/wpcorpus/%s" % (BASE_PATH, filename)
    print (filename)
    worker(filename, nr)

    report_done(nr)

if __name__ == '__main__':
    main()
