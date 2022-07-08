#!/usr/bin/env python
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

''' Helper module to parse tpl file and create a database

uvm_template.py 
Version 1.0.1

'''
from header_cfg import *

import datetime
import re
import os
import sys
import json
from uvm_support import * # global functions
from pathlib     import Path

if sys.version_info[0] < 3 or sys.version_info[1] < 8:
    raise Exception("Python 3.8 or a more recent version is required.")


class uvm_template(object):
  def register(self, func):
    self.__dict__.update({func() : func})
  def __call__(self, name, *args, **kwargs):
    return getattr(self, name)(*args, **kwargs)
  def is_member(self,name):
    if name in self.__dict__:
      return 1
    else:
      return 0

template = uvm_template()



def template_prototype (ref=None,name=None):
  '''
  template_prototype generates a testbench file
  for all not defined file-parameter
  it can be used as template
  def <inc_inside_class_definition> (ref=None):
  ref is the whole database  
  '''
  #but remove ',name=None'
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
    #----------------
    #-- all you need for this generation
    agent_name = ref['agent_name']
    #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")
        text = f'''
        //-----------------------------------------------------------------
        // AGENT NAME: {agent_name}
        // PATH      : {ref["project"]+"/tb/include/"+ref['agent_name']}
        // GENERATOR : {me} for {name}
        //-----------------------------------------------------------------
'''
        INCF.write( text )
        INCF.close()

template.register(template_prototype)

#========================================================================

def driver_inc_inside_class (ref=None):
  '''
  driver_inc_inside_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
  # agent_item = ref["item"];
  
    for decl in ref["port_list"]:
      
      if decl["io"] == "in":
        align("    vif."+ decl["name"]," = req."+decl["name"] ,";")
    portlist = get_aligned();

    for decl in ref["port_list"]:
      if decl["io"] == "in":
        align("        vif."+ decl["name"]," = "+decl["rst_val"],";")
    urandom0 = get_aligned()
    
    for decl in ref["port_list"]:
      if decl["io"] == "in":
        align("        vif."+ decl["name"]," = $urandom();")
    urandom  =  get_aligned() 

  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = f'''

  time synchronization_time = 1ms;

  task run_phase(uvm_phase phase);
    `uvm_info(get_type_name(), "run_phase", UVM_HIGH)
    forever
    begin
      seq_item_port.get_next_item(req);
      `uvm_info(get_type_name(), {{"req item",req.sprint}}, UVM_HIGH)
      do_drive();
      seq_item_port.item_done();
    end
  endtask : run_phase

//=====================================================

  task do_drive();
    string seq_name;
    int    seq_var;
    string seq_mode;

    `uvm_info(get_type_name(), {{"{agent_name}_driver::do_drive task start"}}, UVM_HIGH); //UVM_HIGH);

    // If called while the reset ist activ, drive the reset input values
    if (vif.{reset} == 0) begin
        //disable xy
      reset_values();               // drive the reset values
      @(posedge vif.{reset});
        //set vif.xy
    end

      // take the controll values from the item
      seq_name = req.seq_name;
      seq_var  = req.seq_var;
      seq_mode = req.seq_mode;

      // Check which task is requested by the sequencer and call it!
      if (seq_name) case (seq_name)

'''
        align("        \"passive_reset\""         ,": passive_reset(seq_var);")
        align("        \"active_reset\""          ,": active_reset(seq_var);")
        align("        \"delay\""                 ,": delay();")
        align(f"        \"{agent_name}_init_seq\"",f": {agent_name}_init_seq();")
        align("        \"set_signals\""           ,": set_signals(seq_var);")
        text += get_aligned()
        text +=f'''        default: `uvm_error(get_type_name(), $sformatf("Illegal sequence type %s !!",seq_name))
      endcase

  endtask

//=====================================================

//function void set_mode(int value);
//  vif.mode = value;
//  //$display("mode ",vif.mode);
//endfunction

  function void set_signals(int value);

{portlist}    
  endfunction

//=====================================================
// Drive default the expected reset values or
// for test purpose random data

  function void reset_values(int rndm = 0);
    //disable clk_driver;
    if (rndm==0)
      begin
        `uvm_info(get_type_name(), {{"{agent_name}_driver::reset_values start"}}, UVM_HIGH);
        
        //vif.i_signal = 0 ;
{urandom0}        
      end
   else
      begin
      
        //vif.i_signal = $urandom();//$urandom_range(von,bis);
{urandom}        
      end

//    fork
//      begin
//        @(posedge vif.{reset});
//        //vif.reset_xyz_n = '1 ;
//        clk_driver();
//      end
//    join_none

  endfunction

//=====================================================

  task {agent_name}_init_seq();
    //@(posedge vif.{clock});
    //vif.input_signal  = req.input_signal;
    //analysis_port.write(req);
    //#wait time;
  endtask

//=====================================================

  task active_reset(int rndm = 0);
      int d = $urandom_range(20,100);  // in ns ; mindestens 1 clk , sonst funktioniertn die Property Assertion nicht !!
      int s = $urandom_range(0,20);
      @(posedge vif.{clock});
      #(s * 1ns);

      vif.{reset} = 0;
      reset_values(rndm);               // drive the reset values

      #(d * 1ns);
      vif.{reset} = 1;

      if (rndm==0) `uvm_info(get_type_name(), {{"{agent_name}_driver::reset done"}}, UVM_HIGH);
  endtask

  task passive_reset(int rndm = 0);
    disable psv_rst;
    psv_rst:
    fork
      forever 
      begin
        if (vif.{reset} == 1) @(negedge vif.{reset});
        reset_values(rndm);               // drive the reset values
        @(posedge vif.{reset});
        if (rndm==0) `uvm_info(get_type_name(), {{"{agent_name}_driver::reset done"}}, UVM_HIGH);
      end
    join_none      
  endtask

//=====================================================

  task delay();
    fork
        begin
        #200ns;
        `uvm_info(get_type_name(), {{"delay of 200ns done"}}, UVM_HIGH);
        end
    join
  endtask

