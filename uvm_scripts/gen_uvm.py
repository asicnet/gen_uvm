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

""" Main-Module to create an easier uvm testbench

gen_uvm.py
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
from   uvm_support   import * # global functions
import uvm_create_db as cdb
import uvm_user_if   as uif

import uvm_sim       as usim
from pathlib import Path

#-----------------------#-----------------------#-----------------------#-----------------------#-----------------------
def get_pkg_name (path):
  '''Read the name of the package in the given file.'''
  
  with path.open() as f:
    lines = f.readlines()

  for line in lines:
    res = re.search(r'^\s*package\s+(\w+)\s*;',line)
    if res:
      pkg = res.group(1)
      log("get_pkg_name: found package name "  + pkg)
      return pkg
  res = re.search(r'(\w+)\..*;',path.name)
  if res: return res.group(1)
  return None

def check_common_pkg (tb,db):
  '''Check if the parameter common_pkg, dut_source_path and common_pre_pkg are defined and read or write the content'''
  if not (defined(tb,'common_pkg')):
    return 0

  if not (defined(tb,'dut_source_path')):
    print ('dut_source_path not defined for file '  ,tb['common_pkg']['file'])
    return 0

  fname = Path(os.path.join(tb['dut_source_path'],tb['common_pkg']['file'] ))
  if fname.exists():
    tb['common_pkg']['name'] = get_pkg_name(fname)
  else:
    tb['common_pkg']['name'] = re.sub(r'\..*','',fname.name)
    warning_prompt("common_pkg file ",str(fname.name)," not found ")

    pname = Path(tb['dut_source_path'])
    if not pname.exists():
      pname.mkdir(0o755,parents=True, exist_ok=True)
    if not fname.exists():
      fh = fname.open("w")
      fh.write("//generated "+tb['common_pkg']['file']+"\n\n")
      if defined( tb,'common_define'):
        fh.write(f"`include \"{tb['common_define']['file']}\"\n\n")
      fh.write("package "+tb['common_pkg']['name']+";\n\n")
      fh.write("  const time SYSTEM_CLK_PERIOD = 20ns;\n\n")
      
      for ag in db:
        if "port_list" in db[ag]:
          for a in db[ag]["port_list"] :
            if a["io"] == "out":
              #print( a["logic"] )# , f'{a["rst_name"]}' , f'= {a["rst_val"]};' , f'//  {db[ag]["if_instance_names"]}' )
              align(f'  const {a["logic"]}' , f'{a["rst_name"]}' , f'= {a["rst_val"]};' , f'//  {db[ag]["if_instance_names"]}' )
      fh.write(get_aligned())      
      fh.write("\nendpackage : "+tb['common_pkg']['name']+"\n")
      
      fh.close()

  if defined(tb,'common_pre_pkg'):
    if defined(tb['common_pre_pkg'],'file'):
      fname = Path(os.path.join(tb['dut_source_path'],tb['common_pre_pkg']['file'] ))

      if not fname.exists():
        warning_prompt(" common_pre_pkg file ",tb['common_pre_pkg']['file']," specified in ",tb['tpl']," not found in ",tb['dut_source_path'])
        fh = fname.open("w")
        fh.write("//generated " + fname.name)
        fh.close()

def check_common_env_pkg(tb):
  if not defined (tb,'common_env_pkg'):        return
  if not defined (tb['common_env_pkg'],'file'): return
  fname = Path(os.path.join(tb['inc_path'],"top",tb['common_env_pkg']['file'] ))
  if ( fname.exists() ):
    tb['common_env_pkg']['name'] = get_pkg_name(fname)
  else:
    pname = Path(tb['inc_path'])
    if not pname.exists():
      pname.mkdir(0o755,parents=True, exist_ok=True)
    if not fname.exists():
      warning_prompt("common_env_pkg file ",tb['common_env_pkg']['file']," specified in ",tb['tpl']," not found in ",tb['inc_path']+"/top")
      tb['common_env_pkg']['name'] = re.sub(r'\.sv', '' , tb['common_env_pkg']['file'] )
      
      fh = fname.open("w")
      fh.write("//generated " + fname.name)
      fh.write("\n\npackage " + tb['common_env_pkg']['name'] + ";\n\n")
      fh.write("endpackage : "+ tb['common_env_pkg']['name']+ ";\n\n")
      fh.close()


def after_parse_and_checks (tb,db):
  skeys = list(db.keys())
  skeys.sort()
  if not defined (tb,'stand_alone_agents'): tb['stand_alone_agents']=[]
  if not defined (tb,'agent_list')        : tb['agent_list']=[]
  for agent in skeys:
    if "top" != agent:
      if defined (db[agent],'stand_alone_agents'):
        for i in db[agent]['stand_alone_agents'] : tb['stand_alone_agents'].append(i)
      tb['agent_list'].append(db[agent]['agent_name'])
    if defined( tb,'common_pkg'):     db[agent]['common_pkg']     = tb['common_pkg']
    if defined( tb,'common_env_pkg'): db[agent]['common_env_pkg'] = tb['common_env_pkg']
    if defined( db[agent],'file_header_inc'):#]['file']) [' db[agent]['file_header_inc']['inline'] = "inline" ']
      db[agent]['file_header_inc']['inline'] = "inline"

def create_directories_and_copy_files (tb):
    project  = tb['project']
    if defined (tb,'backup'): backup = tb['backup']
    else: backup = "YES"
    top_name = tb['top_name']
    fproject = Path(project)
    #create backup of existing project directory
    if (fproject.exists()):
      if (backup != "NO"):
        print("Backup of existing generated files ! ")
        dircopy( project, project+".bak" )
    else:
      fproject.mkdir(0o755,parents=True, exist_ok=True)

    dir = project + "/sim"
    makedir( dir )
    dir = project + "/tb"
    makedir( dir )
    dir = project + "/tb/" + top_name
    makedir( dir )
    makedir( dir + "/sv" )
    dir = project + "/tb/" + top_name + "_tb"
    makedir( dir )
    makedir( dir + "/sv" )
    dir = project + "/tb/" + top_name + "_test"
    makedir( dir )
    makedir( dir + "/sv" )

    from_dir = tb['dut_source_path']
    tb['dut_tb_dir'] = "dut"
    tb['dut_tb_path'] = project + "/" + tb['dut_tb_dir']

    to_dir = tb['dut_tb_path']
    check_dir(from_dir)

    if ( from_dir != to_dir ):
        dircopy( from_dir, to_dir )
    else:
        log("dut_path does not exist. Nothing to copy from DUT\n")


    tdir = Path(project + "/tb/include")
    fdir = Path(tb['inc_path'])
    if ( fdir.exists() and (tb['update_include'] == "YES" or not tdir.exists() )):
        dircopy( fdir , tdir )


def gen_cmd(tb):

    cmd= "call \"" + sys.executable + "\"   "
    for i in sys.argv:
      cmd += i + ' '
    if not re.search(r"\.tpl",cmd):
      for i in tb['ctpl']:
        cmd += i + ' '
    cmd = re.sub(r"-overwrite","",cmd)
    cmd = re.sub(r"-o","",cmd)

    if ( sys.platform == "win32" ) or edef(tb,'os', 'WINDOWS'):

      fname = "gen_tb.cmd"
      file = Path(fname)
      if not file.exists() or edef(tb['args'],'overwrite',True):
        FH = file.open("w")
        die(FH, "Exiting due to Error: can't open file: "+fname)

        FH.write(cmd + "\n")
        FH.write("pause\n")

        FH.close()
        os.chmod( fname, 0o755 )
        print ("generate shell script gen_tb.cmd with :"+cmd)

    if ( sys.platform != "win32" ) or edef(tb,'os', 'LINUX'):

      fname = "gen_tb.sh"
      file = Path(fname)
      if not file.exists() or edef(tb['args'],'overwrite',True):
        FH = file.open("w")
        die(FH, "Exiting due to Error: can't open file: "+fname)

        FH.write(cmd + "\n")

        FH.close()
        os.chmod( fname, 0o755 )
        print ("generate shell script gen_tb.sh with :"+cmd)

def gen_tpl(tpl):

  agent = re.sub(r"\..*",'',tpl)
  fname =agent + '.tpl'

  file = Path(fname)
  if not file.exists():
    FH = file.open("w")
    die(FH, "Exiting due to Error: can't open file: "+fname)
  else: die(0, "The file: "+fname+" exists!!")
  agent_is_active = 'UVM_PASSIVE'
  passive_comment = "#"
  choise = input("Is the Agent 'UVM_ACTIVE' ? (y/n)!  [n] >> ")
  if (choise.upper() == 'Y'):
    agent_is_active = 'UVM_ACTIVE'
    passive_comment = ''

  agent_has_active_reset = "NO"
  rst_if = f', {clock_reset}_if_0.{reset}'
  choise = input("Is the Agent the reset generator ? (y/n)!  [n] >> ")
  if (choise.upper() == 'Y'):
    rst_if = ''
    agent_has_active_reset = "YES"
  else:
    choise = input(f"Name of Agent for clock/reset generator ? (default {clock_reset}) >> ")
    if (choise != ''): rst_if = ", "+ choise +'_if_0.'+reset

  FH.write(f'''
agent_name      = {agent}
description     = Agent for {agent} in project {PROJECT_NAME}

agent_is_active = {agent_is_active}   # UVM_PASSIVE or UVM_ACTIVE
agent_has_active_reset    = {agent_has_active_reset}

trans_inc_inside_class    = {agent}_inc_item.sv
if_inc_inside_interface   = {agent}_inc_interface.sv
monitor_inc_inside_class  = {agent}_inc_monitor.sv
{passive_comment}agent_seq_inc             = {agent}_inc_seq.sv
{passive_comment}driver_inc_inside_class   = {agent}_inc_driver.sv

agent_cover_generate_methods_inside_class  = no
agent_cover_generate_methods_after_class   = no
agent_cover_inc_inside_class  = {agent}_inc_cover.sv
#agent_coverage_enable = no

#interface signal (VHDL-ports)
if_clock   = {clock} ;
if_reset   = {reset} {rst_if};     #//, {clock_reset}_if_0.{reset};

if_port    = logic         {clock} ;
if_port    = logic         {reset} ;

if_port    = logic [1:0]   i_input             ; //-- : in  std_logic_vector(w-1 downto 0);
if_port    = logic         o_output            ; //-- : out std_logic;
#if_port   = type  range   name                ; //-- : in/out vhdl type;

#if_port    = int          mode ;
#if_port    = event        trigger;

#transaction variables for monitor, driver, scoreboard and coverage
trans_var = logic [1:0]   i_input             ; //-- : in  std_logic_vector(w-1 downto 0);
trans_var = logic         o_output            ; //-- : out std_logic;
#trans_var = type  range   name                ; //-- : in/out vhdl type;
#trans_var = int           mode = 0;
#trans_var = int           target = 0;

trans_var = int target = 0; // SB=0,COV=1

#interface mapping (assign in top_th)
#if_map = <{agent} if_port> , <agent>_if_<nr>   . <signal>
#if_map = <{agent} if_port> , uut[{{.<instanze]}}]. <signal>
#if_port    = logic timeout           ; #  timeout error
#if_map     = timeout         , uut.inst_master.o_timeout
#if_port    = logic          synchro_flag ;
#if_map     = synchro_flag , myagent_if_0.i_synchro_flag

#configuration variables
config_var      = int sequence_number = 1;
#agent_copy_config_vars         = {agent}_copy_config_vars.sv

''')



def gen_com(prj):
  common = re.sub(r"\..*",'',prj)
  fname = common + '.tpl'

  if Path(fname).exists():
    fname = 'my'+ fname

  file = Path(fname)
  if not file.exists():
    FH = file.open("w")
    die(FH, "Exiting due to Error: can't open file: "+fname)
  else: die(0, "The file: "+fname+" exists!!")

  project = ''
  while (project == ''):
    project = input("Name of the project (top entity name) >> ")
  project = project.lower()

  files = 'files.f'
  choise = input("Name of the source_list_file (default "+files+") >> ")
  if (choise != ''): files = choise

  import datetime
  now = datetime.datetime.now()
  
  try:
    uvm_template
  except:
   uvm_template = "uvm_template"
  
  
  FH.write(f'''

dut_top          = {project}
source_list_file = {files}
sb_top           = top
dut_hdl_com      = vcom

vlog_option      =  -suppress 7053,13177,2282
vlog_option      =  +incdir+C:/questasim64_10.7b/verilog_src/uvm-1.1d/src

framework        = yes
fw_overwrite     = yes
no_logfile       = yes
print_date       = no
backup           = no


copyright        = {copyright} 
author           = {author   } 
email            = {email    } 
tel              = {tel      } 
dept             = {dept     } 
company          = {company  } 
year             = {now.year }

script_version   = 1.0.0
tmplt_include_file = {uvm_template}  #not used

description             = {project} Submodule
repository_version      = SVN/GIT Number
code_version            = {project} NUMBER from {now.year}-{"%02d"%now.month}-{"%02d"%now.day}
test_spec_version       = {project} {now.year}-{"%02d"%now.month}-{"%02d"%now.day}
version                 = #unknown
#os                      = linux

uvm_common     = ../uvm_common
common_define  = common_defines.sv
common_pkg     = {project}_pkg.sv

nested_config_objects  = yes

tmplt_test_case =  RESET_VALUES                         # 1
tmplt_test_case =  SET_SIGNALS                          # 2

config_var = int top_test_start_nr = 1;
config_var = int top_test_end_nr   = 1;
config_var = int execution_mode    = 2;  #0=nop , 1=random , 2=directed, 3=booth

uvm_cmdline = +UVM_VERBOSITY=UVM_MEDIUM  ## UVM_HIGH / UVM_MEDIUM ## => benoetigt Neuaufruf von gen_tp.com und Simulator GUI run_<gui/batch>.cmd

top_env_generate_scoreboard_class                  = yes
top_env_scoreboard_generate_methods_inside_class   = no
top_env_scoreboard_generate_methods_after_class    = no
top_env_scoreboard_inc_inside_class                = {project}_inc_scoreboard.sv

test_generate_methods_inside_class   = no  # build_phase
test_generate_methods_after_class    = no  # build_phase
test_inc_inside_class                = {project}_inc_test.sv

''')

#-----------------------#-----------------------#-----------------------#-----------------------#-----------------------

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
  tb = db['top']
  tb['args'] = auif.db


  if 0:
    json.dump(db,sys.stdout,indent=3,sort_keys=True)

  #print (json.dump(tb,sys.stdout,indent=3,sort_keys=True))
  check_common_pkg(tb,db)
  check_common_env_pkg(tb)
  after_parse_and_checks(tb,db)

  create_directories_and_copy_files(tb)
  gen_cmd(tb)

  if 1:
    json.dump(db,open("uvm_db.json","w"),indent=3,sort_keys=True)

  skeys = list(db.keys())

  skeys.sort()

  os.environ['tmplt_include_file_name'] = tb['tmplt_include_file']

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

  if edef(tb,'no_logfile','YES'):
    import os
    os.remove("uvm_gen.log")
    print("uvm_gen.log file removed!")

  if args.json:

    json.dump(db,open("gen_uvm.json","w"),indent=3,sort_keys=True)


  print ("\n\n")


