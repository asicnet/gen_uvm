#!/usr/bin/env python3.9
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

""" Generator module to create an agent directory

uvm_agent.py
version 1.0.0

"""
import datetime
import re
import os
import sys
import json
import shutil
from   uvm_support   import * # global functions
from pathlib import Path
from uvm_base import *
from header_cfg  import *


class SIM(UVM_BASE):
  '''Class for SIM Generator
  The data base is given to create a top directory structure
  '''

  def __init__(self, database, verbose='info',ind=3):
      '''Define objekt variables and print debug infos
      '''
       
      UVM_BASE.__init__( self, database, verbose, ind)
     
      #self.verbose = verbose
      #self.ind=ind
      #self.db = database
      #self.tb = database['top']
      self.args = self.tb['args']

      #if ind:
      #    self.indstr=' '*ind
      #
      #if severityLevel(self.verbose,'debug'):
      #    class_name = self.__class__.__name__
      #    print_fc(class_name + ' created','gr')

  def gen_sim_dir(self,ag):
    top = self.db[ag]
    log( "Reading: top\n" + top['agent_name'])
    mdir = top['project']+"/sim"
    log( "sim mdir: ",mdir,"\n")
    makedir( mdir )

  def deal_with_files_f(self):
    tb = self.db['top']
    if defined(tb,'dut_source_path') and defined(tb,'source_list_file'):
      src_name = tb['dut_source_path']+"/"+tb['source_list_file']
      src = Path(src_name)

      if not src.exists():       # tb['source_list_file']  does not exist, so create source_list_file in the output directory
        src = Path(src_name)

        FH = src.open( "w" )
        flist = os.listdir(tb['dut_source_path'])
        for f in flist:
          res = re.search(r".*\.svh?",f)
          resv= re.search(r".*\.v",f)
          if ( res or resv ):
            FH.write(f+"\n")
        FH.close()

        pexit("ERROR: "+src_name+" does not exist, so create source_list_file! check template "+src_name+" in the dut directory")

  def gen_vcs_script(self):
    tb = self.db['top']
    mdir = tb['project'] + "/sim"
    vcs_opts =  "-sverilog +acc +vpi -timescale="+ tb['timeunit'] + "/"+ tb['timeprecision'] + " -ntb_opts uvm-1.2"
    script =   mdir + "/compile_vcs.sh"
    FH = Path(script).open( "w" )

    FH.write("#!/bin/sh\n")
    FH.write("vcs "+ vcs_opts + " \\\n")
    self.gen_compile_file_list()
    FH.write("-R +UVM_TESTNAME="+ tb['top_name'] + "_test "+ tb['uvm_cmdline'] + " \$* \n")
    FH.close()
    ### add execute permissions for script
    os.chmod( script, 0o755)

  def gen_ius_script(self):
    print("gen_ius_script is not implemented yet!")
    pass
    
  def gen_riviera_script(self):
    print("gen_ius_script is not implemented yet!")
    pass
    
  def gen_questa_script(self):
    self.gen_framework_script()
    
  def gen_framework_script(self):
    tb = self.db['top']
    db = self.db
    args = tb['args']
    mdir = tb['project'] + "/sim"
    file = Path(mdir+"/compile.tcl")
    FH = file.open("w")
    FH.write("\n")
    FH.write("transcript file compilation_transcript.txt\n\n")
    FH.write("#file delete -force work\n\n")
    FH.write("#vlib work\n\n")
    FH.write("#compile the dut code\n")
    
    
    questa_home = os.getenv('QUESTA_HOME',"$::env(QUESTA_HOME)")
    if questa_home == "$::env(QUESTA_HOME)":
        print("\n\n   !! Environment Variable 'QUESTA_HOME' is not defined. !!\n\n")
		
    if questa_home:
      tb['vlog_option'] +=  " -sv -permissive" +" -timescale " + tb['timeunit'] + "/"+ tb['timeprecision'] + " +incdir+" + questa_home +"/verilog_src/uvm-1.1d/src"  
    if edef( tb ,'dut_hdl_com' , "vcom"):
      FH.write("set cmd \""+ tb['dut_hdl_com'] + " " + tb['vcom_option'] + " -F ../"+ tb['dut_tb_dir'] + "/"+ tb['source_list_file'] + " \"\n")
    else:
      FH.write("set cmd \""+ tb['dut_hdl_com'] + " " + tb['vlog_option'] + " -F ../"+ tb['dut_tb_dir'] + "/"+ tb['source_list_file'] + " \"\n")
    FH.write("puts \"\\n\\n\"\n")
    FH.write("eval $cmd\n\n")

    if mdefined( tb ,'common_pkg' ,'file'):
        mlist = ""
        if mdefined ( tb , 'common_pre_pkg','file'):
          mlist = ("../" + tb['dut_tb_dir'] + "/" + tb['common_pre_pkg']['file']+ " ")

        mlist +=("../" + tb['dut_tb_dir'] + "/" + tb['common_pkg']['file'])
        FFH =  Path(tb['dut_tb_path']+"/"+tb['source_list_file']).open("r")
        if not FFH : pexit("Exiting due to Error: can't open file: "+tb['dut_tb_path']+"/"+tb['source_list_file'])
        lines = FFH.readlines()
        FFH.close()

        found = 0
        for i in lines:
          if re.search(tb['common_pkg']['file'],i): found = 1

        if not found:
          FH.write("set cmd \"vlog " + tb['vlog_option'] + " "+ mlist + "\"\n")
          FH.write("puts \"\\n\\n\"\n")
          FH.write("eval $cmd\n\n")

    if defined(tb,'regmodel'):
      FH.write("#compile the register model package\n")
      FH.write("set cmd \"vlog " +  tb['vlog_option'] + " ../tb/regmodel/"+ tb['regmodel_file'] + "\"\n")
      FH.write("puts \"\\n\\n\"\n")
      FH.write("eval $cmd\n\n")

    tb_name = tb['top_name']
    FH.write("set tb_name "+ tb_name + "\n")
    incdir = " +incdir+../tb/include"