//=====================================================

//  task synchronization_task();
//    //`uvm_info(get_type_name(), {{"synchronization_task started"}}, UVM_HIGH)
//    fork
//      synchronization_event : forever begin
//        #(req.synctime-20ns);  // normaly 1ms
//        @(negedge vif.{clock});
//        vif.synchronization_trigger = 1;
//        @(negedge vif.{clock});
//        vif.synchronization_trigger = 0;
//      end
//    join_none
//  endtask

//=====================================================

//  task new_task_or_req();
//    string test_name = "new_task_or_req";
//    `uvm_info(get_type_name(), {{$sformatf("{agent_name}_driver::%s start",test_name)}}, UVM_HIGH);
//
//    //@(posedge vif.{clock});
//    //vif.input_signal   = req.input_signal ;
//
//    `uvm_info(get_type_name(), {{$sformatf("{agent_name}_driver::%s finished",test_name)}}, UVM_HIGH);
//  endtask

//=====================================================
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(driver_inc_inside_class)



def driver_inc_after_class (ref=None):
  '''
  driver_inc_after_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = f'''

  task {agent_name}_driver::run_phase(uvm_phase phase);
    `uvm_info(get_type_name(), "run_phase", UVM_HIGH)
    forever
    begin
      seq_item_port.get_next_item(req);
      `uvm_info(get_type_name(), {{"req item",req.sprint}}, UVM_HIGH)
      do_drive();
      seq_item_port.item_done();
    end
  endtask : run_phase

//=====================================================

  task {agent_name}_driver::do_drive();
    string seq_name;
    int    seq_var;
    string seq_mode;
    `uvm_info(get_type_name(), {{"{agent_name}_driver::do_drive task start"}}, UVM_HIGH);

    if (vif.{reset} == 0) begin
      reset_values();               // drive the reset values
       @(posedge vif.{reset});
    end

      seq_name = req.seq_name;
      seq_var  = req.seq_var;
      seq_mode = req.seq_mode;

      case (seq_name)
        "delay"              : delay();
        "reset_test"         : reset_values(seq_var);
        "{agent_name}_init_seq"     : {agent_name}_init_seq();
        default: `uvm_error(get_type_name(), $sformatf("Illegal sequence type %s !!",seq_name))
      endcase

  endtask

//=====================================================

  function void {agent_name}_driver::reset_values(int rndm = 0);
    if (rndm==0)
      begin
        `uvm_info(get_type_name(), {{"{agent_name}_driver::reset_values start"}}, UVM_HIGH);
        //vif.input_signal = 0 ;
      end
   else
      begin
        //vif.input_signal =  $urandom();// $urandom_range(von,bis);
      end
  endfunction

//=====================================================

  task {agent_name}_driver::{agent_name}_init_seq();
    //@(posedge vif.{clock});
    //vif.input_signal  = req.input_signal;
    //analysis_port.write(req);
    //#wait time;
  endtask

//=====================================================

  task {agent_name}_driver::reset_test(int rndm = 0);
      int d = $urandom_range(20,100);  // in ns ; mindestens 1 clk , sonst funktioniertn die Property Assertion nicht !!
      int s = $urandom_range(0,20);
      @(posedge vif.{clock});
      #(s * 1ns);
      vif.{reset} = 0;
      reset_values(rndm);               // drive the reset values
      //disable synchronization_task;
      #(d * 1ns);
      vif.{reset} = 1;
      //synchronization_task();
      if (rndm==0) `uvm_info(get_type_name(), {{"{agent_name}_driver::reset done"}}, UVM_HIGH);
  endtask

//=====================================================

  task {agent_name}_driver::delay();
    fork
        begin
        #200ns;
        `uvm_info(get_type_name(), {{"{agent_name}_driver::delay done"}}, UVM_HIGH);
        end
    join
  endtask

//=====================================================

  task {agent_name}_driver::synchronization_task();
//    //`uvm_info(get_type_name(), {{"{agent_name}_driver::synchronization_task started"}}, UVM_HIGH)
//    fork
//      synchronization_event : forever begin
//        #(req.synctime-20ns);  // normaly 1ms
//        @(negedge vif.{clock});
//        vif.synchronization_trigger = 1;
//        @(negedge vif.{clock});
//        vif.synchronization_trigger = 0;
//      end
//    join_none
  endtask

//=====================================================

//  task {agent_name}_driver::new_task_or_req();
//    string test_name = "new_task_or_req";
//    `uvm_info(get_type_name(), {{ $sformatf("{agent_name}_driver::%s start",test_name)}}, UVM_HIGH);
//
//    //@(posedge vif.{clock});
//    //vif.input_signal   = req.input_signal ;
//
//
//    finfo(task_name);
//  endtask

//=====================================================
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(driver_inc_after_class)



def if_inc_before_interface (ref=None):
  '''
  if_inc_before_interface generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue
      else:
        INCF = file.open("w")

        text = f'''
        // if_inc_before_interface

        // AGENT NAME: {agent_name}
        // PATH      : {ref["project"]+"/tb/include/"+ref['agent_name']}
        // GENERATOR : {me}
'''
        INCF.write( text )
  #---------------
        text = f'''
        // if_inc_before_interface
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(if_inc_before_interface)



