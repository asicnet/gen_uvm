#!/usr/bin/env python3.9
# -*- coding: utf8 -*-
""" Generator module to create all agent tpl file for a new project

compatible with easier_uvm

uvm_setup.py 
Version 0.1.0

"""

from header_cfg import *

import datetime
import re
import os
import sys
import json
from   uvm_support   import *      # global functions
from   pathlib       import Path

class SETUP():
  '''Class for PIN List Generator
  The the data base is given to create a top directory structure
  '''

  def __init__(self, verbose='info',ind=3):
      '''Define objekt variables and print debug infos
      '''
      self.db = {}
      
      try:
        self.db["CLOCK"] = clock    
      except:
        self.db["CLOCK"] = "clock"
      
      try:
        self.db["RESET"] = reset
      except:
        self.db["RESET"] = "reset"

      self.verbose = verbose
      self.ind=ind
      if ind:
          self.indstr=' '*ind

#      if severityLevel(self.verbose,'debug'):
#          class_name = self.__class__.__name__
#          print_fc(class_name + ' created','gr')

  def get_width(self,mrange):
    res = re.search(r"\[\s*(\d+)\s*:\s*(\d+)\s*\]",mrange)
    if res: 
      return ( abs( int(res.group(1)) - int(res.group(2)) ) +1 )
    else:
      return (0)
      
  
  def gen_pinlist(self):
  
    reset = self.db["RESET"]
    clock = self.db["CLOCK"]
    fname = "pinlist.txt"
    
    file = Path(fname)
    if not file.exists():
      PFH = file.open("w")
      die(PFH, "Exiting due to Error: can't open file: "+fname)
    else: 
      return
    
    for infa in self.db["DEC"]:
      PFH.write( f"\nDEC {infa}\n\n")
      
    align()  
    for infa in self.db["PAR"]:
      for ind in infa:
        align( f"PAR = {ind}", f"{infa[ind]}")
    align()  
    PFH.write(get_aligned())


    for infa in self.db["IF"]:
      if len(self.db["IF"][infa]):
        PFH.write( f"\n!{infa}\n\n")
        
        for port in self.db["IF"][infa]:
          align("  "+port["port"],port["wire"])
          if port["dir"] == "reset": reset = port["wire"]
          if port["dir"] == "clock": clock = port["wire"]
        text = get_aligned() 
        PFH.write( text +"\n")
    
    self.db["CLOCK"] = clock    
    self.db["RESET"] = reset
    
    PFH.close()

  def get_entity_desc(self,desc="entity_desc.txt"):

    db = self.db
    fname = desc
    file = Path(desc)

    if file.exists():
      if 0 == os.path.getsize(file):
        die(0,"File entity_desc.txt is empty")
      PFH = file.open("r")
      die(PFH, "Exiting due to Error: can't open file: "+fname)
    else:
      
      die(0,"File entity_desc.txt not found")

    count_of_trailing_comments = 0
    if_name = "top"
    param = []
    var_dec=[]
    interface = {if_name :[]}
    agent = {}
    lines = PFH.readlines()
    
    for line in lines:
      line = re.sub(r"(#|//).*$","",line)   # remove comments
      line = re.sub(r"\s*$","",line)        # remove comments
      res = re.search(r"^\s*$", line)       # check for empty line
      if res : continue                     # next if empty
      line = re.sub(r"[\r\n]*","",line)     # remove CR/LF

      parameters   = re.search(r"^\s*PAR\s*(\||\=)\s*(\S+)\s+(\S+)",line)
      variable_dec = re.search(r"^\s*DEC\s*(\||\=)\s*(.+)\s*",line)
      entity       = re.search(r"^\s*ENTITY\s*(\||\=)\s*(.+)\s*",line)
      next_if_name = re.search(r"^\s*!(\w+)(.*)?",line)
      ports        = re.search(r"^\s*([^!]\S+)\s+(\S+)\s*(.*)?",line)
      
      if (entity):
        db["ENTITY"]  = entity.group(2)
      elif ( parameters ) :
        param.append({parameters.group(2):parameters.group(3)})

      elif ( variable_dec ) :
        var_dec.append(group(2))
        
      elif ( ports ) :
        mport = ports.group(1)
        mwire = ports.group(2)
        mspec = ports.group(3) 
                               
        mdir   = 'out'
        mrange = ''
        mwidth = 0
        mtype  = "logic"
        mreset = "0"
        
        res = re.search(r'\s*(\w+)\s*(\[.*\])?\s*(\w+)?\s*:?(=\s*(.+))?',mspec)
        if res:
          if res.group(1): mdir   = res.group(1)
          if res.group(2): mrange = res.group(2)
          if res.group(3): mtype  = res.group(3)
          if res.group(5): mreset = res.group(5)
          if mrange: mwidth = self.get_width(mrange)

        interface[if_name].append( { "port"  : mport  ,
                                     "wire"  : mwire  ,
                                     "spec"  : mspec  ,
                                     "dir"   : mdir   ,
                                     "range" : mrange ,
                                     "type"  : mtype  ,
                                     "width" : mwidth ,
                                     "reset" : mreset
                                   } )
                             
      elif ( next_if_name ):
        if_name = next_if_name.group(1)
        rest    = next_if_name.group(2)
        active = None
        reset  = None
        res     = re.search(r"(active|passive)",rest)
        if res: 
          active = res.group(1)
        
        res     = re.search(r"(reset)",rest)
        if res: reset   = res.group(1)
        
        res = re.search(r"_if_\d+",if_name)
        if not res:
          res = re.search(r"_if",if_name)
          if res: if_name += "_0"
          else:   if_name += "_if_0"
            
        if not defined (interface, if_name):
          interface[if_name] = []
          agent_name = re.sub(r"_if_\d+","",if_name)
          agent[agent_name] = {"active":active,
                            "reset" :reset
                           }
    # end for
    
    PFH.close()

    db["IF"]  = interface
    db["PAR"] = param
    db["DEC"] = var_dec
    db["AGENT"] = agent
    
    rst_gen = None
    for ag in agent:
      if agent[ag]["reset"]:
        if rst_gen:
          die(0,"Only one interface can have the attribute 'reset'!")
        else:
          rst_gen = ag
    
    db["RST_GEN"] = rst_gen

    for tpl in interface:
      print (tpl,"==")
      res = re.search(f"(.*)(_if_\d+)",tpl)
      if res:
        if mdefined (db["AGENT"],res.group(1),"nr_of_if"):
          db["AGENT"][res.group(1)]["nr_of_if"] = db["AGENT"][res.group(1)]["nr_of_if"] + 1
        else : 
          db["AGENT"][res.group(1)]["nr_of_if"] = 1
          
    #tpl_list = {}
    #for tpl in interface:
    #  res = re.search(f"(.*)(_if_\d+)",tpl)
    #  if res:
    #    if defined (tpl_list,res.group(1)):
    #      tpl_list[res.group(1)]= tpl_list[res.group(1)] + 1
    #    else : 
    #      tpl_list[res.group(1)]= 1
    #      
    #db["TPL"] = tpl_list
    
    return db
   
  def gen_tpl(self):
    for agent in self.db["AGENT"]:  
      fname = agent + '.tpl'
      print ("--" , fname)
      file = Path(fname)
      if not file.exists():
        FH = file.open("w")
        die(FH, "Exiting due to Error: can't open file: "+fname)
      else: 
        #die(0, "The file: "+fname+" exists!!")
        continue
        #FH = file.open("w")
        
      agent_is_active = 'UVM_PASSIVE'
      passive_comment = "#"
      if self.db["AGENT"][agent]["active"] == "active":
        agent_is_active = 'UVM_ACTIVE'
        passive_comment = ''
      elif self.db["AGENT"][agent]["active"] == "passive" or self.db["AGENT"][agent]["active"] == None:
        agent_is_active = 'UVM_PASSIVE'
      else:  
        choise = input(f"Is the Agent {agent} 'UVM_ACTIVE' ? (y/n)!  [n] >> ")
        if (choise.upper() == 'Y'):
          agent_is_active = 'UVM_ACTIVE'
          passive_comment = ''
    
      agent_has_active_reset = "NO" 
      rst_gen = self.db["RST_GEN"]  
      if rst_gen:
        if agent == rst_gen:
          rst_if = ''
          agent_has_active_reset = "YES"
        else:  
          rst_if = ", "+ rst_gen +'_if_0.'+ self.db["RESET"]
      else:  
        rst_if = f', {clock_reset}_if_0.{self.db["RESET"]}'
        choise = input(f"Is the Agent {agent} the reset generator ? (y/n)!  [n] >> ")
        if (choise.upper() == 'Y'):
          rst_if = ''
          agent_has_active_reset = "YES"
        else:
          choise = input(f"Name of Agent  {agent} for clock/reset generator ? (default {clock_reset}) >> ")
          if (choise != ''): rst_if = ", "+ choise +'_if_0.'+self.db["RESET"]

      yesno = "yes"
      if (agent == "clk_rst_gen"):
        yesno = "no"

      cnt=""
      if self.db["AGENT"][agent]["nr_of_if"]>1:
        cnt = f"\nnumber_of_instances      = {self.db['AGENT'][agent]['nr_of_if']}\n"
      
      cmpt = "" 
      if (compatible == 1):
        cmpt = agent+"/"
        
      FH.write(f'''
agent_name      = {agent}
description     = Agent for {agent} in project {PROJECT_NAME}

agent_is_active = {agent_is_active}   # UVM_PASSIVE or UVM_ACTIVE
agent_has_active_reset    = {agent_has_active_reset}
{cnt}
trans_item                = item  # default
trans_inc_inside_class    = {cmpt+agent}_inc_item.sv
if_inc_inside_interface   = {cmpt+agent}_inc_interface.sv
monitor_inc_inside_class  = {cmpt+agent}_inc_monitor.sv
{passive_comment}agent_seq_inc             = {cmpt+agent}_inc_seq.sv
{passive_comment}driver_inc_inside_class   = {cmpt+agent}_inc_driver.sv

agent_cover_generate_methods_inside_class  = no
agent_cover_generate_methods_after_class   = no
agent_cover_inc_inside_class  = {cmpt+agent}_inc_cover.sv
agent_coverage_enable = {yesno}

#interface signal (VHDL-ports)
if_clock   = {self.db["CLOCK"]} ;
if_reset   = {self.db["RESET"]} {rst_if};     #//, {clock_reset}_if_0.{self.db["RESET"]};

if_port    = logic         {self.db["CLOCK"]} ;
if_port    = logic         {self.db["RESET"]} ;

'''   )
      wire_cnt = {}
      for i in range(0,self.db["AGENT"][agent]["nr_of_if"]):
        infa = self.db["IF"][agent+"_if_"+str(i)]
        for line in infa:
          mwire  = line["wire"]
          mtype  = line["type"]
          mrange = line["range"]
          mdir   = line["dir"]
          mreset = line["reset"]
          mwidth = ""
          if defined (wire_cnt, mwire):
            pass
          elif mdir != "clock" and mdir != "reset":
            wire_cnt[mwire] = 1
            if mtype != "logic":
              mrange = ''
              cnt = line["width"]
              mwidth = f"[{cnt}]"
            align(f"if_port    = {mtype} ", mrange, mwire+mwidth ,f"; // {mdir} := {mreset}")
        
        FH.write("\n"+ get_aligned() +  "\n")         

      wire_cnt = {}
      for i in range(0,self.db["AGENT"][agent]["nr_of_if"]):
        infa = self.db["IF"][agent+"_if_"+str(i)]
        for line in infa:
          mwire  = line["wire"]
          mtype  = line["type"]
          mrange = line["range"]
          mdir   = line["dir"]
          mwidth = ""
          if defined (wire_cnt, mwire):
            pass  
          elif mdir != "clock" and mdir != "reset":
            wire_cnt[mwire] = 1
            if mtype != "logic":
              mrange = ''
              cnt = line["width"]
              mwidth = f"[{cnt}]"
            align(f"trans_var  = {mtype} ", mrange, mwire+mwidth  ,";")
        
        FH.write("\n"+ get_aligned() +  "\n")         
  
      FH.write(f'''

trans_var  = int           target = 0;      # SB=0,COV=1

#interface mapping (assign in top_th)
#if_map = <{agent} if_port> , <agent>_if_<nr>     . <signal> [ , if_<nr_of_if> ] [;]
#if_map = <{agent} if_port> , uut[{{.<instanze]}}]. <signal> [ , if_<nr_of_if> ] [;]
#if_port    = logic grand           ; 
#if_map     = grand         , uut.inst_master.grand
#if_port    = logic          request_flag ;
#if_map     = request_flag , myagent_if_0.request_flag

#configuration variables
#config_var      = int sequence_number = 1;
#agent_copy_config_vars         = {cmpt+agent}_copy_config_vars.sv

'''    )
  
  
  def check_project(self):
  
    if defined (self.db,"ENTITY"):
      project = self.db["ENTITY"]
    else:  
      choise = input("Name of the project (top entity name) >> ")
      if (choise != ''): project = choise
      project = project.lower()
      self.db["ENTITY"] = project
      
    self.db["common_pkg"]       = project + "_pkg"
    self.db["project"]          = project 
    self.db["source_list_file"] = 'files.f'
    #choise = input("Name of the source_list_file (default "+files+") >> ")
    #if (choise != ''): files = choise
  #-------------------------------------------------------------------------------------

  def gen_com(self):
   
    fname   = "common.tpl"
    files   = self.db["source_list_file"]
    project = self.db["project"]

    file = Path(fname)
    if not file.exists():
      FH = file.open("w")
      die(FH, "Exiting due to Error: can't open file: "+fname)
    else: 
      print("The file: "+fname+" exists!!")
      return
    
    import datetime
    now = datetime.datetime.now()
    uvm_template = "uvm_template"
    try:
      uvm_template = tmplt_include_file
    except:
      pass
    
    cmpt = "" 
    if (compatible == 1):
      cmpt = "top/"
        
    
    FH.write(f'''
  
dut_top          = {project}
source_list_file = {files}
sb_top           = top
dut_hdl_com      = vcom  # None to use precompiled work
dut_pfile        = pinlist.txt

# Verilog compile options !
#vlog_option      =  -suppress 12345
#vlog_option      =  +incdir+{os.environ["QUESTA_HOME"]}/verilog_src/uvm-1.1d/src

# VHDL compile options
# vcom_options = 
# vopt_options =
# vsim_options =

fw_overwrite     = yes
no_logfile       = yes
print_date       = yes
backup           = yes


copyright        = {copyright} 
author           = {author   } 
email            = {email    } 
tel              = {tel      } 
dept             = {dept     } 
company          = {company  } 
year             = {now.year }

script_version   = 1.0.0
tmplt_include_file = {uvm_template}  

description             = {project} Top/Sub Module
repository_version      = SVN/GIT Number
code_version            = {project} NUMBER from {now.year}-{"%02d"%now.month}-{"%02d"%now.day}
test_spec_version       = {project} {now.year}-{"%02d"%now.month}-{"%02d"%now.day}
version                 = #unknown

generate_file_header    = yes  

#os                      = linux  # optional for *.sh shell scripts ;  os = windows #optional for *.cmd scripts

#uvm_common     = ../uvm_common        # if defined copy all data from .../uvm_common/ to .../dut/
common_define  = common_defines.sv
common_pkg     = {project}_pkg.sv

nested_config_objects  = yes

tmplt_top_active_agent = {self.db["RST_GEN"]}

tmplt_test_case =  RESET_VALUES                         # 1
tmplt_test_case =  SET_SIGNALS                          # 2

config_var = int top_test_start_nr = 1;
config_var = int top_test_end_nr   = 2;
config_var = int execution_mode    = 2;  #0=nop , 1=random , 2=directed, 3=booth

uvm_cmdline = +UVM_VERBOSITY=UVM_MEDIUM  ## UVM_HIGH / UVM_MEDIUM ## => benoetigt Neuaufruf von gen_tp.com und Simulator GUI run_<gui/batch>.cmd

top_env_generate_scoreboard_class                  = yes
top_env_scoreboard_generate_methods_inside_class   = no
top_env_scoreboard_generate_methods_after_class    = no
top_env_scoreboard_inc_inside_class                = {cmpt+project}_inc_scoreboard.sv

test_generate_methods_inside_class   = no  # build_phase
test_generate_methods_after_class    = no  # build_phase
test_inc_inside_class                = {cmpt+project}_inc_test.sv

#th_inc_inside_module                = {cmpt+project}_inc_th.sv         inline

''' )

    for agent in self.db["AGENT"]:
          FH.write("tpl = "+ agent +".tpl\n")
    
    FH.close()    

  def gen_cmd(self):

    cmd= "call " + tool + " " + join(script_path , genscript+" ")
    cmdl="python "
    for i in self.db["AGENT"]:
      i=re.sub(f"\..*$","",i)
      cmd += i + '.tpl '
      cmdl += i + '.tpl '

    if ( sys.platform == "win32" ):

      fname = "gen_tb.cmd"
      file = Path(fname)
      if not file.exists() : #or edef(tb['args'],'overwrite',True):
        FH = file.open("w")
        die(FH, "Exiting due to Error: can't open file: "+fname)

        FH.write(cmd + "\n")
        FH.write("pause\n")

        FH.close()
        os.chmod( fname, 0o755 )
        print ("generate shell script gen_tb.cmd with :"+cmd)

    if ( sys.platform != "win32" ):

      fname = "gen_tb.sh"
      file = Path(fname)
      if not file.exists() : #or edef(tb['args'],'overwrite',True):
        FH = file.open("w")
        die(FH, "Exiting due to Error: can't open file: "+fname)

        FH.write(cmdl + "\n")

        FH.close()
        os.chmod( fname, 0o755 )
        print ("generate shell script gen_tb.sh with :"+cmdl)
        
  def gen_pkg(self):
   
    pname = Path("dut")
    if not pname.exists():
      pname.mkdir(0o755,parents=True, exist_ok=True)
      
    name = self.db["common_pkg"] 
    fname = name + ".svh" 
    pname = Path("dut/"+fname)
    if not pname.exists():
      fh = pname.open("w")
      fh.write("//generated "+fname+"\n\n")
      fh.write("`include \"../dut/common_defines.sv\"\n\n")
      fh.write("package "+name+";\n\n")
      fh.write("// `include \"<vhdl_to_sv>_pkg.sv\"")
      fh.write("  const time SYSTEM_CLK_PERIOD = 20ns;\n\n")
      port_cnt = {}
      for infa in self.db["IF"]:
        for ports in self.db["IF"][infa]:
          if ports["dir"] == "out":
            if defined (port_cnt,ports["wire"]): pass
            else:
              port_cnt[ports["wire"]] = 1
              mrst = "rst_" + re.sub(r"^o_","",ports["wire"])
              
              ports["type"]  = str(ports["type"]  )
              ports["range"] = str(ports["range"] )
              mrst           = str(mrst           )
              ports['reset'] = str(ports['reset'] )
              infa           = str(infa           )

              align ( "  const ", ports["type"] , ports["range"],mrst, "= "+ ports['reset']+";" ,"     //  "+infa)
        align ()    
      fh.write(get_aligned() +"\n")
      
      fh.write("\nendpackage : "+name+"\n")
      fh.close()

  def gen_source_list_file(self):
    name = self.db["source_list_file"] 
    pname = Path("dut/"+name)
    if not pname.exists():
      fh = pname.open("w")
      fh.write("\n" + self.db["project"]  +".vhd\n")
      fh.close()
    
  def gen_wave(self):
    fname = "wave.do"
    file = Path(fname)
    if not file.exists():
      FH = file.open("w")
      die(FH, "Exiting due to Error: can't open file: "+fname)
    else: 
      #die(0, "The file: "+fname+" exists!!")
      return
      #FH = file.open("w") 
    
    align("add wave -group TH     ","sim:/top_tb/th/*")
    align("add wave -group UUT    ","sim:/top_tb/th/uut/*")
    align()
    for agif in self.db["IF"]:
      res = re.search(f"(.*)(_if_\d+)",agif)
      if res:
        align( "add wave -group "+agif, "sim:/top_tb/th/"+agif+"/*")

    add_wave = get_aligned()
 
    FH.write( f'''\
    
if {{ $init_start }} {{

view wave       -undock
view transcript

run 0
onerror {{resume}}
quietly WaveActivateNextPane {{}} 0

{add_wave}

TreeUpdate [SetDefaultTree]

quietly wave cursor active 1
configure wave -namecolwidth 150
configure wave -valuecolwidth 100
configure wave -justifyvalue left
configure wave -signalnamewidth 1
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ns

wave zoom full

set init_start 0

}}

run 0

#add definitions after elaboration visible
#add wave -group <SystemVerilog Agent>      sim:/uvm_root/uvm_test_top/m_env/m_<agent>_agent/*

''')  

    FH.close()

  def generate_top (self):

    self.db = self.get_entity_desc()
    enable = 1
    setup = ""
	
    if(json_enable & enable==1):
      json.dump(self.db,open("get_entity_desc.json","w"),indent=3,sort_keys=True)
    self.check_project()
    
    pname = Path("uvm_"+self.db["ENTITY"]+setup)
    if not pname.exists():
      pname.mkdir(0o755,parents=True, exist_ok=True)
    
    os.chdir(pname)

    self.gen_pinlist()
    self.gen_com()
    self.gen_tpl()
    self.gen_cmd()
    self.gen_pkg()
    self.gen_source_list_file()
    self.gen_wave()
    
    if(json_enable & enable==1):
      json.dump(self.db,open("gen_setup.json","w"),indent=3,sort_keys=True)

    print("Generating pinlist done!\n")

##==============================================================
if __name__ == '__main__':

  db = {}
  
#  f=open('uvm_agent.json')
#  db = json.load(f)
#
#  skeys = list(db.keys())
#
#  skeys.sort()
#  print(skeys)

  obj = SETUP(db)
  regmodel = 0
  print("------------------------------------------------")

  print ("generate TOP " )

  obj.generate_top()
  if(json_enable):
    json.dump(obj.db,sys.stdout,indent=3,sort_keys=True)
  
  print("------------------------------------------------")