#  inc_path_list
#  for inc_path in inc_path_list:
#      if inc_path!="" :
#          incdir .= "+incdir+" + inc_path + " "


    if mdefined( tb ,'common_env_pkg' ,'file'):
        FFH = Path(tb['dut_tb_path']+"/"+tb['source_list_file']).open("r")
        if not FFH: pexit( "Exiting due to Error: can't open file: "+ tb['dut_tb_path'] + "+ "/tb['source_list_file'] )
        lines = FFH.readlines()
        FFH.close()
        found = 0
        for i in lines:
          if re.search(tb['common_env_pkg']['file'],i): found = 1

        if not found:
          FH.write("set cmd \"vlog " + tb['vlog_option']  + incdir + " ../tb/include/"+ tb['common_env_pkg']['file'] + "\"\n")
          FH.write("puts \"\\n\\n\"\n")
          FH.write("eval $cmd\n\n")

    FH.write("set agent_list {\\ \n")
    for agent in tb['agent_list'] :
      FH.write("    "+ agent + " \\\n")

    FH.write("}\n")
    FH.write("foreach  ele $agent_list {\n")
    FH.write("  if {$ele != \" \"} {\n")
    FH.write("    set cmd  \"vlog " + tb['vlog_option'] + incdir + "+incdir+../tb/include/$ele +incdir+../tb/\"\n")
    FH.write("    append cmd $ele \"/sv ../tb/\" $ele \"/sv/\" $ele \"_pkg.sv ../tb/\" $ele \"/sv/\" $ele \"_if.sv\"\n")
    for agent in tb['agent_list'] :
      if edef(db[agent],'split_transactors' , "YES"):
          FH.write("    append cmd \" ../tb/\" $ele \"/sv/\" $ele \"_bfm.sv\"\n")

    FH.write("    puts \"\\n\\n\"\n")
    FH.write("    eval $cmd\n")
    FH.write("  }\n")
    FH.write("}\n\n")
    if defined(tb,'syosil_scoreboard_src_path'):
        FH.write("set cmd  \"vlog " + tb['vlog_option'] +incdir+ " ../../"+ tb['syosil_scoreboard_src_path'] + " ../../"+ tb['syosil_scoreboard_src_path'] + "/pk_syoscb.sv\"\n")
        FH.write("puts \"\\n\\n\"\n")
        FH.write("eval $cmd\n\n")


    FH.write("set cmd  \"vlog " + tb['vlog_option'] + incdir + "+incdir+../tb/include/$tb_name/ +incdir+../tb/\"\n")
    FH.write("append cmd $tb_name \"/sv ../tb/\" $tb_name \"/sv/\" $tb_name \"_pkg.sv\"\n")
    FH.write("puts \"\\n\\n\"\n")
    FH.write("eval $cmd\n\n")
    FH.write("set cmd  \"vlog " + tb['vlog_option'] + incdir + "+incdir+../tb/include/$tb_name/ +incdir+../tb/\"\n")
    FH.write("append cmd $tb_name \"_test/sv ../tb/\" $tb_name \"_test/sv/\" $tb_name \"_test_pkg.sv\"\n")
    FH.write("puts \"\\n\\n\"\n")
    FH.write("eval $cmd\n\n")
    FH.write("set cmd  \"vlog " + tb['vlog_option'] + incdir  + "+incdir+../tb/include/$tb_name/ +incdir+../tb/\"\n")
    FH.write("append cmd $tb_name \"_tb/sv ../tb/\" $tb_name \"_tb/sv/\" $tb_name \"_th.sv\"\n")
    FH.write("puts \"\\n\\n\"\n")
    FH.write("eval $cmd\n\n")
    FH.write("set cmd  \"vlog " + tb['vlog_option'] + incdir  + "+incdir+../tb/include/$tb_name/ +incdir+../tb/\"\n")
    FH.write("append cmd $tb_name \"_tb/sv ../tb/\" $tb_name \"_tb/sv/\" $tb_name \"_tb.sv\"\n")
    FH.write("puts \"\\n\\n\"\n")
    FH.write("eval $cmd\n\n")
    FH.write("transcript file simulation_transcript.txt\n\n")
    
    FH.close()

    if ( sys.platform == "win32" ) or edef(tb,'os', 'WINDOWS'):

      fname = "run_gui.cmd"
      file = Path(fname)
      if not file.exists() or edef(args,'overwrite',True):
        FH = file.open("w")
        die(FH, "Exiting due to Error: can't open file: "+fname)

        FH.write("@ cd "+ tb['project'] + "/sim\n")
        FH.write("@ if %errorlevel% neq  0 (\n")
        FH.write("@   call gen_tb.cmd\n")
        FH.write("@   if %errorlevel% neq  0 (\n")
        FH.write("@     call \"" + tool + "\"  \"" + join(script_path , script_name) +"\"   )\n")
        FH.write("@   cd "+ tb['project'] + "/sim  )\n") 
        FH.write("\n")
        FH.write("call vgui.cmd\n")

        FH.close()
        os.chmod( fname, 0o755 )

      fname = "run_batch.cmd"
      file = Path(fname)
      if not file.exists() or edef(args,'overwrite',True):
        FH = file.open("w")
        die(FH, "Exiting due to Error: can't open file: "+fname)

        FH.write("@ doskey sim=vsim -c -do batch.do \n")
        FH.write("@ doskey fre=vsim -c -do batch.do \n")
        FH.write("@ cd "+ tb['project'] + "/sim\n")
        FH.write("@ if %errorlevel% neq  0 (\n")
        FH.write("@   call gen_tb.cmd\n")
        FH.write("@   if %errorlevel% neq  0 (\n")
        FH.write("@     call \"" + tool + "\"  \"" + join(script_path , script_name) +"\"   )\n")
        FH.write("@  cd "+ tb['project'] + "/sim )\n") 
        FH.write("\n")
        FH.write("cmd.exe /K vsim -c -do batch.do \n")

        FH.close()
        os.chmod( fname, 0o755 )

    if ( sys.platform != "win32" ) or edef(tb,'os', 'LINUX'):

      fname = "run_gui.sh"
      file = Path(fname)
      if not file.exists() or edef(args,'overwrite',True):
        FH = file.open("w")
        die(FH, "Exiting due to Error: can't open file: "+fname)

        FH.write("cd "+ tb['project'] + "/sim\n")
        FH.write("vgui.sh\n")

        FH.close()
        os.chmod( fname, 0o755 )

      fname = "run_batch.sh"
      file = Path(fname)
      if not file.exists() or edef(args,'overwrite',True):
        FH = file.open("w")
        die(FH, "Exiting due to Error: can't open file: "+fname)

        FH.write("cd "+ tb['project'] + "/sim\n")
        FH.write("vsim -c -do batch.do \n")

        FH.close()
        os.chmod( fname, 0o755 )


    mdir = tb['project'] + "/sim"
    file = Path(mdir + "/common.tcl")

    if not file.exists() or 1:
      FH = file.open("w")
      die(FH, "Exiting due to Error: can't open file: common.tcl")
      FH.write(f'''
proc fcompile {{}} {{
    source "compile.tcl"
    eval vopt {tb['vopt_option']} +acc +cover=sbecft top_tb -o top_tb_cov
    return false
}}

proc fgenerate {{}} {{
''')

      script_exec = str(sys.executable)  # 'py.exe' #
      script_exec = re.sub(r'\\','/',script_exec)
      allcmd = []

      if (args['all']):
        allcmd.append('--all')
      if (args['inline']):
        allcmd.append('--inline')
      for i in args['agent']:
        allcmd.append(i)

      cmd = args['scriptdir']
      cmdq = ""
      for i in allcmd:
        cmd  += " " + i
        cmdq += ",'" + i + "'"

      FH.write("    set cmd_show {" + script_exec + " -u "+ cmd + "}\n")
      FH.write("    puts \"Generation of the TB with the command ${cmd_show}\" \n")
      FH.write("    set chan [open |[list {"+ script_exec + "} {-u} {-c} {import sys;import subprocess;exit(subprocess.call")