def if_inc_inside_interface (ref=None):
  '''
  if_inc_inside_interface generates a testbench file
  '''
  if not ref: return sys._getframe().f_code.co_name
  if defined( ref,'agent_name'):
    #----------------
    agent_name = ref['agent_name']
    agent_item = ref["item"];
    #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")
        text = f'''
  `include "uvm_macros.svh"
  import uvm_pkg::*;
  string if_name = "{agent_name}_if";

  {agent_item} resp;
  {agent_name}_monitor proxy_back_ptr;
  //event {agent_name}_end;
  //time t,t0,t1;

  int SB  = 0;
  int COV = 1;

  default clocking cp @(posedge {clock}); endclocking
  // always \@(reset) begin {reset} = reset; end
  // `AssertCon(if_name , RST_SIGNAL , @(posedge {reset}) (signal == rst_signal ) , $sformatf("signal -> reset value incorrect 0x%04h" , $sampled(signal)))

'''
        INCF.write( text )

        for decl in ref["port_list"]:
          if decl["io"] == "out":
            align ( f'''  `AssertCon(if_name , {decl["rst_name"].upper()}''',f''', @(posedge {reset}) ({decl["name"]} == {decl["rst_name"]} )''',f''', $sformatf("{decl["name"]}''',f'''-> reset value incorrect 0x%04h"''',f''', $sampled({decl["name"]})))''')
                     
        INCF.write( get_aligned())
        INCF.write( "\n\n  // Interface Ports:\n\n")
        for decl in ref["port_list"]:
          align ( "  // " , decl["logic"] , decl["name"] ,"; //" , decl["io"] , ":=" , decl["rst_val"])          
        INCF.write( get_aligned())
       
        ks='   '
        if edef (ref,"agent_coverage_enable", "NO"):
          ks="  //"
        if (agent_name == "clk_rst_gen"):
          ks="  //"
          
        align(ks+"      ")
        align(ks+"      cresp.target"," = COV",";")
        align(ks+"      ")
          
        for decl in ref["port_list"]:
          align(ks+"      cresp."+ decl["name"]," = "+decl["name"],";")
            
            
        portlist = get_aligned();
        
        
        text = f'''
  //`AssertCon (if_name, TCON_NAME, disable iff (!{reset}) PROPERTY, MSG)
        
{ks} always_comb 
{ks}   if({reset})
{ks}   begin     
{ks}     automatic {agent_item} cresp = {agent_item}::type_id::create("cresp");
{portlist}
{ks}     
{ks}     proxy_back_ptr.write(cresp);
{ks}   end  

  // always_ff @(posedge clk_50 iff reset_n or negedge reset_n)
  //   if(reset_n)
  //   begin 
  //     signal_d <= i_signal;
  //     if (signal_d == 0 && i_signal == 1)
  //       syferr = 1;
  //     else
  //       syferr = 0;      
  //   end 
  //   else
  //     syferr = 0;
  
'''
        INCF.write( text )

        INCF.close()

template.register(if_inc_inside_interface)



def monitor_inc_inside_class (ref=None):
  '''
  monitor_inc_inside_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
    agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = f'''

  {agent_item} resp;

  task run_phase(uvm_phase phase);
    `uvm_info(get_type_name(), "run_phase", UVM_HIGH)
    vif.proxy_back_ptr = this;
    do_mon();
  endtask : run_phase

  function void sample();
    //resp.input_signal  = vif.input_signal ;
    //resp.output_signal = vif.output_signal;
  endfunction : sample

  task do_mon();
    //`uvm_info(get_type_name(), "do_mon ", UVM_HIGH)
    //resp = {agent_item}::type_id::create("resp");
    //  fork vif.run(); join_none

    monitor_test_seq();

    //forever @(posedge vif.input_signal)
    //begin
    //  resp = {agent_item}::type_id::create("resp");
    //  sample();
    //  analysis_port.write(resp);
    //end

  endtask : do_mon

  function void write({agent_item} resp);
    analysis_port.write(resp);
  endfunction

  task monitor_test_seq();
    //`uvm_info(get_type_name(), $sformatf( "%s started  ",  "test " ), UVM_HIGH )
    //fork
    //    mycheck();
    //    mymeasure();
    //join_none
  endtask
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(monitor_inc_inside_class)



def monitor_inc_after_class (ref=None):
  '''
  monitor_inc_after_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
    agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = f'''
  task {agent_name}_monitor::run_phase(uvm_phase phase);
    `uvm_info(get_type_name(),  "run_phase", UVM_HIGH)
    //resp = {agent_item}::type_id::create("resp");
    do_mon();
  endtask : run_phase

  function void {agent_name}_monitor::sample();
    //resp.input_signal         = vif.input_signal         ;
    //resp.output_signal        = vif.output_signal        ;
  endfunction

  task {agent_name}_monitor::do_mon();
    `uvm_info(get_type_name(), "do_mon", UVM_HIGH)
    resp = {agent_item}::type_id::create("resp");

    monitor_test_seq();

    //forever @(posedge vif.input_signal)
    //begin
    //  resp = {agent_item}::type_id::create("resp");
    //  sample();
    //  analysis_port.write(resp);
    //end

  endtask : do_mon

//  task {agent_name}_monitor::measure();
//    fork
//      me: forever begin
//        @(posedge vif.{clock});
//        // do somethin to measure time or signals
//      end
//    join_none
//  endtask


//  task {agent_name}_monitor::mcheck();
//    fork
//      ch: forever
//      begin
//          //@(posedge vif.signal);
//          //@(posedge vif.{clock});
//          //check_time(filter);
//      end
//    join_none
//  endtask

//=====================================================

