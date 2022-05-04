#!/usr/bin/env python3 -B
# -*- coding: utf8 -*-
#eval 'exec python -B $0 ${1+"$@"}'

''' Class for uvm user interface

uvm_user_if.py 
Version 0.1.0

'''

import argparse
import re

class uvm_user_if():

  def __init__(self,fname=__file__):

    """ uvm_user_if.py __main__ """
    thisFile = re.match(r'(.*/)?(?P<name>.*)', fname)
    name = thisFile.group('name')
    self.db = {}
    print ("\n")
    ###################
    # parse arguments #
    ###################
    #usage: Run UVM FrameWork Generator
    #
    #uvm_main.py -a | -all (generate all)
    #
    #optional arguments:
    #  -h, --help            show this help message and exit
    #
    #  -v {debug,info,warning,error,critical}, --verbose {debug,info,warning,error,critical}
    #                        overwite the default verbose level 'info'
    #
    #  -c <file.tpl>, --common <file.tpl>
    #                        common template for top-level testbench
    #
    #  -a [<file.tpl> [<file.tpl> ...]], --agent [<file.tpl> [<file.tpl> ...]]
    #                        list of agent templates
    #
    #  --all                  create all files ifnot exists
    #
    #  --setup                use the file entity_desc.txt and generate a set of tpl-files
    #


    parser = argparse.ArgumentParser(
            usage = 'Run UVM FrameWork Generator\n',
            description= 'Default call: {0} <tpl-list> -all (generate templates)\n'.format(name),
            epilog='version: %s svn %s \n\n' % (
                '$Date: 2020-11-20 11:05:00 +0100 $'[7:32],
                '$Revision: 0 $'[11:-2]
                ),
            formatter_class=argparse.RawDescriptionHelpFormatter
            )

    tpl = parser.add_argument_group()

    tpl.add_argument('agent',
            type=str,
            metavar='<file.tpl>',
            action='store',
            nargs='*',
            help='list of agents templates',
        )

    tpl.add_argument('-c','--common',
            metavar='<common.tpl>',
            action='store',
            default='common.tpl',
            help='common template for top-level testbench',
        )

#    tpl.add_argument('-a','--agent',
#            metavar='<file.tpl>',
#            action='store',
#            nargs='*',
#            help='list of agent templates',
#        )

    tpl.add_argument('-a','--all',
            action='store_true',
            default=False,
            help='create all files if not exists',
        )

    tpl.add_argument('-i','--inline',
            action='store_true',
            default=False,
            help='copy content of inlined file into destination file',
        )

    tpl.add_argument('-o','--overwrite',
            action='store_true',
            default=False,
            help='overwrite of sim/* files',
        )

    tpl.add_argument('-j','--json',
            action='store_true',
            default=False,
            help='print the database files gen_uvm.json',
        )

    tpl.add_argument('--gencom',
            metavar='<common.tpl>',
            action='store',
            default=False,
            help='Write a mycommon.tpl file !!',
        )

    tpl.add_argument('--gentpl',
            metavar='<agent.tpl>',
            action='store',
            default=False,
            help='Write <agent>.tpl !!\n"',
        )
        
    tpl.add_argument('--setup',
            action='store_true',
            default=False,
            help='Read entity_desc.txt and write a set of tpl files !!\n"',
        )


##    verbose = parser.add_argument_group()
    tpl.add_argument('-v','--verbose',
            action='store',
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            default='info',
            help="overwite the default verbose level 'info'",
          )

    self.args = parser.parse_args()
    self.db = vars(self.args)
    fname = re.sub(r'\\', '/', fname)
    self.db['scriptdir'] = fname

    #print (self.args);exit()

if __name__ == '__main__':

    args = uvm_user_if().args
    if (args.agent) :
        print ("Agents:   %s"%args.agent)
    if (args.common) :
        print ("Top-TB:   %s"%args.common)
    if (args.all) :
        print ("CreatAll: %s"%args.all)
    print(args)