#      FH.write("(['"+ script_exec + "', '-u'," + " '" + args['scriptdir'] +"'" + cmdq + "], cwd='../../', bufsize=0, universal_newlines=True, stdout=sys.stdout, stderr=sys.stdout))}] r]\n")
      FH.write("(['"+ script_exec + "'," + " '" + args['scriptdir'] +"'" + cmdq + "], cwd='../../', bufsize=0, universal_newlines=True, stdout=sys.stdout, stderr=sys.stdout))}] r]\n")
      FH.write('''

    while {[gets $chan line] >= 0} {
        puts $line
    }

    if {[catch {close $chan} error_msg]} {
        puts "\\nGeneration failed"
        puts ${error_msg}
        return true
    } else {
        puts "\\nGeneration finished"
        return false
    }
}

proc fexists {name} {
    expr {![catch {file lstat $name finfo}]}
}

proc fcoverage {} {

    if { [fexists ../dut/coverage_report.do ] } {

    if { [catch {source ../dut/coverage_report.do } error_msg] } {
        puts ${error_msg}
        puts "\\ncoverage_report.do failed"
        return true
    } else {
        puts "\\ncoverage_report.do finished"
''')
      FH.write("        set cmd_show {"+script_exec+" report2csv.scr}\n")
      FH.write('''        puts "For coverage_report.csv using command ${cmd_show}\\n"'''+  "\n")    
      FH.write("        if { [catch {exec \""+script_exec+"\" report2csv.scr } error_msg] } {\n")

      FH.write('''          
            puts ${error_msg}
            puts "\\ngeneration failed"
            return true
        } else {
            puts "\\ngeneration finished"
            return false
        }
        return false
    }
    }
}



proc fhelp {} {
    puts {List of fw commands:}

    puts {fhelp       - Prints this help }
    puts {fload [vsim_extra_args] }
    puts {            - Load design with correct generics for the test }
    puts {            - Optional first argument are passed as extra flags to vsim }
    puts {fuser_init  - Re-runs the user defined init file }
    puts {frun        - Run test, must do fload first }
    puts {fgenerate   - Generate the testbench files }
    puts {fcompile    - Recompiles the source files }
    puts {frestart    - Generate and recompiles the source files and restart }
    puts {            - and re-runs the simulation if the compile was successful }
    puts {fdo         - reload, do wave and restart }
    puts {frc         - recompile,reload and restart without generation }    
}

proc frun {} {
    if {[catch {_frun} failed_or_err]} {
        puts $failed_or_err
        return true
    }

    if {![is_test_suite_done]} {
        puts
        puts "Test Run Failed!"
        puts
        _frun_failure
        return true
    }

    return false
}

proc _fsource_init_files_after_load {} {
    return 0
}
proc _fsource_init_files_before_run {} {
    return 0
}

proc fload {{vsim_extra_args ""}} {

    transcript file simulation_transcript.txt
    
    set vsim_failed [catch {
        eval vsim ${vsim_extra_args} { -coverage top_tb_cov +UVM_TESTNAME=top_test +UVM_VERBOSITY=UVM_MEDIUM -voptargs=+acc -solvefaildebug -uvmcontrol=all -classdebug -quiet -t ps -onfinish stop   }
    }]

    if {${vsim_failed}} {
       puts Command 'vsim ${vsim_extra_args} top_tb +UVM_TESTNAME=top_test +UVM_VERBOSITY=UVM_MEDIUM -voptargs=+acc -solvefaildebug -uvmcontrol=all -classdebug -quiet -t ps -onfinish stop ' failed
       puts Bad flag from vsim_extra_args?
       return true
    }

    if {[_fsource_init_files_after_load]} {
        return true
    }

    global BreakOnAssertion
    set BreakOnAssertion 2

    global NumericStdNoWarnings
    set NumericStdNoWarnings 1

    global StdArithNoWarnings
    set StdArithNoWarnings 1


    return false
}

proc is_test_suite_done {} {
    return true
    set fd [open "fresults" "r"]
    set contents [read $fd]
    close $fd
    set lines [split $contents "
"]
    foreach line $lines {
        if {$line=="test_suite_done"} {
           return true
        }
    }

    return false
}


proc _frun_failure {} {
    catch {
        # tb command can fail when error comes from pli
        puts "Stack trace result from 'tb' command"
        puts [tb]
        puts
        puts "Surrounding code from 'see' command"
        puts [see]
    }
}

proc _frun {} {
    #if {[_fsource_init_files_before_run]} {
    #    return true
    #}
    #
    #proc on_break {} {
    #    resume
    #}
    #onbreak {on_break}

    set starttime [ clock seconds ]

    run -all
    set endtime [ clock seconds ]
    set runtime [ expr ($endtime - $starttime) ]
    set min  [ expr $runtime/60 ]
    set sec  [ expr ($runtime-($min*60)) ]
    puts "Runtime = $min min $sec sec ($runtime sec)"

    global guimode
    if { $guimode } { wave zoom full }
}


proc fsim_restart {} {
    transcript file simulation_transcript.txt
    restart -f
    fuser_init 0
}

proc frestart {} {
    transcript file compilation_transcript.txt
    
    if {![fgenerate]} {
      if {[fcompile]}      {quit -code 1}
      fsim_restart
      if {[frun]}          {quit -code 1}
    }
}

proc fdo {} {
    if {[fload]} {quit -code 1}
    if {[frun]}  {quit -code 1}
}

proc frc {} {
    transcript file compilation_transcript.txt

      if {[fcompile]}      {quit -code 1}
      fsim_restart
      if {[frun]}          {quit -code 1} 
}

''')
      FH.close()


    self.gen_file("gui.do","sim",'''\
source "common.tcl"
set init_start 0
set guimode true

proc fuser_init {{ init 0 }} {
    set init_start ${init}
    set file_name "wave.do"
    puts "Sourcing file ${file_name}"
    if {[catch {source ${file_name}} error_msg]} {
        puts "Sourcing ${file_name} failed"
        puts ${error_msg}
        #return true
    }
    #return 0
}

fgenerate
fcompile

if {![fload]} {
  fhelp
  fuser_init 1
  frun

  if {[fcoverage]} { 
    puts "No coverage_report.csv written! "
  } else { 
    puts "coverage_report.csv written! "
  }
 
}

''')


    self.gen_file("vgui.do","sim",'''
transcript file simulation_transcript.txt    
source "common.tcl"
set init_start 0
set guimode true

proc fuser_init {{init 0 }} {
    set init_start ${init}
    set file_name "wave.do"
    puts "Sourcing file ${file_name}"
    if {[catch {source ${file_name}} error_msg]} {
        puts "Sourcing ${file_name} failed"
        puts ${error_msg}
        #return true
    }
    #return 0
}

fhelp
fuser_init 1
frun

if {[fcoverage]} { 
  puts "No coverage_report.csv written! "
} else { 
  puts "coverage_report.csv written! "
}

''')


    self.gen_file("batch.do","sim",'''\
onerror {quit -code 1}
source "common.tcl"
set guimode false

set init_start 0

if { [fgenerate] } {quit -code 1}

if { [fcompile] }  {quit -code 1}

if { [fload] }     {quit -code 1}

if { [frun] }      {quit -code 1}

if {[fcoverage]} { 
  puts "No coverage_report.csv written! "
} else { 
  puts "coverage_report.csv written! "
}

quit -code 0

''')


    self.gen_file("compile.do","sim",'''\
onerror {quit -code 1}
source "common.tcl"
set guimode false

set init_start 0


if { [fgenerate] } {quit -code 1}

if { [fcompile] }  {quit -code 1}

quit -code 0

''')

    self.gen_file("wave.do","..",'''\
if { $init_start } {

view wave       -undock
view transcript

run 0
onerror {resume}
quietly WaveActivateNextPane {} 0

add wave -group TH     sim:/top_tb/th/*
add wave -group UUT    sim:/top_tb/th/uut/*

#add wave -group AGENT                  sim:/top_tb/th/agent_if_0/*
#add wave -group <agent-name>_if_0      sim:/top_tb/th/<agent-name>_if_0/*

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


#set wname [view wave]
set wname .main_pane.wave


_add_menu $wname controls right SystemButtonFace red   ms {configure wave -timelineunits ms}
_add_menu $wname controls right SystemButtonFace green us {configure wave -timelineunits us}
_add_menu $wname controls right SystemButtonFace blue  ns {configure wave -timelineunits ns}
_add_menu $wname controls right SystemButtonFace #cc33dd  FRestart {frestart}
_add_menu main   controls right SystemButtonFace #cc33dd  FRestart {frestart}

# WindowName Menu   MenuItem label Command
add_menu     $wname timeline
add_menuitem $wname timeline "ps" "configure wave -timelineunits ps"
add_menuitem $wname timeline "ns" "configure wave -timelineunits ns"
add_menuitem $wname timeline "us" "configure wave -timelineunits us"
add_menuitem $wname timeline "ms" "configure wave -timelineunits ms"

wave zoom full

set init_start 0

}

run 0

#add definitions after elaboration visible
#add wave -group <SystemVerilog agent>      sim:/uvm_root/uvm_test_top/m_env/m_<agent>_agent/*

''')
    mdir = tb['project'] + "/sim"
    shutil.copyfile("wave.do",mdir+"/wave.do")

    self.gen_file("vgui.cmd","sim",f'''\

vsim -c -do compile.do

if %errorlevel% equ  0 (
  vsim -c -do "run 0;quit" -coverage top_tb_cov {tb['vsim_option']} +UVM_TESTNAME=top_test {tb['uvm_cmdline']} -voptargs=+acc -solvefaildebug -uvmcontrol=all -classdebug -quiet -t ps -onfinish stop
)
if %errorlevel% equ  0 (
  questasim -do vgui.do -coverage top_tb_cov {tb['vsim_option']} +UVM_TESTNAME=top_test {tb['uvm_cmdline']} -voptargs=+acc -solvefaildebug -uvmcontrol=all -classdebug -quiet -t ps -onfinish stop
) else (
  pause
)
''')

    self.gen_file("vgui.sh","sim",f'''\

vsim -c -do compile.do
if [ $? == 0 ]
then
  vsim -c -do "run 0;quit" -coverage top_tb_cov {tb['vsim_option']} +UVM_TESTNAME=top_test {tb['uvm_cmdline']} -voptargs=+acc -solvefaildebug -uvmcontrol=all -classdebug -quiet -t ps -onfinish stop
fi
if [ $? == 0 ]
then
  vsim -gui -do vgui.do -coverage top_tb_cov {tb['vsim_option']} +UVM_TESTNAME=top_test {tb['uvm_cmdline']} -voptargs=+acc -solvefaildebug -uvmcontrol=all -classdebug -quiet -t ps -onfinish stop &
fi

''')

  def print_structure(self):
    pass

  def gen_compile_file_list(self):
    pass

  def gen_file(self,pfile,pdir,ptxt):

    mdir = self.db['top']['project'] + "/" + pdir
    mfile= mdir + "/" + pfile
    file = Path(mfile)

    if not file.exists() or ( self.db['top']['args']['overwrite'] and pdir == "sim"):
      FH = file.open("w")
      die(FH, "Exiting due to Error: can't open file: " + mfile)
      FH.write(ptxt)
      FH.close()
    os.chmod( mfile, 0o755)
    
  def gen_coverage_report_do(self):
    sfile = Path("dut/"+self.db["top"]["source_list_file"])
    if sfile.exists():
      FH = sfile.open() 
      flist = FH.readlines()
      list =[]
    
      for src in flist:
        src = re.sub('#.*$','',src)
        src = re.sub('\s*$','',src)
        src = re.sub('^\s*','',src)
        if re.search('^\s*$',src): continue
        if re.search('_pkg.vhd',src): continue
        src =  re.sub('^(\w)',r'../dut/\1',src) 
        res = re.search(r'([^/\s]+)\s*$',src)
        if res:
          file = res.group(0)
          file = re.sub(r'\.vhd','_report.txt',file)
          cmd = f"coverage report -output {file} -srcfile={src} -assert -directive -cvg -codeAll\n";
          list.append(cmd)
      
      FH.close()
      FH = Path("dut/coverage_report.do").open('w')
      FH.write("\n".join(list))
      FH.write("\ncoverage report -output report_all.txt -srcfile=* -assert -directive -cvg -codeAll\n"
      )
      FH.close
      
  def gen_report2csv_scr(self):
    sfile = Path(self.db['top']['project'] + "/sim/report2csv.scr")
    FH = sfile.open('w')
    FH.write('''
import os
import re

stmtdef = [
    'Branches'        ,       
    'Conditions'      ,
    'Expressions'     ,
    'FSM States'      ,
    'FSM Transitions' ,
    'Statements'      ,
    'Toggles'         ,
  ] 
  
clist=[]
db = {}
total = {}
   
def writedata(db):
  for name in db:
    FC.write(name+";;;")
    for sdef in stmtdef:
      if sdef in db[name]:
        FC.write(db[name][sdef])
      FC.write(";")
    if 'Total' in db[name]:  
      FC.write(db[name]['Total'])
    FC.write("\\n")

list = os.listdir('.')
for file in list:
  if re.search(r'_report.txt',file):
    clist.append(file)
clist.append('report_all.txt')
FC = open( "coverage_report.csv" ,'w')
FC.write("Source;;;")
for name in stmtdef:
  FC.write(name+";")
FC.write("Total;\\n")  

for crpt in clist:
  if crpt == 'report_all.txt':  FC.write("\\n")
  FH=open(crpt)
  lines = FH.readlines()
  target = None
  for line in lines:
    res = re.search(r"=== File:.*/(.+)",line)
    if res:
      if target != None:
        writedata(db)
      target = res.group(1)
      db = {}
      db[target] = {}
    #  print(target)
    for sdef in stmtdef:
      res = re.search(sdef+r'\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',line)
      if res:
        db[target][sdef] = res.group(4)
    res = re.search(r'TOTAL\s+(\w+)\s+COVERAGE:\s(\S+)',line)
    if res:
      total[res.group(1)] = res.group(2)
    res = re.search(r'Total.*\s+(\S+)\s*$',line)
    if res:
      if 'ASSERTION' in total:
        total['TOTAL'] = res.group(1)
      else:      
        db[target]['Total'] = res.group(1) 
  FH.close
  writedata(db)
  
FC.write("\\nTOTAL COVERAGE")
head=';'
value=';'
for i in total:
  head=head+i+";"
  value=value+total[i]+";"
FC.write(head+"\\n"+value+"\\n")
 ''')    
     
##===============================================================

  def generate_sim(self):
    tb = self.db['top']
    self.gen_sim_dir('top')

    print("Generating simulator scripts in "+ tb['project'] + "/sim\n")
    log("Generating simulator scripts in "+ tb['project'] + "/sim\n")
    self.deal_with_files_f()
	
    if edef( tb ,'tool' , "vcs") :
        self.gen_vcs_script()

    elif edef( tb ,'tool' , "ius") :
        self.gen_ius_script()

    elif edef( tb ,'tool' , "riviera") :
        self.gen_riviera_script()
        
    elif edef( tb ,'tool' , "questasim") or edef( tb ,'tool' , "questa"):
        self.gen_questa_script()
		
    else:
        self.gen_framework_script()

    self.print_structure()
    self.gen_coverage_report_do()
    self.gen_report2csv_scr()
    
    log("Code generation complete!\n")
    print ("Code generation complete!\n")

if __name__ == '__main__':

  f=open('uvm_agent.json')
  db = json.load(f)

  skeys = list(db.keys())

  skeys.sort()
  print(skeys)

  obj = SIM(db)

  print("---------------for------------------------")

  print ("generate SIM " )

  obj.generate_sim()

  print("---------------------------------------")