//  task {agent_name}_monitor::check_time( int mres
//    int newval = vif.output_signal;
//    {agent_name}_monitor_x : assert ( mres == newval ) else `uvm_error(get_type_name(), $sformatf( "updata error new %0d - old %0d ", newval, mres ))
//  endtask

  task {agent_name}_monitor::monitor_test_seq();
    `uvm_info(get_type_name(), $sformatf( "%s started ",  "test" ), UVM_HIGH )
    //fork
    //    mcheck();
    //    measure();
    //join_none
  endtask
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(monitor_inc_after_class)



def trans_inc_before_class (ref=None):
  '''
  trans_inc_before_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = f'''
        // trans_inc_before_class

        // AGENT NAME: {agent_name}
        // PATH      : {ref["project"]+"/tb/include/"+ref['agent_name']}
        // GENERATOR : {me}
'''
        INCF.write( text )
  #---------------
        text = f'''
        // trans_inc_before_class
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(trans_inc_before_class)



def trans_inc_inside_class (ref=None):
  '''
  trans_inc_inside_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = f'''

  string seq_name = "{agent_name}_init_seq";
  int    seq_var  = 0;
  string seq_mode = "nop";

  function void init_item();

  endfunction
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(trans_inc_inside_class)



def trans_inc_after_class (ref=None):
  '''
  trans_inc_after_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
    agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")
                                                                                    #        if defined():
                                                                                    #          INCF.write()
        if defined(ref,'trans_var')and len(ref['trans_var']) != 0:
          INCF.write("  // Transaction variables\n")

          for var in range(0,len(ref['trans_var'])):
            INCF.write("  //  "+ ref['trans_var'][var] )
            if defined(ref['trans_var_default'][var]):
                INCF.write(" = "+ ref['trans_var_default'][var] )

            INCF.write(";\n")

        if defined(ref,'trans_meta') and len(ref['trans_meta']) != 0:
          INCF.write("  // Transaction metadata\n")
          for var_decl in ref['trans_meta']:
            if defined(var_decl):
                INCF.write("  //  "+ var_decl + "\n")
            INCF.write("\n")

        text = f'''
function void {agent_item}::init_item();
endfunction :init_item

function void {agent_item}::print();
  $display("\\n{agent_item}:\\n", sprint());
endfunction

//function int {agent_item}::seq2int (string s);
//  case (s)
//    "init_seq"              : return 1;
//    default: return 0;
//  endcase
//endfunction

//function string {agent_item}::int2seq (int i);
//  case (i)
//    1  : return "init_seq"         ;
//    default: return "unknown";
//  endcase
//endfunction
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(trans_inc_after_class)



def agent_seq_inc (ref=None):
  '''
  agent_seq_inc generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
    reset_type = "passive_reset"
    if edef(ref,"agent_has_active_reset","YES"):
       reset_type = "active_reset"
    
    portlist = '' 
    for decl in ref["port_list"]:  
      if decl["io"] == "in":
        align("            req."+decl["name"]," = value%2;")
    portlist = get_aligned();

  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = f'''
`ifndef {agent_name.upper()}_SEQ_SV
`define {agent_name.upper()}_SEQ_SV

class {agent_name}_test_seq extends {agent_name}_default_seq;

  `uvm_object_utils({agent_name}_test_seq)

  string test_name;
  int    execution_mode = 'b10; // directed test
  string reset_type = "{reset_type}";  // passive_reset or active_reset
  int    short = 1;
  
  function new(string name = "");
    super.new(name);
  endfunction : new

