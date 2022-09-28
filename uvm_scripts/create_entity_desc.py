#!/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2022 Helmut Steinbach

import os, os.path
import sys
import io
import re


''' Class for user interface

user_if.py 

'''

import argparse
import re

class user_if():

  def __init__(self,script=__file__):

    ''' user_if.py __main__ '''
    name = os.path.basename(script)
    
    parser = argparse.ArgumentParser(
            usage = '\n'.join(['',' Run a template generator for entity_desc file.',
                              ' Takes a HDL file and check the file extension on vhd,vhdl or v,sv,vlog.',
                              ' The file type can be given for all other file extensions.',
                              f' To check if file is ok call: {name} -n -i [-f <file>] ',
                              ]) ,
            description= ' Default call: {0} --file <vhdl-file>\n'.format(name)+
            ' The script generate: ./entity_desc.txt.gen\n',

            epilog=' version: %s' % (
                '$Date: 2022-09-28 00:00:00 '[7:18],
                ),
            formatter_class= argparse.RawDescriptionHelpFormatter
            )
    tpl = parser.add_argument_group()

    tpl.add_argument('-f','--file',
            type=str,
            metavar='<hdl_file>',
            action='store',
            #nargs='*',
            help='file with entity/module description',
        )
    
    tpl.add_argument('--vlog',
            action='store_true',
            help='overwrite file type for Verilog',
        )

    tpl.add_argument('--vhdl',
            action='store_true',
            help='overwrite file type for VHDL',
        )
        
    tpl.add_argument('-i','--info',
            action='store_true',
            help='print database info',
        )

    tpl.add_argument('-n','--no_create',
            action='store_true',
            help='suppress generation of entity_desc-files',
        )


    self.args = parser.parse_args()
    args = vars(self.args)
    args['name'] = name
    args['script'] = script
    args['parser'] = parser
    
    #print(args);exit()
    
if __name__ == '__main__':

  import entity_desc 

  uif = user_if(sys.argv[0])
  args = uif.args
  fnames = []
  
  if args.file: 
    fnames.append(args.file)
    
  if not fnames:
    print('\n  File Error!\n\nFor more information call:  '+ args.name +'  --help' )
    args.parser.print_help()
    exit()
  for fname in fnames:
    if os.path.exists(fname):
      obj = entity_desc.entity_desc(fname, 
                                    vhdl=args.vhdl, vlog=args.vlog, 
                                    info=args.info, no_create=args.no_create, ) .create()
      try:
        obj.create()
      except:
        print(f'\n  Can not create entity_desc templates with file {fname} \n' );
    else:
      print(f'\n  Can not find file {fname}\n' );  
        
