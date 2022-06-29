#!/usr/bin/env python3
# -*- coding: utf8 -*-
#========================================================================================================================#
# Copyright (c) 2022 By AsicNet.  All rights reserved.
# You should have received a copy of the license file containing the MIT License (see LICENSE.TXT), if not, 
# contact AsicNet software@asicnet.de
#
# THE SOFTWARE GEN_UVM IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS 
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#========================================================================================================================#

""" Main-Script to create an easier uvm testbench

gen_uvm.py or __init__.py or __main__.py
version 1.0.0

"""

from header_cfg import *

import sys
#if sys.version_info[0] < 3 or sys.version_info[1] < 8:
#    raise Exception("Python 3.8 or a more recent version is required.")
import datetime
import re
import os
import json
from   uvm_support    import * # global functions
import uvm_create_db  as cdb
import uvm_user_if    as uif
import uvm_sim        as usim
import uvm_create_env as uenv

from pathlib import Path

if __name__ == '__main__':

  auif = uif.uvm_user_if(sys.argv[0])
  args = auif.args

  VERNUM =  "ASICNET 2022 1.0.0"

  if args.setup: 
    import uvm_setup 
    sdb = {}  
    obj = uvm_setup.SETUP(sdb)
    obj.generate_top()
    if not args.all: exit()
    
  if args.gentpl: gen_tpl (args.gentpl);exit()
  if args.gencom: gen_com (args.gencom);exit()

  db = cdb.uvm_create_db(args.common,args.agent).get_db()
  db['top']['args'] = auif.db
  
  if 0:
    json.dump(db,sys.stdout,indent=3,sort_keys=True)
  #print (json.dump(tb,sys.stdout,indent=3,sort_keys=True))

  main = uenv.UVM_CREATE_ENV(db)
  main.check_common_pkg()
  main.check_common_env_pkg()
  main.after_parse_and_checks()
  main.create_directories_and_copy_files()
  main.gen_cmd()

  if 1:
    json.dump(db,open("uvm_db.json","w"),indent=3,sort_keys=True)

  skeys = list(db.keys())

  skeys.sort()

  os.environ['tmplt_include_file_name'] = db['top']['tmplt_include_file']

  import uvm_agent as uag
  obj = uag.AGENT(db)

  regmodel = 0

  for ag in skeys:
    if ag == 'top': continue
    print ("generate agent ", ag )

    obj.generate_agents(ag)

  if 0:
    json.dump(db,open("uvm_agent.json","w"),indent=3,sort_keys=True)

  import uvm_top as utop
  obj = utop.TOP(db)
  obj.generate_top()

  obj = usim.SIM(db)
  obj.generate_sim()

  if edef(db["top"],'no_logfile','YES'):
    import os
    os.remove("uvm_gen.log")
    print("uvm_gen.log file removed!")

  if args.json:

    json.dump(db,open("gen_uvm.json","w"),indent=3,sort_keys=True)


  print ("\n\n")