//=====================================================

  task body();

    if ( !uvm_config_db#({agent_name}_config)::get(get_sequencer(), "", "config", m_config) )
      `uvm_error(get_type_name(), "Failed to get config object")

    if (short) linfo({{get_type_name(),":  START Seq"}},test_name);
    else       `uvm_info(get_type_name(), "{agent_name}_test_seq sequence starting", UVM_MEDIUM)

    begin

      if (!short) $info(get_type_name(),$sformatf(":\\n   {agent_name}: Start Test Sequence %s !\\n",test_name));
      case (test_name)

        "RESET_VALUES"         : reset_driver     (reset_type);
        "RESET_INIT"           : reset_init_seq   (reset_type);
        "SET_SIGNALS"          : set_signals      ("set_signals");

        default: `uvm_fatal(get_type_name(), $sformatf("Illegal test_name name %s",test_name))
      endcase

      if (!short) $info(get_type_name(),$sformatf(":\\n   {agent_name}: Test Sequence %s finished !\\n",test_name));

    end

    if (short) linfo({{get_type_name(),":  END   Seq"}},test_name);
    else       `uvm_info(get_type_name(), "{agent_name}_test_seq sequence completed\\n", UVM_MEDIUM)

  endtask : body

//==========================================================================================================

  function void sinfo (string task_name,string seq_name,int rndm = 0);
    if ( !uvm_config_db#({agent_name}_config)::get(get_sequencer(), "", "config", m_config) )
      `uvm_error(get_type_name(), "Failed to get config object")
    if (!rndm) `uvm_info(get_type_name(), $sformatf("%s started with %s", task_name , seq_name), UVM_HIGH)
  endfunction

  function void finfo (string task_name,int rndm = 0);
    if (!rndm) `uvm_info(get_type_name(), $sformatf("%s finished ", task_name ), UVM_HIGH)
  endfunction

  function void linfo(string str1="",string str2="", int le1= 35 , int le2= 45);
    string s1 = $sformatf("%0d",le1);  string s2 = $sformatf("%0d",le2);
    string format = {{"-------------   %-",s1,"s : %-",s2,"s -------------"}};
    $display(format, str1, str2 );
  endfunction

//==========================================================================================================


  task call_driver_seq(string seq_name,int rndm = 0,int seq_var = 0);
    string task_name = "call_driver_seq";
    sinfo(task_name,seq_name);

    begin
      get_item(req,seq_name);
        req.seq_var = seq_var;
      finish_item(req);
    end

    finfo(task_name);
  endtask

//=====================================================

  task reset_test(string seq_name);
    int d;
    int rndm = 0;                     // First no random enabled
    for (int i=0; i<3; i++)
      begin
        d = $urandom_range(10,100);
        reset_driver(seq_name,rndm);  // create the item and send it to driver
        rndm = 1;                     // All other with random data
        #(d*SYSTEM_CLK_PERIOD);        // time between to resets
      end

    reset_driver(seq_name,0);         // Last no random enabled
    //#(100*SYSTEM_CLK_PERIOD);
    
  endtask

//=====================================================

  task reset_init_seq(string seq_name);
    string task_name = "reset_init_seq";
    sinfo(task_name,seq_name);

    if ( "passive_reset" == seq_name)
    begin
      reset_driver(seq_name);
    end
    else
    begin
      reset_test(seq_name);
    end

    finfo(task_name);
  endtask

//=====================================================

  task get_item(output {agent_name}_item mreq, input string seq_name = "");

      mreq = {agent_name}_item::type_id::create("req");
      mreq.init_item();
      mreq.seq_name = seq_name;
      start_item(mreq);

  endtask

//=====================================================

task reset_driver(string seq_name="passive_reset", int rndm = 0);
    string task_name = "reset_driver";
    sinfo(task_name,seq_name);

      get_item(req,seq_name);
        req.seq_var  = rndm;
        if (rndm)
          req.randomize();
        else begin
          //req.xyz  = '0;
        end
      finish_item(req);

    finfo(task_name);
  endtask

//========================================================
// TEST set_signals
//

  task set_signals(string seq_name, int rndm = 0,int seq_var = 0);
    string task_name = "set_signals";
    sinfo(task_name,seq_name);

    reset_driver(reset_type);                // test start always with reset
    linfo ({{get_type_name(),":  TASK"}} , "TASK_SEQUENCE_TAG" );   

    for (int value=0; value<100; value++)
    begin
        get_item(req,seq_name);
          begin
            req.seq_var = seq_var;

{portlist}       
          end
        finish_item(req);
        #SYSTEM_CLK_PERIOD;
    end

    finfo(task_name);
  endtask

//==========================================================================================================

endclass : {agent_name}_test_seq

`endif // {agent_name.upper()}_SEQ_SV
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(agent_seq_inc)



def tb_inc_before_run_test (ref=None):
  '''
  tb_inc_before_run_test generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
#  if defined( ref,'agent_name'):
#  #----------------
#  #-- all you need for my generation
#    agent_name = ref['agent_name']
#  # agent_item = ref["item"];
#  #----------------
#  print ("==================================================================")
#    for mfile in ref["tmplt"]:
#      file = Path(ref["tmplt"][mfile])
#      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
#      dir.mkdir(parents=True, exist_ok=True)
#      if file.exists() and os.stat(file).st_size != 0 :
#        continue
#      else:
#        INCF = file.open("w")
#
#        text = f'''
#  uvm_top.finish_on_completion = 0;
#  run_test();
#  $stop;
#  $finish;
#        '''
#        INCF.write( text )
#  #---------------
#        INCF.close()

template.register(tb_inc_before_run_test)



def agent_scoreboard_inc_inside_class (ref=None):
  '''
  agent_scoreboard_inc_inside_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
    agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = f'''

  {agent_item} mon_item[$];
  {agent_item} drv_item[$];

  extern function void check_data();
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(agent_scoreboard_inc_inside_class)



def agent_scoreboard_inc_after_class (ref=None):
  '''
  agent_scoreboard_inc_after_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
    agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = f'''
function  {agent_name}_scoreboard::new(string name, uvm_component parent);
  super.new(name, parent);
endfunction : new


function void  {agent_name}_scoreboard::write(input  {agent_item} t);
  //if (m_config.scoreboard_enable)
  begin
     {agent_item} item;
    $cast(item,t.clone());
//    $display("write_mon ",item.sprint());
    write_cnt++;

    //mon_item.push_back(item);
    //check_data();

  end
endfunction : write

function void  {agent_name}_scoreboard::write_drv(input {agent_item} t);
  begin
    {agent_item} item = t;
    $cast(item,t.clone());
    write_cnt_drv++;

    //drv_item.push_back(item);

  end
endfunction : write_drv

function void {agent_name}_scoreboard::report_phase(uvm_phase phase);
    `uvm_info(get_type_name(), "Scoreboard enabled for this agent", UVM_MEDIUM)
    `uvm_info(get_type_name(), $sformatf("write_cnt = %0d ,  write_cnt_drv = %0d",write_cnt,write_cnt_drv), UVM_MEDIUM)
endfunction : report_phase

function void {agent_name}_scoreboard::check_data();
  {agent_item} mitem;
  {agent_item} ditem;

  //$display(" mom-items ",mon_item.size);
  //$display(" drv-items ",drv_item.size);
  //mitem = mon_item.pop_front();
  //ditem = drv_item.pop_front();

endfunction : check_data
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(agent_scoreboard_inc_after_class)



def common_define (ref=None):
  '''
  common_define generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = '''

//=======================================================================================================

`include "uvm_macros.svh"

`define AssertCon(IF, NAME, PROPERTY, MSG) \\
    ``NAME``_assert :  \\
        assert property (``PROPERTY) \\
        else \\
            `uvm_error(``IF,$sformatf("Concurrent Assertion  %0s  failed  >> %0s",`"NAME`",``MSG));  \\
    ``NAME``_cover :  \\
        cover property (``PROPERTY);


`define AssertIm(IF, NAME, PROPERTY, MSG) \\
  begin \\
    ``NAME``_assert :  \\
        assert (``PROPERTY) \\
        else \\
            `uvm_error(``IF, $sformatf("Immediate  Assertion  %0s  failed  >> %0s",`"NAME`",``MSG) );  \\
    ``NAME``_cover :  \\
        cover (``PROPERTY);\\
  end

'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(common_define)



def agent_copy_config_vars (ref=None):
  '''
  agent_copy_config_vars generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")

        text = f'''
  m_{agent_name}_config.sequence_start_nr = m_config.top_sequence_start_nr;
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(agent_copy_config_vars)



def top_env_scoreboard_inc_inside_class (ref=None):
  '''
  top_env_scoreboard_inc_inside_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
 
  if defined( ref,'agent_name'):
  
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue

      else:
        INCF = file.open("w")
        text = ''
        if defined ( ref , "agent_list" ):
          for ag in ref["agent_list"]:          
           for inst in ref["all_inst"][ag]:
            
            text += f'''int write_{inst}_cnt   = 0;
'''
            text += f'''//{ag}_item item_of_{inst};
'''

          text += f'''
function new(string name, uvm_component parent);
  super.new(name, parent);
endfunction : new
'''
          for ag in ref["agent_list"]:          
            for inst in ref["all_inst"][ag]:
              text += f'''
function void write_{inst}(input {ag}_item t);
  begin
    {ag}_item item_of_{ag} = t;
    $cast(item_of_{ag},t.clone());
    //$display("{inst}",item_of_{ag}.sprint());
    write_{inst}_cnt++;
  end
endfunction
'''

          text += "function void build_phase(uvm_phase phase);\n";
          for ag in ref["agent_list"]:          
            for inst in ref["all_inst"][ag]:
              text += f'''
  if (!uvm_config_db #({ag}_config)::get(this, "", "config", m_{inst}_config))
    `uvm_error(get_type_name(), "{inst} config not found")
'''

        text += '''
endfunction

function void report_phase(uvm_phase phase);
  `uvm_info(get_type_name(), "Scoreboard is enabled for this agent_instance", UVM_MEDIUM)
'''
        text += "  `uvm_info(get_type_name(), $sformatf({\"Result of Transaction counters !\\n\\n\"\n";
        for ag in ref["agent_list"]:          
           for inst in ref["all_inst"][ag]:
             if inst == "clk_rst_gen" :  continue
             text +=  "                                        ,\"\\n  write_"+ inst + "_cnt = %0d \"\n";
        text += "                                        ,\"\\n\\n\"}\n";
        text += "                                         "
        for ag in ref["agent_list"]:          
          for inst in ref["all_inst"][ag]:
            if inst == "clk_rst_gen" :  continue
            text +=  ", write_"+ inst + "_cnt";
        text +=  "\n                                        ), UVM_MEDIUM)\nendfunction\n\n";



        INCF.write( text )
  #---------------
        INCF.close()

template.register(top_env_scoreboard_inc_inside_class)



def top_env_scoreboard_inc_after_class (ref=None):
  '''
  top_env_scoreboard_inc_after_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
    sb_top     = ref['sb_top']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue
      else:
        INCF = file.open("w")

        text = f'''
//
function void {sb_top}_scoreboard::write_{agent_name}_drv(input {agent_name}_item t);
  begin
    {agent_name}_item item = t;
    $cast(item,t.clone());
    //$display("{agent_name} ",item.sprint());
    write_{agent_name}_drv_cnt++;
  end
endfunction : write_{agent_name}_drv
'''

        INCF.write( text )
  #---------------
        INCF.close()

template.register(top_env_scoreboard_inc_after_class)



def top_env_append_to_connect_phase (ref=None):
  '''
  top_env_append_to_connect_phase generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
    sb_top     = ref['sb_top']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue
      else:
        INCF = file.open("w")
        if defined ( ref , "agent_list" ):
          for ag in ref["agent_list"]:
            text = f'''
//
  m_{ag}_agent.analysis_port_drv.connect(m_{sb_top}_scoreboard.analysis_export_{ag}_drv );
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(top_env_append_to_connect_phase)



def agent_cover_inc_inside_class (ref=None):
  '''
  agent_cover_inc_inside_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if file.exists() and os.stat(file).st_size != 0 :
        continue
      else:
        INCF = file.open("w")

        text = f'''

  int COV = 1;   // module ID

  covergroup m_cov;
    option.per_instance = 1;
    // You may insert additional coverpoints here ...
    //  bins start = (0=>1);
    //  bins stop  = (1=>0);
    //  bins b1   = {{1 }};
    //  bins b2   = {{[2:4]}};
'''     
        if defined (ref,'non_local_tx_vars'):
          for field in ref['non_local_tx_vars']:
            flag = 1
            for f in ref['port_list']:
              if field == f["name"] and f["io"] == "in":
                flag = 0;
            if flag:   
               text += f'''
    cp_{field}: coverpoint m_{ref['trans_item']}.{field} {{
      bins all = {{[0:$]}};
    }}
'''

        INCF.write( text )
  #---------------
        text = f'''

  endgroup

  covergroup TCI;
    option.per_instance = 1;
'''    
        if defined (ref,'non_local_tx_vars'):
          for field in ref['non_local_tx_vars']:
            flag = 1
            for f in ref['port_list']:
              if field == f["name"] and f["io"] == "out":
                flag = 0;
            if flag:   
               text += f'''
    cp_{field}: coverpoint m_{ref['trans_item']}.{field} {{
      bins all = {{[0:$]}};
    }}
'''

        INCF.write( text )

        text = f'''
  endgroup

function new(string name, uvm_component parent);
  super.new(name, parent);
  m_is_covered = 0;
  m_cov = new();
  TCI = new();
endfunction : new


function void write(input {agent_name}_item t);
  if (m_config.coverage_enable) // && t.target == COV)
  begin
    m_item = t;
    m_cov.sample();
    TCI.sample();
    // Check coverage - could use m_cov.option.goal instead of 100 if your simulator supports it
    if ( TCI .get_inst_coverage() >= 100 
         &&  m_cov.get_inst_coverage() >= 100
       ) m_is_covered = 1;
  end
endfunction : write


function void build_phase(uvm_phase phase);
  if (!uvm_config_db #({agent_name}_config)::get(this, "", "config", m_config))
    `uvm_error(get_type_name(), "{agent_name} config not found")
endfunction : build_phase


function void report_phase(uvm_phase phase);
  if (m_config.coverage_enable)
  begin
    `uvm_info(get_type_name(), $sformatf("Coverage score = %3.1f%%", m_cov.get_inst_coverage()), UVM_MEDIUM)
    `uvm_info(get_type_name(), $sformatf("TCI Coverage score = %3.1f%%", TCI.get_inst_coverage()), UVM_MEDIUM)
  end
  else
  begin
    `uvm_info(get_type_name(), "Coverage disabled for this agent", UVM_MEDIUM)
  end
endfunction : report_phase
'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(agent_cover_inc_inside_class)



def test_inc_inside_class (ref=None):
  '''
  test_inc_inside_class generates a testbench file
  '''
  me = sys._getframe().f_code.co_name
  if not ref: return me
  if defined( ref,'agent_name'):
  #----------------
  #-- all you need for my generation
    agent_name = ref['agent_name']
  # agent_item = ref["item"];
  #----------------
    for mfile in ref["tmplt"]:
      file = Path(ref["tmplt"][mfile])
      dir = Path(re.sub(r'/[^/]*$','',ref["tmplt"][mfile]))
      dir.mkdir(parents=True, exist_ok=True)
      if not defined ( ref , "agent_list" ): return

      activ_agent = []
      for ag in ref["agent_list"]:
        if defined(ref['active_inst'], ag):
          activ_agent.append(ag)
      
      if not defined (ref,"tpl_top_active_agent"): ref["tpl_top_active_agent"] = activ_agent[0];
      
      #print (  activ_inst)
      if file.exists() and os.stat(file).st_size != 0 :
        continue
      else:
        INCF = file.open("w")
        text = "  // Start the active sequencer\n\n";
        for ag in activ_agent:
          for inst in ref["active_inst"][ag]:
            align("  " + ag + "_test_seq", inst + ";")
        text += get_aligned()    
        text += "\n  //------------------------------------------\n\n";
        align("  int",       "max = 1000;")
        #align("  string",    "top;")
        #align("  string",    "top_active_agent;")
        align("  top_config","m_config;")

        text += get_aligned()    


        text += f'''
  //==========================================
  // common.tpl
  // nested_config_objects              = yes
  // config_var = int top_test_start_nr = 1;
  // config_var = int top_test_end_nr   = 1;

  function bit check_test_nr(int test_nr);

    if (!uvm_config_db #(top_config)::get(this, "", "config", m_config))
      `uvm_error(get_type_name(), "Unable to get top_config")

    if ( m_config.top_test_start_nr <= test_nr &&  m_config.top_test_end_nr >= test_nr) return 1;
    else return 0;

  endfunction  // check_test_nr

  function void linfo(string str1="",string str2="", int le1= 35 , int le2= 45);
    string s1 = $sformatf("%0d",le1);  string s2 = $sformatf("%0d",le2);
    string format = {{"-------------   %-",s1,"s : %-",s2,"s -------------"}};
    string line;repeat(le1+le2+33) line = {{line,"-"}};
    $display("\\n",line);  
    $display(format, str1, str2 );
    $display(line);  
  endfunction

  task reset_phase (uvm_phase phase);
    super.reset_phase(phase);
    
    phase.raise_objection(this);
      `uvm_info(get_type_name(), "Wait the posedge of the {reset}", UVM_LOW)
      //@(posedge $root.top_tb.th.uut.{reset});
      #{ref["reset_time"]};
      `uvm_info(get_type_name(), "Detected posedge of the {reset}", UVM_LOW)
    phase.drop_objection(this);
    
  endtask // reset_phase

  task main_phase (uvm_phase phase);

    if (!uvm_config_db #(top_config)::get(this, "", "config", m_config))
      `uvm_error(get_type_name(), "Unable to get top_config")
    `uvm_info(get_type_name(), "start main_phase()", UVM_LOW)    
'''

  #---------------
        for ag in activ_agent:
          for inst in ref["active_inst"][ag]:
           align("    "+ inst , " = "+ ag + "_test_seq"," ::type_id::create(\"" + inst + "\");");

        text +=get_aligned();
        text += '''
    phase.raise_objection(this);

    begin

      int found = 0;
'''
        if not defined (ref,"tmplt_test_case"): ref["tmplt_test_case"] = ["RESET_VALUES"];
        for ag in activ_agent:
          align("      string  "+ ag + "_test_name [] ","= '{")
          sep = ' '
          cnt = 1;          
          for tc in ref["tmplt_test_case"]:
            align("","",sep + '"' + tc + '"'," // "+str(cnt))
            sep = ','
            cnt+=1
          align("","   };")
          align("","","")

        text +=get_aligned();
        c = "  ";
        align(c + "    max = "+ ref["tpl_top_active_agent"] + "_test_name.size ","< max ? "+ ref["tpl_top_active_agent"] + "_test_name.size"," : max;","")
        c="//"        
        for ag in activ_agent:
         align(c + "    max = "+ ag + "_test_name.size ","< max ? "+ ag + "_test_name.size"," : max;","")
         c="//"

        text +=get_aligned();
        text += '''

      for (int i = 1; i <= max ; i++) begin
'''

        for ag in activ_agent:
          for inst in ref["active_inst"][ag]:
            align("        m_config", " ."+ inst + "_config", " .checks_enable", " = 1;")

        text +=get_aligned();
        text += '''

        // Disable checks in monitor
        // if ( i == 1 ) begin
'''
        for ag in activ_agent:
          for inst in ref["active_inst"][ag]:
            align("//          m_config", " ."+ inst + "_config", " .checks_enable", " = 0;")

        text += get_aligned();
        
        if not defined (ref,"tpl_top_active_agent"): ref["tpl_top_active_agent"] = activ_agent[0];
        
        text += f'''
        //end

        if ( check_test_nr(i) ) begin
          found++;
          linfo ("{ref["dut_top"]}",{ref["tpl_top_active_agent"]}_test_name[i-1]);         
'''
        for ag in activ_agent:
          for inst in ref["active_inst"][ag]:
            align("          if (m_config."+ inst + "_config.is_active) "+ inst ," .test_name = "+ ag + "_test_name","[i-1];","")

        text +=get_aligned();
        text += '''

          fork
'''
        for ag in activ_agent:
          for inst in ref["active_inst"][ag]:
            env = inst + "_agent";
            if mdefined( ref, 'env_list_agent',ag+"_env"):# and defined( ref['env_list_agent'],"${ag}_env"}) {
              env = inst + "_env ."+ env
            align("            if (m_config."+ inst + "_config.is_active) "+ inst ," .start( m_env ."+ env ," .m_sequencer );","")

        text += get_aligned()
  #---------------
        text += f'''
          join

        end
      end

      assert(found>0) else begin
        `uvm_fatal(get_type_name(), "No test number in Range!")
        $fatal("No test number in Range!");
      end

    end

    phase.drop_objection(this);
    
    linfo("{ref["dut_top"]}","finished");
	
    $display();
    `uvm_info(get_type_name(),"all test done, leave main_phase()", UVM_LOW)
    $display();

  endtask

  function void build_phase(uvm_phase phase);

    super.build_phase (phase);

    m_env = top_env::type_id::create("m_env", this);

  endfunction : build_phase

'''
        INCF.write( text )
  #---------------
        INCF.close()

template.register(test_inc_inside_class)



if __name__ == '__main__':
  print ('template_prototype '                   , template.is_member('template_prototype'     ))

  print ('driver_inc_inside_class '              , template.is_member('driver_inc_inside_class'))
  print ('driver_inc_after_class '               , template.is_member('driver_inc_after_class'))
  print ('if_inc_before_interface '              , template.is_member('if_inc_before_interface'))
  print ('if_inc_inside_interface '              , template.is_member('if_inc_inside_interface'))
  print ('monitor_inc_inside_class '             , template.is_member('monitor_inc_inside_class'))
  print ('monitor_inc_after_class '              , template.is_member('monitor_inc_after_class'))
  print ('trans_inc_before_class '               , template.is_member('trans_inc_before_class'))
  print ('trans_inc_inside_class '               , template.is_member('trans_inc_inside_class'))
  print ('trans_inc_after_class '                , template.is_member('trans_inc_after_class'))
  print ('agent_seq_inc '                        , template.is_member('agent_seq_inc'))
  print ('tb_inc_before_run_test '               , template.is_member('tb_inc_before_run_test'))
  print ('agent_scoreboard_inc_inside_class '    , template.is_member('agent_scoreboard_inc_inside_class'))
  print ('agent_scoreboard_inc_after_class '     , template.is_member('agent_scoreboard_inc_after_class'))
  print ('common_define '                        , template.is_member('common_define'))
  print ('agent_copy_config_vars '               , template.is_member('agent_copy_config_vars'))
  print ('top_env_scoreboard_inc_inside_class '  , template.is_member('top_env_scoreboard_inc_inside_class'))
  print ('top_env_scoreboard_inc_after_class '   , template.is_member('top_env_scoreboard_inc_after_class'))
  print ('top_env_append_to_connect_phase '      , template.is_member('top_env_append_to_connect_phase'))
  print ('agent_cover_inc_inside_class '         , template.is_member('agent_cover_inc_inside_class'))
  print ('test_inc_inside_class '                , template.is_member('test_inc_inside_class'))

  try:
    f=open('uvm_db.json')
    db = json.load(f)

    skeys = list(db.keys())
    skeys.sort()

    for ag in skeys:
      if ag == 'top': continue
      print ("generate agent ", ag )
      ref = db[ag]

      for name in ('driver_inc_inside_class'             ,
                   'driver_inc_after_class'              ,
                   'if_inc_before_interface'             ,
                   'if_inc_inside_interface'             ,
                   'monitor_inc_inside_class'            ,
                   'monitor_inc_after_class'             ,
                   'trans_inc_before_class'              ,
                   'trans_inc_inside_class'              ,
                   'trans_inc_after_class'               ,
                   'agent_seq_inc'                       , 
                   'agent_scoreboard_inc_inside_class'   , 
                   'agent_scoreboard_inc_after_class'    , 
                   'agent_copy_config_vars'              , 
                   'agent_cover_inc_inside_class'         
                   ):

        tb_fname = ref['project']+"/tb/include/" + ref['agent_name'] +'/'+ ref[name]['file']
        inc_fname = ref['inc_path']+"/" + ref['agent_name'] +'/'+ ref[name]['file']
        ref['tmplt'] ={}
        ref['tmplt']['tb_fname']  = tb_fname
        ref['tmplt']['inc_fname'] = inc_fname

        template(name , ref )

      ref = db['top']

      for name in ('tb_inc_before_run_test'              ,
                   'common_define'                       ,
                   'top_env_scoreboard_inc_inside_class' ,
                   'top_env_scoreboard_inc_after_class'  ,
                   'top_env_append_to_connect_phase'     ,
                   'test_inc_inside_class'
                   ):

        tb_fname = ref['project']+"/tb/include/" + ref['agent_name'] +'/'+ ref[name]['file']
        inc_fname = ref['inc_path']+"/" + ref['agent_name'] +'/'+ ref[name]['file']
        ref['tmplt'] ={}
        ref['tmplt']['tb_fname']  = tb_fname
        ref['tmplt']['inc_fname'] = inc_fname

        template(name , ref )
  
  except:
    pass