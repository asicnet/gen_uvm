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
Version 1.0.1

"""

import datetime
import re
import os
import sys
import json
from   uvm_support   import * # global functions
from pathlib import Path

tmplt_include_file_name = "uvm_template"
if os.getenv('tmplt_include_file_name'):
  tmplt_include_file_name = os.environ['tmplt_include_file_name']

try:
  
  #from uvm_template import *
  import importlib
  #print ("Import ", tmplt_include_file_name)
  module = importlib.import_module(tmplt_include_file_name)
  names = [x for x in module.__dict__ if not x.startswith("_")]
  globals().update({k: getattr(module, k) for k in names})
  
except:

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
        
  def template_prototype (ref=None,name=None):
    """
    template_prototype generates a testbench file
    for all not defined file-parameter
    it can be used as template
    """
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
          return
        else:
          INCF = file.open("w")
          text = f"""
          //-----------------------------------------------------------------
          // AGENT NAME: {agent_name}
          // PATH      : {ref["project"]+"/tb/include/"+ref['agent_name']}
          // GENERATOR : {me} for {name}
          //-----------------------------------------------------------------
          """
          INCF.write( text )
          INCF.close()

  template = uvm_template()
  template.register(template_prototype)

from uvm_base import *

class AGENT(UVM_BASE):
  '''Class for Agent Generator
  The the data base is given to create a agent directory structure
  '''
  def __init__(self, database, verbose='info',ind=3):
      '''Define objekt variables and print debug infos
      '''
      UVM_BASE.__init__( self, database, verbose, ind)
      #self.verbose = verbose
      #self.ind=ind
      #self.db = database
      #self.tb = database['top']
      #
      #if ind:
      #    self.indstr=' '*ind
      #
      #if severityLevel(self.verbose,'debug'):
      #    class_name = self.__class__.__name__
      #    print_fc(class_name + ' created','gr')

  def gen_agent_dir(self,ag):
    agent = self.db[ag]
    log( "Reading: agent\n" + agent['agent_name'])
    dir = agent['project']+"/tb/"+agent['agent_name']
    self.dir = dir
    log( "dir: ",dir,"\n")
    makedir( dir,       )
    makedir( dir + "/sv")
    if edef (agent,'agent_has_test' , "YES"):
        makedir( dir + "/sv/test")
        makedir( dir + "/sv/test/sequences")
        makedir( dir + "/sv/test/tests")
        makedir( dir + "/sv/test/tests_sequences")

  def gen_if(self,ag):
    agent = self.db[ag]
    tb    = self.db['top']

    FH = open( self.dir + "/sv/" + agent['agent_name'] + "_if.sv" ,'w' )

    self.write_file_header(FH, agent, agent['agent_name']+"_if.sv", "Signal interface for agent "+agent['agent_name'])
    FH.write("`ifndef " + agent['agent_name'].upper() + "_IF_SV\n")
    FH.write("`define " + agent['agent_name'].upper() + "_IF_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH, "  ","common_define",tb,"dut" )

    self.insert_inc_file(FH, "  ","if_inc_before_interface",agent )

    FH.write("interface " + agent['agent_if']+"(); \n")
    FH.write("\n")
    FH.write("  timeunit      "+ tb['timeunit'] + ";\n")
    FH.write("  timeprecision "+ tb['timeprecision'] + ";\n")
    FH.write("\n")
    if defined(tb,'common_pkg'):
      if mdefined(tb,'common_pkg','name'):
        FH.write("  import "+ tb['common_pkg']['name'] + "::*;\n")
      else:
        pexit("Name of ",'common_pkg'," is not defined")
    if defined(tb,'common_env_pkg'):
      FH.write("  import "+ tb['common_env_pkg']['name'] + "::*;\n")
    FH.write("  import "+ agent['agent_name'] + "_pkg::*;\n")
    FH.write("\n")
    
    for port_decl in agent['if_port']:
        port_decl = form(port_decl)
        FH.write( port_decl +"\n")

    FH.write("\n")
    FH.write("  // You can insert properties and assertions here\n")
    FH.write("\n")

    self.insert_inc_file(FH,"  ","if_inc_inside_interface",agent)

    FH.write("endinterface : "+ agent['agent_if'] + "\n")
    FH.write("\n")
    FH.write("`endif // " + agent['agent_name'].upper() + "_IF_SV\n")
    FH.write("\n")
    FH.close()

  def gen_bfm(self,ag):

    agent = self.db[ag]
    tb    = self.db['top']
    if edef(agent,'split_transactors' ,"NO"): return

    #TEST agent['agent_inc_inside_bfm']={}
    #TEST agent['agent_inc_inside_bfm']['file'] = "blabla_bfm.sv"
    #TEST agent['agent_inc_inside_bfm']['name'] = "blabla_bfm"
    #TEST agent['agent_inc_inside_bfm']['inline'] = "0"

    FH = open( self.dir + "/sv/" + agent['agent_name'] + "_bfm.sv" ,'w' )
    self.write_file_header(FH, agent, agent['agent_name']+"_bfm.sv", "Synthesizable BFM for agent "+agent['agent_name'])

    FH.write("`ifndef " + agent['agent_name'].upper() + "_BFM_SV\n")
    FH.write("`define " + agent['agent_name'].upper() + "_BFM_SV\n")
    FH.write("\n")

    if defined(agent,'byo_interface'):
      interface_type = agent['byo_interface']
    else:
      interface_type = agent['agent_if']

    FH.write("interface "+ agent['agent_name'] + "_bfm("+ interface_type + " if_port); \n")
    FH.write("\n")
    FH.write("  timeunit      "+ tb['timeunit'] + ";\n")
    FH.write("  timeprecision "+ tb['timeprecision'] + ";\n")
    FH.write("\n")
    if defined2 (agent,'common_pkg','file'):
      FH.write("  import "+ agent['common_pkg']['name'] + "::*;\n")
    if defined2 (agent,'common_env_pkg','file'):
      FH.write("  import "+ agent['common_env_pkg']['name'] + "::*;\n" )
    FH.write("  import "+ agent['agent_name'] + "_pkg::*;\n")
    FH.write("\n")

    self.insert_inc_file(FH,"  ","agent_inc_inside_bfm",agent)

    FH.write("endinterface : "+ agent['agent_name'] + "_bfm\n")
    FH.write("\n")
    FH.write("`endif // " + agent['agent_name'].upper() + "_BFM_SV\n")
    FH.write("\n")
    FH.close()

  #end gen_bfm


  def gen_seq_item(self,ag):

    agent = self.db[ag]
    tb    = self.db['top']
    log( "AGENT-ITEM:",agent['item'],"\n")
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['item'] + ".sv")
    FH=file.open('w')
    self.write_file_header(FH,agent, agent['agent_name']+"_seq_item.sv", "Sequence item for "+ agent['agent_name'] + "_sequencer")

    FH.write("`ifndef " + agent['item'].upper() + "_SV\n")
    FH.write("`define " + agent['item'].upper() + "_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH,"","trans_inc_before_class",agent)
    if defined( tb,'common_define'):
        FH.write(f"//  `include \"{tb['common_define']['file']}\"\n\n")
    

    FH.write("class "+ agent['item'] + " extends uvm_sequence_item; \n")
    FH.write("\n")
    FH.write("  `uvm_object_utils(" + agent['item'] + ")\n")
    FH.write("\n")
    FH.write("  // To include variables in copy, compare, print, record, pack, unpack, and compare2string, define them using trans_var in file "+ agent['tpl'] + "\n")
    FH.write("  // To exclude variables from compare, pack, and unpack methods, define them using trans_meta in file "+ agent['tpl'] + "\n")
    FH.write("\n")

    if defined(agent,'trans_var'):
      if len(agent['trans_var']):
        FH.write("  // Transaction variables\n")
    p=0
    for var_decl in  agent['trans_var']:
        if agent['trans_var'+'_default'][p] != None:
          var_decl+=" = " + agent['trans_var'+'_default'][p]
        var_decl = form(var_decl)
        FH.write(var_decl+";\n")
        p+=1

    p=0

    for var_decl in  agent['trans_enum_var']:
        if agent['trans_enum_var'+'_default'][p] != None:
          var_decl+=" = " + agent['trans_enum_var'+'_default'][p]
        var_decl = form(var_decl)
        FH.write(var_decl + ";\n")
        p+=1

    FH.write("\n")

    if defined(agent,'trans_meta'):
      if len(agent['trans_meta']):
        FH.write("  // Transaction metadata\n")

    p=0
    for var_decl in  agent['trans_enum_meta']:
        if agent['trans_enum_meta'+'_default'][p] != None:
          var_decl+=" = " + agent['trans_enum_meta'+'_default'][p]
        var_decl = form(var_decl)
        FH.write(var_decl+";\n")
        p+=1

    p=0
    for var_decl in  agent['trans_meta']:
        if agent['trans_meta'+'_default'][p] != None:
          var_decl+=" = " + agent['trans_meta'+'_default'][p]
        var_decl = form(var_decl)
        FH.write(var_decl + ";\n")
        p+=1

    FH.write("\n")

    if defined(agent,'trans_var_constraint'):
        cnstr_count = 0
        for cnstr in  agent['trans_var_constraint']:
            FH.write("  constraint cnstr_count "+ cnstr + "\n")
            cnstr_count+=1

        FH.write("\n")

    FH.write("  extern function new(string name = \"\");\n")
    if not ( edef(agent,'trans_generate_methods_inside_class', "NO" )):

        if not ( edef(tb,'comments_at_include_locations', "NO" )):
            FH.write("\n  // You can remove do_copy/compare/print/record and convert2string method by setting trans_generate_methods_inside_class = no in file "+ agent['tpl'] + "\n")

        FH.write("  extern function void do_copy(uvm_object rhs);\n")
        FH.write("  extern function bit  do_compare(uvm_object rhs, uvm_comparer comparer);\n")
        FH.write("  extern function void do_print(uvm_printer printer);\n")
        FH.write("  extern function void do_record(uvm_recorder recorder);\n")
        if not defined (tb,'flag_nopack'):
            FH.write("  extern function void do_pack(uvm_packer packer);\n")
            FH.write("  extern function void do_unpack(uvm_packer packer);\n")

        FH.write("  extern function string convert2string();\n")
    FH.write("\n")


    self.insert_inc_file(FH,"  ","trans_inc_inside_class",agent)

    FH.write("endclass : "+ agent['item'] + " \n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function "+ agent['item'] + "::new(string name = \"\");\n")
    FH.write("  super.new(name);\n")
    FH.write("endfunction : new\n")
    FH.write("\n")
    FH.write("\n")
    all_tx_vars = []
    non_local_tx_vars = []
    non_meta_tx_vars = []
    enum_var_types = {}
    unpacked_bound = {}
    count = 1

    #PROC_VAR:for var_decl in  agent['trans_var']}, @{agent['trans_meta']:
    for var_decl in  agent['trans_var'] + agent['trans_enum_var']+ agent['trans_meta']:

      log("var_decl=", var_decl, "\n")
      if (count) > (len(agent['trans_var']+agent['trans_enum_var'])):
        ismeta = 1
      else:
        ismeta = 0
      count+=1

      if (  re.search(r'^const\s+',var_decl) ):
        print ("WARNING: CONSTANT TRANS_VAR "+ var_decl + " not adding to copy/compare functions!\n")
        continue

      if (  re.search(r'^static\s+',var_decl) ):
        print ("WARNING: STATIC TRANS_VAR "+ var_decl + " not adding to copy/compare functions!\n")
        continue

      if (  re.search(r'^typedef\s+',var_decl) ):
        log("Found type definition "+ var_decl + "\n")
        continue

      if (  re.search(r'^constraint\s+',var_decl) ):
        log("Found constraint "+ var_decl + "\n")
        continue

      if (  re.search(r'^\/\/',var_decl) ):
        log("Found comment "+ var_decl + "\n")
        continue


      islocal = re.search(r'local|protected',var_decl)
      stripped_decl = var_decl
      stripped_decl = re.sub(r'\[' , ' ['      , stripped_decl )   # Insert space before [
      stripped_decl = re.sub(r'\]' , '] '      , stripped_decl )   # Insert space after ]
      stripped_decl = re.sub(r'\[.+?:.+?\]' , '', stripped_decl )   # Remove array bounds of the form [a:b]
     
#      $stripped_decl =~ s/\[/ \[/g;        # Insert space before [
#      $stripped_decl =~ s/\]/\] /g;        # Insert space after ]
#      $stripped_decl =~ s/\[.+?:.+?\]//g;  # Remove array bounds of the form [a:b]
#      reduce = re.sub(r'\s*;\s*' , '' , stripped_decl )
      reduce = re.sub('\s*;.*' , '' , stripped_decl )
      reduce = re.sub(r'//.*' , ''   , reduce )
      reduce = re.sub(r'=.*' , ''   , reduce )
      
      reduce = re.sub(r'[\s]+' , '@' , reduce )

      log("stripped_decl = ", stripped_decl, "\n")
#      my @fields = split /[\s]+/, $stripped_decl; #split on space

      fields = reduce.split('@')  #split on space

      pf = 0;    # Type Variable is simplest case
      if ( re.search(r'rand|local|protected' ,fields[pf])):
          #starts with "rand", "local" or "protected" so skip
          pf+=1

      if ( re.search(r'rand|local|protected' ,fields[pf])):
          #skip "rand local", "local rand", "rand protected" or "protected rand" modifier
          pf+=1

      if ( re.search(r'signed|unsigned' ,fields[pf+1])):
          #skip signed or unsigned modifier
          pf+=1

      while ( re.search(r'^\d+:\d+',fields[pf])):
          #skip packed dimensions (i.e. bit [7:0]
          pf+=1

      pf+=1 # Should now point to the variable
      var_name =  fields[pf]

      if ( (len(fields) > pf + 1) and  re.search(r'\[', fields[pf + 1])):
          # Found unpacked array dimension (e.g. type var [N]
          # Concatenate the remaining fields in case the unpacked range contained spaces was therefore split over multiple fields
          parse = ""
          for i in range(pf + 1, len(fields)) :
              parse += fields[i]

          res = re.search(r'\[(.+)\].*', parse)
          if not res: pexit ("Exiting due to Error: ran out of steam trying to parse unpacked array dimension\n")
          unpacked_bound[var_name] = res.group(1)

      all_tx_vars.append(var_name)
      if not (islocal or ismeta or defined(unpacked_bound,var_name )):
        non_local_tx_vars.append(var_name)
      if not ismeta:
        non_meta_tx_vars.append(var_name)
      for i in agent['trans_enum_var']+agent['trans_enum_meta']:
          if ( var_decl == i ):
              enum_var_types[var_name] = fields[pf-1]
              break


      if ( ismeta ):
          log("METADATA type = "+ fields[pf-1] + ", var = "+ var_name + "\n")

      else:
          log("VARIABLE type = "+ fields[pf-1] + ", var = "+ var_name + "\n")

    #end PROC_VAR

    if not ( edef(agent,'trans_generate_methods_after_class' , "NO" )):

      if not ( edef(tb,'comments_at_include_locations', "NO" )):
        FH.write("// You can remove do_copy/compare/print/record and convert2string method by setting trans_generate_methods_after_class = no in file "+ agent['tpl'] + "\n\n")

      FH.write("function void "+ agent['item'] + "::do_copy(uvm_object rhs);\n")
      FH.write("  "+ agent['item'] + " rhs_;\n")
      FH.write("  if (!$cast(rhs_, rhs))\n")
      FH.write("    `uvm_fatal(get_type_name(), \"Cast of rhs object failed\")\n")
      FH.write("  super.do_copy(rhs);\n")

      for field in  all_tx_vars :
          align("  "+ field , " = rhs_."+ field + ";")
      gen_aligned(FH)

      FH.write("endfunction : do_copy\n")
      FH.write("\n")
      FH.write("\n")
      FH.write("function bit "+ agent['item'] + "::do_compare(uvm_object rhs, uvm_comparer comparer);\n")
      FH.write("  bit result;\n")
      FH.write("  " + agent['item'] + " rhs_;\n")
      FH.write("  if (!$cast(rhs_, rhs))\n")
      FH.write("    `uvm_fatal(get_type_name(), \"Cast of rhs object failed\")\n")
      FH.write("  result = super.do_compare(rhs, comparer);\n")
      for field in non_meta_tx_vars :
          if defined( unpacked_bound,field ):
              align(" ","for (int i = 0; i < "+ unpacked_bound[field] + "; i++)", "", "")
              align(" ","  result &= comparer.compare_field(\""+ field + "\", "+ field + "[i], ", "rhs_."+ field + "[i], ", "$bits("+ field + "[i]));")

          else :
              align(" ","result &= comparer.compare_field(\""+ field + "\", "+ field + ", ", "rhs_."+ field + ", ", "$bits("+ field + "));")


      gen_aligned(FH)

      FH.write("  return result;\n")
      FH.write("endfunction : do_compare\n")
      FH.write("\n")
      FH.write("\n")
      FH.write("function void "+ agent['item'] + "::do_print(uvm_printer printer);\n")
      FH.write("  if (printer.knobs.sprint == 0)\n")
      FH.write("    `uvm_info(get_type_name(), convert2string(), UVM_MEDIUM)\n")
      FH.write("  else\n")
      FH.write("    printer.m_string = convert2string();\n")
      FH.write("endfunction : do_print\n")
      FH.write("\n")
      FH.write("\n")
      FH.write("function void "+ agent['item'] + "::do_record(uvm_recorder recorder);\n")
      FH.write("  super.do_record(recorder);\n")
      FH.write("  // Use the record macros to record the item fields:\n")
      for field in  all_tx_vars:
          if defined(unpacked_bound,field ):
              align(" ","for (int i = 0; i < "+ unpacked_bound[field] + "; i++)\n", "", "")
              align(" ","  `uvm_record_field({\""+ field +"_\",$sformatf(\"%0d\",i)}, ",  field +"[i])", "")
          else:
              align(" ","`uvm_record_field(\""+ field +"\", ",  field +")", "")
      gen_aligned(FH)

      FH.write("endfunction : do_record\n")
      FH.write("\n")
      FH.write("\n")

      if not defined(tb,'flag_nopack') :

          FH.write("function void "+ agent['item'] + "::do_pack(uvm_packer packer);\n")
          FH.write("  super.do_pack(packer);\n")
          for field in non_meta_tx_vars :
              if defined(unpacked_bound,field ):
                  align(" ","`uvm_pack_sarray("+ field +")", "", "")

              elif defined(enum_var_types,field ) :
                  align(" ","`uvm_pack_enum("+ field +")", "", "")

              else :
                  align(" ","`uvm_pack_int("+ field +")", "", "")


          gen_aligned(FH)
          FH.write("endfunction : do_pack\n")
          FH.write("\n")
          FH.write("\n")


          FH.write("function void "+ agent['item'] + "::do_unpack(uvm_packer packer);\n")
          FH.write("  super.do_unpack(packer);\n")
          for field in non_meta_tx_vars :
              if defined(unpacked_bound,field ) :
                  align("  `uvm_unpack_sarray("+ field +")","","")

              elif defined(enum_var_types,field ):
                  align(" ","`uvm_unpack_enum("+ field +", ", enum_var_types[field] + ")", "")

              else :
                  align(" ","`uvm_unpack_int("+ field +")", "", "")

          gen_aligned(FH)

          FH.write("endfunction : do_unpack\n")
          FH.write("\n")
          FH.write("\n")


      FH.write("function string "+ agent['item'] + "::convert2string();\n")
      FH.write("  string s;\n")
      FH.write("  $sformat(s, \"%s\\n\", super.convert2string());\n")
      if ( len(all_tx_vars) > 0 ) :
          FH.write("  $sformat(s, {\"%s\\n\",\n")
          l = len(all_tx_vars) -1
          for i in  range(0,l+1):
              field = all_tx_vars[i]
              if ( i < l ): terminator =  ","
              else :        terminator = "},"
              if defined ( unpacked_bound,field):
                formatting = "%p"
              elif defined ( enum_var_types,field ):
                formatting = "%s"
              else:
                formatting = "'h%0h  'd%0d"
              align(" ","  \""+ field  , "= "+ formatting + "\\n\""+ terminator , "")

          gen_aligned(FH)

          FH.write("    get_full_name(),")
          for i in  range(0,l+1):
              field = all_tx_vars[i]
              if defined(unpacked_bound,field ):
                  FH.write(" "+ field )

              elif defined(enum_var_types,field ) :
                  FH.write(" "+ field +".name")

              else :
                  FH.write(" "+ field +", "+ field )

              if ( i < l ): terminator =  ","
              else :        terminator = ");"

              FH.write(terminator)

      FH.write("\n")
      FH.write("  return s;\n")
      FH.write("endfunction : convert2string\n")
      FH.write("\n")
      FH.write("\n")

    if not defined(agent,'trans_inc_after_class') : agent['trans_inc_after_class'] = {}
    agent['trans_inc_after_class']['agent_item'] = agent['item']

    self.insert_inc_file(FH,"","trans_inc_after_class",agent)

    FH.write("`endif // " + agent['item'].upper() + "_SV\n")
    FH.write("\n")
    FH.close()

    agent['all_tx_vars']       = all_tx_vars
    agent['non_local_tx_vars'] = non_local_tx_vars
    agent['non_meta_tx_vars']  = non_meta_tx_vars
    agent['enum_var_types']    = enum_var_types
    agent['unpacked_bound']    = unpacked_bound
  #end gen_seq_item

    #print ("============", agent['all_tx_vars']       )
    #print ("============", agent['non_local_tx_vars'] )
    #print ("============", agent['non_meta_tx_vars']  )
    #print ("============", agent['enum_var_types']    )
    #print ("============", agent['unpacked_bound']    )


  def gen_config(self,ag):

    agent = self.db[ag]
    tb    = self.db['top']
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_config.sv")
    FH=file.open('w')
    self.write_file_header(FH,agent, agent['agent_name']+"_config.sv", "Configuration for agent "+ agent['agent_name'] )

    FH.write("`ifndef " + agent['agent_name'].upper()+ "_CONFIG_SV\n")
    FH.write("`define " + agent['agent_name'].upper()+ "_CONFIG_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH,"","agent_config_inc_before_class",agent)

    FH.write("class "+ agent['agent_name'] + "_config extends uvm_object;\n")
    FH.write("\n")
    FH.write("  // Do not register config class with the factory\n")
    FH.write("\n")

    if edef( agent,'split_transactors', "YES" ):
      interface_type = agent['agent_name'] + "_bfm"
    elif defined (agent,'byo_interface'):
      interface_type = agent['byo_interface']
    else :
      interface_type = agent['agent_name'] + "_if"

    align(" ","virtual "+ interface_type , "vif;", "")
    align()
    if defined ( agent , 'reg_access_mode'):
      align(" ",agent['reg_access_block_type'], "regmodel;", "")

    align(" ","uvm_active_passive_enum", "is_active = UVM_ACTIVE;", "")
    align(" ","bit", "coverage_enable;", "")
    align(" ","bit", "checks_enable;", "")
    align(" ","bit", "scoreboard_enable;", "")
    align(" ","int", "build_in_bug;", "");
    align(" ","int", "execution_mode;", "");
    align(" ","string", "if_name;", "");

    gen_aligned(FH)

    FH.write("\n")
    if not ( defined( agent,'config_var') and len(agent['config_var']) ) :
      FH.write("  // You can insert variables here by setting config_var in file "+ agent['tpl'] + "\n")

    p=0
    for var_decl in  agent['config_var']:
        if agent['config_var'+'_default'][p] != None:
          var_decl+=" = " + agent['config_var'+'_default'][p]
        var_decl = form(var_decl)
        FH.write(var_decl+";\n")
        p+=1

    FH.write("\n")
    if not ( edef(agent,'agent_config_generate_methods_inside_class' , "NO" )):
        if not ( edef(tb,'comments_at_include_locations',"NO")):
            FH.write("  // You can remove new by setting agent_config_generate_methods_inside_class = no in file "+ agent['tpl'] + "\n\n")

        FH.write("  extern function new(string name = \"\");\n")
        FH.write("\n")

    self.insert_inc_file(FH,"  ","agent_config_inc_inside_class",agent)
    FH.write("endclass : " + agent['agent_name'] + "_config \n")
    FH.write("\n")
    FH.write("\n")

    if not ( edef(agent,'agent_config_generate_methods_after_class',"NO")):
        if not ( edef(tb,'comments_at_include_locations',"NO")) :
            FH.write("// You can remove new by setting agent_config_generate_methods_after_class = no in file "+ agent['tpl'] + "\n\n")

        FH.write("function "+ agent['agent_name'] + "_config::new(string name = \"\");\n")
        FH.write("  super.new(name);\n")
        FH.write("endfunction : new\n")
        FH.write("\n")
        FH.write("\n")

    self.insert_inc_file(FH,"","agent_config_inc_after_class",agent)
    FH.write("`endif // " + agent['agent_name'].upper()+ "_CONFIG_SV\n")
    FH.write("\n")
    FH.close()




  def gen_driver (self,ag):

    agent = self.db[ag]
    tb    = self.db['top']
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_driver.sv")
    FH=file.open('w')
    self.write_file_header(FH,agent, agent['agent_name']+"_driver.sv", "Driver for agent "+ agent['agent_name'] )

    FH.write("`ifndef " + agent['agent_name'].upper()+ "_DRIVER_SV\n")
    FH.write("`define " + agent['agent_name'].upper()+ "_DRIVER_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH,"","driver_inc_before_class",agent)

    FH.write("class "+ agent['agent_name'] + "_driver extends uvm_driver #("+ agent['item'] + ");\n")
    FH.write("\n")
    FH.write("  `uvm_component_utils(" + agent['agent_name'] + "_driver)\n")
    FH.write("\n")

    if edef( agent,'split_transactors', "YES" ) :
      interface_type = agent['agent_name'] + "_bfm"
    elif defined ( agent , 'byo_interface'):
      interface_type = agent['byo_interface']
    else :
      interface_type = agent['agent_if']

    FH.write("  virtual "+ interface_type + " vif;\n")
    FH.write("\n")
    FH.write("  "+ agent['agent_name'] + "_config     m_config;\n")
    FH.write("\n")
    if edef(agent,'agent_generate_scoreboard_class' , "YES") :
        FH.write("\n")
        FH.write("  uvm_analysis_port #("+ agent['item'] + ") analysis_port;\n")
        FH.write("\n")

    FH.write("  extern function new(string name, uvm_component parent);\n")
    if defined ( agent , 'agent_driv_inc'): check_file(agent['project']+"/tb/include/"+ agent['agent_name'] + "/"+ agent['agent_driv_inc'] )
    if defined ( agent , 'agent_driv_inc') and \
          path(agent['project'] + "/tb/include/" + agent['agent_name'] + "/" + agent['agent_driv_inc'] ).exists()  :
        FH.write("\n")
        FH.write("  // Methods run_phase and do_drive generated by setting driver_inc in file "+ agent['tpl'] + "\n")
        FH.write("  extern task run_phase(uvm_phase phase);\n")
        FH.write("  extern task do_drive();\n")
        for mdir in  ( agent['project'] + "/tb/include/" , agent['inc_path'] ) :
            file = Path(mdir + "/" + agent['agent_name'] +"/"+ agent['agent_driv_inc'])
            if not( file.exists() and os.stat(file).st_size != 0) :
                IFH = file.open("w")
                IFH.write( "task "+ agent['agent_name'] + "_driver::do_drive();\n\n")
                IFH.write( "    `uvm_info(get_type_name(), \"do_drive run for 1 us\", UVM_MEDIUM)\n")
                IFH.write( "    #1us;\n\n")
                IFH.write( "endtask : do_drive\n")
                IFH.close()
    FH.write("\n")

    self.insert_inc_file(FH,"  ","driver_inc_inside_class",agent)

    FH.write("endclass : " + agent['agent_name'] + "_driver \n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function "+ agent['agent_name'] + "_driver::new(string name, uvm_component parent);\n")
    FH.write("  super.new(name, parent);\n")
    if edef(agent,'agent_generate_scoreboard_class',"YES") :
        FH.write("  analysis_port = new(\"analysis_port\", this);\n")

    FH.write("endfunction : new\n")
    FH.write("\n")
    FH.write("\n")
    if defined ( agent , 'agent_driv_inc') and Path(agent['project'] + "/tb/include/" + agent['agent_name'] + "/"+ agent['agent_driv_inc']  ).exists():

        FH.write("task " + agent['agent_name'] + "_driver::run_phase(uvm_phase phase);\n")
        FH.write("  `uvm_info(get_type_name(), \"run_phase\", UVM_HIGH)\n")
        FH.write("\n")
        FH.write("  forever\n")
        FH.write("  begin\n")
        FH.write("    seq_item_port.get_next_item(req);\n")
        FH.write("      `uvm_info(get_type_name(), {\"req item\\n\",req.sprint}, UVM_HIGH)\n")
        FH.write("    do_drive();\n")
        FH.write("    seq_item_port.item_done();\n")
        agent_clock = agent['agent_clock_array'][0]
        if ( not agent_clock or agent_clock == "" ) :
            FH.write("    # 10ns;\n")

        FH.write("  end\n")
        FH.write("endtask : run_phase\n")
        FH.write("\n")
        FH.write("\n")

        self.insert_inc_file(FH,"","driver_inc",agent)

    self.insert_inc_file(FH,"","driver_inc_after_class",agent)

    FH.write("`endif // " + agent['agent_name'].upper()+ "_DRIVER_SV\n")
    FH.write("\n")
    FH.close()

  def gen_monitor(self,ag): pass


  def gen_monitor (self,ag):

    agent = self.db[ag]
    tb    = self.db['top']
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_monitor.sv")
    FH=file.open('w')
    self.write_file_header(FH, agent, agent['agent_name']+"_monitor.sv", "Monitor for agent "+ agent['agent_name'] )

    FH.write("`ifndef " + agent['agent_name'].upper()+ "_MONITOR_SV\n")
    FH.write("`define " + agent['agent_name'].upper()+ "_MONITOR_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH,"","monitor_inc_before_class",agent)

    FH.write("class "+ agent['agent_name'] + "_monitor extends uvm_monitor;\n")
    FH.write("\n")
    FH.write("  `uvm_component_utils(" + agent['agent_name'] + "_monitor)\n")
    FH.write("\n")

    if edef( agent ,'split_transactors' , "YES" ):
      interface_type = agent['agent_name'] + "_bfm"

    elif defined ( agent , 'byo_interface'):
      interface_type = agent['byo_interface']

    else:
      interface_type = agent['agent_if']

    FH.write("  virtual "+ interface_type + " vif;\n")
    FH.write("\n")
    FH.write("  "+ agent['agent_name'] + "_config     m_config;\n")
    FH.write("\n")
    FH.write("  uvm_analysis_port #("+ agent['item'] + ") analysis_port;\n")
    FH.write("\n")
    if defined ( agent , 'agent_mon_inc'):
        check_file( agent['project'] + "/tb/include/"+ agent['agent_name'] + "/"+ agent['agent_mon_inc'] )
    if defined ( agent , 'agent_mon_inc') and Path(agent['project'] + "/tb/include/"+ agent['agent_name'] + "/" + agent['agent_mon_inc']).exists():
        FH.write("  "+ agent['item'] + " "+ m_agent['trans_item'] + ";\n")
        FH.write("\n")

    FH.write("  extern function new(string name, uvm_component parent);\n")
    if defined ( agent , 'agent_mon_inc') and Path(agent['project'] + "/tb/include/"+ agent['agent_name'] + "/"+ agent['agent_mon_inc']).exists():
        FH.write("\n")
        FH.write("  // Methods run_phase, and do_monitor generated by setting monitor_inc in file "+ agent['tpl'] + "\n")
        FH.write("  extern task run_phase(uvm_phase phase);\n")
        FH.write("  extern task do_monitor();\n")
        for mdir in  ( agent['project'] + "/tb/include/" , tb['inc_path'] + "/"):
            file = mdir +  agent['agent_name'] + "/"+ agent['agent_mon_inc']
            if file.exists() and os.stat(file).st_size != 0 :
                IFH = file.open("w")
                FH.write("task "+ agent['agent_name'] + "_monitor::do_monitor();\n\n")
                FH.write("    `uvm_info(get_type_name(), \"do_monitor run for 1 us\", UVM_MEDIUM)\n")
                FH.write("    #1us;\n\n")
                FH.write("endtask : do_monitor\n")
                IFH.close()

    FH.write("\n")
    #agent['monitor_inc_inside_class']['agent_item'] = agent['item']

    self.insert_inc_file(FH,"  ","monitor_inc_inside_class",agent)

    FH.write("endclass : " + agent['agent_name'] + "_monitor \n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function "+ agent['agent_name'] + "_monitor::new(string name, uvm_component parent);\n")
    FH.write("  super.new(name, parent);\n")
    FH.write("  analysis_port = new(\"analysis_port\", this);\n")
    FH.write("endfunction : new\n")
    FH.write("\n")
    FH.write("\n")
    if defined ( agent , 'agent_mon_inc') and Path( agent['project'] + "/tb/include/"+ agent['agent_name'] + agent['agent_mon_inc']).exists():
        FH.write("task "+ agent['agent_name'] + "_monitor::run_phase(uvm_phase phase);\n")
        FH.write("  `uvm_info(get_type_name(), \"run_phase\", UVM_HIGH)\n")
        FH.write("\n")
        FH.write("  "+ m_agent['trans_item'] + " = "+ agent['item'] + "::type_id::create(\ "+ m_agent['trans_item'] + " + \");\n")
        FH.write("  do_monitor();\n")
        FH.write("endtask : run_phase\n")
        FH.write("\n")
        FH.write("\n")

        self.insert_inc_file(FH,"","monitor_inc",agent)

    #agent['monitor_inc_after_class']['agent_item'] = agent['item']

    self.insert_inc_file(FH,"","monitor_inc_after_class",agent)

    FH.write("`endif // " + agent['agent_name'].upper()+ "_MONITOR_SV\n")
    FH.write("\n")
    FH.close()

  def gen_sequencer(self,ag):

    agent = self.db[ag]
    tb    = self.db['top']
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_sequencer.sv")
    FH=file.open('w')
    self.write_file_header(FH, agent, agent['agent_name']+"_sequencer.sv", "Sequencer for agent "+ agent['agent_name'] )


    FH.write("`ifndef " + agent['agent_name'].upper()+ "_SEQUENCER_SV\n")
    FH.write("`define " + agent['agent_name'].upper()+ "_SEQUENCER_SV\n")
    FH.write("\n")
    if edef(agent, 'uvm_seqr_class' ,"YES"):

        self.insert_inc_file(FH,"","sequencer_inc_before_class",agent)

        FH.write("class "+ agent['agent_name'] + "_sequencer extends uvm_sequencer #("+ agent['item']+");\n")
        FH.write("\n")
        FH.write("  `uvm_component_utils(" + agent['agent_name'] + "_sequencer)\n")
        FH.write("\n")
        FH.write("  extern function new(string name, uvm_component parent);\n")
        FH.write("\n")

        self.insert_inc_file(FH,"  ","sequencer_inc_inside_class",agent)

        FH.write("endclass : " + agent['agent_name'] + "_sequencer \n")
        FH.write("\n")
        FH.write("\n")
        FH.write("function "+ agent['agent_name'] + "_sequencer::new(string name, uvm_component parent);\n")
        FH.write("  super.new(name, parent);\n")
        FH.write("endfunction : new\n")
        FH.write("\n")
        FH.write("\n")

        self.insert_inc_file(FH,"","sequencer_inc_after_class",agent)

        FH.write("\n")
        FH.write("typedef "+ agent['agent_name'] + "_sequencer "+ agent['agent_name'] + "_sequencer_t;\n")

    else:
        FH.write("// Sequencer class is specialization of uvm_sequencer\n")
        FH.write("typedef uvm_sequencer #("
          + agent['item'] + ") " + agent['agent_name']
          + "_sequencer_t;\n")

    FH.write("\n")
    FH.write("\n")
    FH.write("`endif // " + agent['agent_name'].upper()+ "_SEQUENCER_SV\n")
    FH.write("\n")
    FH.close()

  def gen_cov(self,ag):

    agent = self.db[ag]
    tb    = self.db['top']
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_coverage.sv")
    FH=file.open('w')
    self.write_file_header(FH, agent, agent['agent_name']+"_coverage.sv", "Coverage for agent "+ agent['agent_name'] )

    FH.write("`ifndef " + agent['agent_name'].upper()+ "_COVERAGE_SV\n")
    FH.write("`define " + agent['agent_name'].upper()+ "_COVERAGE_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH,"","agent_cover_inc_before_class",agent)

    FH.write("class "+ agent['agent_name'] + "_coverage extends uvm_subscriber #("+ agent['item'] + ");\n")
    FH.write("\n")
    FH.write("  `uvm_component_utils(" + agent['agent_name'] + "_coverage)\n")
    FH.write("\n")
    align("  "+ agent['agent_name'] + "_config ", "m_config;", "")
    align("  bit ",                               "m_is_covered;", "")
    align("  "+ agent['item'] ,                   "m_" + agent['trans_item'] + ";", "")
    gen_aligned(FH)
    FH.write("\n")
    #if include file for coverage collector exists, pull it in here, otherwise
    #create covergroup and coverpoints with default bins

    if defined (agent, 'agent_cover_inc'):
        covfile = Path(agent['project'] + "/tb/include/"+ agent['agent_name'] + "/"+ agent['agent_cover_inc'] )
        if  covfile.exists():
            FH_COV = covfile.open()
            for i in FH_COV.readline(): cov_inc += i
            #check that file contains covergroup named "m_cov"
            if not re.search(r'covergroup\s+m_cov(\s|;)', cov_inc):
                warning_prompt("COVERGROUP \"m_cov\" MUST BE DEFINED IN "+ agent['agent_cover_inc'] )

        self.insert_inc_file(FH,"  ","agent_cover_inc",agent)

    else:
        if not edef( agent, 'agent_cover_generate_methods_inside_class',"NO"):
            if not edef(tb,'comments_at_include_locations',"NO"):
                FH.write("  // You can replace covergroup m_cov by setting agent_cover_inc in file "+ agent['tpl'] + "\n")
                FH.write("  // or remove covergroup m_cov by setting agent_cover_generate_methods_inside_class = no in file "+ agent['tpl'] + "\n\n")

            FH.write("  covergroup m_cov;\n")
            FH.write("    option.per_instance = 1;\n")
            FH.write("    // You may insert additional coverpoints here ...\n")
            FH.write("\n")
            for field in  agent['non_local_tx_vars']:
#                    FH.write("    cp_['i']: coverpoint m_agent['trans_item'].$['tmp'];\n")
#                FH.write("    cp_"+ field + ": coverpoint "+ agent['trans_item'] + "."+ field + ";\n")
                FH.write("    cp_"+ field + ": coverpoint m_"+ agent['trans_item'] + "."+ field + ";\n")
                FH.write("    //  Add bins here if required\n")
                FH.write("\n")

            FH.write("  endgroup\n")
            FH.write("\n")


    if not edef(agent, 'agent_cover_generate_methods_inside_class',"NO"):
        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("  // You can remove new, write, and report_phase by setting agent_cover_generate_methods_inside_class = no in file "+ agent['tpl'] + "\n\n")
        FH.write("  extern function new(string name, uvm_component parent);\n")
        FH.write("  extern function void write(input " + agent['item'] + " t);\n")
        FH.write("  extern function void build_phase(uvm_phase phase);\n")
        FH.write("  extern function void report_phase(uvm_phase phase);\n")
        FH.write("\n")

    self.insert_inc_file(FH,"  ","agent_cover_inc_inside_class",agent)

    FH.write("endclass : " + agent['agent_name'] + "_coverage \n")
    FH.write("\n")
    FH.write("\n")
    if not edef(agent,'agent_cover_generate_methods_after_class',"NO"):
        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("// You can remove new, write, and report_phase by setting agent_cover_generate_methods_after_class = no in file "+ agent['tpl'] + "\n\n")
        FH.write("function "+ agent['agent_name'] + "_coverage::new(string name, uvm_component parent);\n")
        FH.write("  super.new(name, parent);\n")
        FH.write("  m_is_covered = 0;\n")
        FH.write("  m_cov = new();\n")
        FH.write("endfunction : new\n")
        FH.write("\n")
        FH.write("\n")
        FH.write("function void "+ agent['agent_name'] + "_coverage::write(input "+ agent['item'] + " t);\n")
        FH.write("  if (m_config.coverage_enable)\n")
        FH.write("  begin\n")
        FH.write("    m_"+ agent['trans_item'] + " = t;\n")
        FH.write("    m_cov.sample();\n")
        FH.write("    // Check coverage - could use m_cov.option.goal instead of 100 if your simulator supports it\n")
        FH.write("    if (m_cov.get_inst_coverage() >= 100) m_is_covered = 1;\n")
        FH.write("  end\n")
        FH.write("endfunction : write\n")
        FH.write("\n")
        FH.write("\n")
        FH.write("function void "+ agent['agent_name'] + "_coverage::build_phase(uvm_phase phase);\n")
        FH.write("  if (!uvm_config_db #("+ agent['agent_name'] + "_config)::get(this, \"\", \"config\", m_config))\n")
        FH.write("    `uvm_error(get_type_name(), \""+ agent['agent_name'] + " config not found\")\n")
        FH.write("endfunction : build_phase\n")
        FH.write("\n")
        FH.write("\n")
        FH.write("function void "+ agent['agent_name'] + "_coverage::report_phase(uvm_phase phase);\n")
        FH.write("  if (m_config.coverage_enable)\n")
        FH.write("    `uvm_info(get_type_name(), $sformatf(\"Coverage score = %3.1f%%\", m_cov.get_inst_coverage()), UVM_MEDIUM)\n")
        FH.write("  else\n")
        FH.write("    `uvm_info(get_type_name(), \"Coverage disabled for this agent\", UVM_MEDIUM)\n")
        FH.write("endfunction : report_phase\n")
        FH.write("\n")
        FH.write("\n")

    self.insert_inc_file(FH,"","agent_cover_inc_after_class",agent)

    FH.write("`endif // " + agent['agent_name'].upper()+ "_COVERAGE_SV\n")
    FH.write("\n")
    FH.close()

  def gen_sb(self,ag):
    agent = self.db[ag]
    tb    = self.db['top']
    if edef(agent,'agent_generate_scoreboard_class' ,"NO"): return
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_scoreboard.sv")
    FH=file.open('w')
    self.write_file_header(FH, agent, agent['agent_name']+"_scoreboard.sv", "Scoreboard for agent "+ agent['agent_name'] )

    FH.write("`ifndef " + agent['agent_name'].upper()+ "_SCOREBOARD_SV\n")
    FH.write("`define " + agent['agent_name'].upper()+ "_SCOREBOARD_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH,"","agent_scoreboard_inc_before_class",agent)

    FH.write("class "+ agent['agent_name'] + "_scoreboard extends uvm_subscriber #("+ agent['item'] + ");\n")
    FH.write("\n")
    FH.write("  `uvm_component_utils(" + agent['agent_name'] + "_scoreboard)\n")
    FH.write("\n")
    FH.write("  `uvm_analysis_imp_decl(_drv)\n")
    FH.write("  uvm_analysis_imp_drv #("+ agent['item'] + ","+ agent['agent_name'] + "_scoreboard) analysis_export_drv = new (\"analysis_export_drv\",this); \n")
    FH.write("\n")
    align("  "+ agent['agent_name'] + "_config ", "m_config;", "")
    align("  "+ agent['item'] + " ", "m_"+ agent['trans_item'] + ";\n", "")
    gen_aligned(FH)
    FH.write("\n")
    FH.write("  int write_cnt     = 0;\n")
    FH.write("  int write_cnt_drv = 0;\n")
    FH.write("\n")
    if not edef(agent,'agent_scoreboard_generate_methods_inside_class',"NO"):
        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("  // You can remove new, write, and report_phase by setting agent_scoreboard_generate_methods_inside_class = no in file "+ agent['tpl'] + "\n\n")
        FH.write("  extern function new(string name, uvm_component parent);\n")
        FH.write("  extern function void write(input " + agent['item'] + " t);\n")
        FH.write("  extern function void write_drv(input " + agent['item'] + " t);\n")
        FH.write("  extern function void report_phase(uvm_phase phase);\n")
        FH.write("\n")

    self.insert_inc_file(FH,"  ","agent_scoreboard_inc_inside_class",agent)

    FH.write("endclass : " + agent['agent_name'] + "_scoreboard \n")
    FH.write("\n")
    FH.write("\n")
    if not  edef(agent,'agent_scoreboard_generate_methods_after_class',"NO"):
        if not edef( tb, 'comments_at_include_locations',"NO"):
            FH.write("// You can remove new, write, write_drv and report_phase by setting agent_scoreboard_generate_methods_after_class = no in file "+ agent['tpl'] + "\n\n")

        FH.write("function "+ agent['agent_name'] + "_scoreboard::new(string name, uvm_component parent);\n")
        FH.write("  super.new(name, parent);\n")
        FH.write("endfunction : new\n")
        FH.write("\n")
        FH.write("\n")
        FH.write("function void "+ agent['agent_name'] + "_scoreboard::write(input "+ agent['item'] + " t);\n")
        FH.write("  //if (m_config.scoreboard_enable)\n")
        FH.write("  begin\n")
        FH.write("    "+ agent['item'] + " item = t;\n")
        FH.write("    $cast(item,t.clone());\n")
        FH.write("    //\$display(\"write_mon\",item.sprint());\n")
        FH.write("    write_cnt++;\n")
        FH.write("  end\n")
        FH.write("endfunction : write\n")
        FH.write("\n")
        FH.write("function void "+ agent['agent_name'] + "_scoreboard::write_drv(input "+ agent['item'] + " t);\n")
        FH.write("  //if (m_config.scoreboard_enable)\n")
        FH.write("  begin\n")
        FH.write("    "+ agent['item'] + " item = t;\n")
        FH.write("    \$cast(item,t.clone());\n")
        FH.write("    //\$display(\"write_drv\",item.sprint());\n")
        FH.write("    write_cnt_drv++;\n")
        FH.write("  end\n")
        FH.write("endfunction : write_drv\n")
        FH.write("\n")
        FH.write("function void "+ agent['agent_name'] + "_scoreboard::report_phase(uvm_phase phase);\n")
        FH.write("    `uvm_info(get_type_name(), \"Scoreboard is enabled for this agent\", UVM_MEDIUM)\n")
        FH.write("    `uvm_info(get_type_name(), \$sformatf(\"write_cnt = %0d ,  write_cnt_drv = %0d\",write_cnt,write_cnt_drv), UVM_MEDIUM)\n")
        FH.write("endfunction : report_phase\n")
        FH.write("\n")
        FH.write("\n")

    self.insert_inc_file(FH,"","agent_scoreboard_inc_after_class",agent)

    FH.write("`endif // " + agent['agent_name'].upper()+ "_SCOREBOARD_SV\n")
    FH.write("\n")
    FH.close()

  def gen_agent(self,ag):
    agent = self.db[ag]
    tb    = self.db['top']
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_agent.sv")
    FH=file.open('w')

    self.write_file_header(FH, agent, agent['agent_name']+"_agent.sv", "Agent for agent "+ agent['agent_name'] )

    FH.write("`ifndef " + agent['agent_name'].upper()+ "_AGENT_SV\n")
    FH.write("`define " + agent['agent_name'].upper()+ "_AGENT_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH,"","agent_inc_before_class",agent)

    FH.write("class " + agent['agent_name'] + "_agent extends uvm_agent;\n")
    FH.write("\n")
    FH.write("  `uvm_component_utils(" + agent['agent_name'] + "_agent)\n")
    FH.write("\n")
    FH.write("  uvm_analysis_port #("+ agent['item'] + ") analysis_port;\n")
#    FH.write("  uvm_analysis_port #("+ agent['item'] + ") analysis_port_drv;\n")
    FH.write("\n")
    FH.write("  " + agent['agent_name'] + "_config       m_config;\n")
    FH.write("  " + agent['agent_name'] + "_sequencer_t  m_sequencer;\n")
    FH.write("  " + agent['agent_name'] + "_driver       m_driver;\n")
    FH.write("  " + agent['agent_name'] + "_monitor      m_monitor;\n")

    if edef( agent ,'agent_generate_scoreboard_class' , "YES"):
        FH.write("  " + agent['agent_name'] + "_scoreboard      m_scoreboard;\n")

    FH.write("\n")
    FH.write("  local int m_is_active = -1;\n")
    FH.write("\n")
    FH.write("  extern function new(string name, uvm_component parent);\n")
    FH.write("\n")
    if not edef(agent,'agent_generate_methods_inside_class',"NO"):
        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("  // You can remove build/connect_phase and get_is_active by setting agent_generate_methods_inside_class = no in file "+ agent['tpl'] + "\n\n")

        FH.write("  extern function void build_phase(uvm_phase phase);\n")
        FH.write("  extern function void connect_phase(uvm_phase phase);\n")
        FH.write("  extern function uvm_active_passive_enum get_is_active();\n")
        FH.write("\n")

    self.insert_inc_file(FH,"  ","agent_inc_inside_class",agent)

    FH.write("endclass : " + agent['agent_name'] + "_agent \n")
    FH.write("\n")
    FH.write("\n")

    c = ""
    if edef(agent,'agent_generate_methods_after_class',"NO"):
        c = "// ";
        FH.write(c+" You must move the new function to \"agent_inc_after_class\" defined in file "+ agent['tpl'] + "\n")

    FH.write(c+"function  " + agent['agent_name'] + "_agent::new(string name, uvm_component parent);\n")
    FH.write(c+"  super.new(name, parent);\n")
    FH.write(c+"  analysis_port = new(\"analysis_port\", this);\n")
#   FH.write(c+"  analysis_port_drv = new(\"analysis_port_drv\", this);\n")
    FH.write(c+"endfunction : new\n")
    FH.write("\n")
    FH.write("\n")

    if not edef(agent,'agent_generate_methods_after_class',"NO"):
        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("// You can remove build/connect_phase and get_is_active by setting agent_generate_methods_after_class = no in file "+ agent['tpl'] + "\n\n")

        FH.write("function void " + agent['agent_name'] + "_agent::build_phase(uvm_phase phase);\n")
        FH.write("\n")
        self.insert_inc_file(FH,"  ","agent_prepend_to_build_phase",agent)
        FH.write("  if (!uvm_config_db #(" + agent['agent_name'] + "_config)::get(this, \"\", \"config\", m_config))\n")
        FH.write("    `uvm_error(get_type_name(), \"" + agent['agent_name'] + " config not found\")\n")
        FH.write("\n")
        FH.write("  m_monitor     = " + agent['agent_name'] + "_monitor    ::type_id::create(\"m_monitor\", this);\n")
        FH.write("\n")
        FH.write("  if (get_is_active() == UVM_ACTIVE)\n")
        FH.write("  begin\n")
        FH.write("    m_driver    = " + agent['agent_name'] + "_driver     ::type_id::create(\"m_driver\", this);\n")
        FH.write("    m_sequencer = " + agent['agent_name'] + "_sequencer_t::type_id::create(\"m_sequencer\", this);\n")
        FH.write("  end\n")
        FH.write("\n")

        if edef( agent ,'agent_generate_scoreboard_class' , "YES"):
            FH.write("    m_scoreboard = " + agent['agent_name'] + "_scoreboard::type_id::create(\"m_scoreboard\", this);\n")

        self.insert_inc_file(FH,"  ","agent_append_to_build_phase",agent)

        FH.write("endfunction : build_phase\n")
        FH.write("\n")
        FH.write("\n")
        FH.write("function void " + agent['agent_name'] + "_agent::connect_phase(uvm_phase phase);\n")
        FH.write("  if (m_config.vif == null)\n")
        FH.write("    `uvm_warning(get_type_name(), \"" + agent['agent_name'] + " virtual interface is not set!\")\n")
        FH.write("\n")
        FH.write("  m_monitor.vif      = m_config.vif;\n")
        FH.write("  m_monitor.m_config = m_config;\n")
        FH.write("  m_monitor.analysis_port.connect(analysis_port);\n")
        FH.write("\n")
        FH.write("  if (get_is_active() == UVM_ACTIVE)\n")
        FH.write("  begin\n")
        FH.write("    m_driver.seq_item_port.connect(m_sequencer.seq_item_export);\n")
        FH.write("    m_driver.vif      = m_config.vif;\n")
        FH.write("    m_driver.m_config = m_config;\n")

        if edef( agent ,'agent_generate_scoreboard_class' , "YES"):
          FH.write("    m_driver.analysis_port.connect(analysis_port_drv  );\n")

        FH.write("  end\n")
        FH.write("\n")

        if edef( agent ,'agent_generate_scoreboard_class' , "YES"):
            FH.write("  m_scoreboard.m_config = m_config;\n")
            FH.write("  m_monitor.analysis_port.connect(m_scoreboard.analysis_export);\n")
            FH.write("  m_driver.analysis_port.connect(m_scoreboard.analysis_export_drv);\n")

        self.insert_inc_file(FH,"  ","agent_append_to_connect_phase",agent)

        FH.write("endfunction : connect_phase\n")
        FH.write("\n")
        FH.write("\n")
        FH.write("function uvm_active_passive_enum " + agent['agent_name'] + "_agent::get_is_active();\n")
        FH.write("  if (m_is_active == -1)\n")
        FH.write("  begin\n")
        FH.write("    if (uvm_config_db#(uvm_bitstream_t)::get(this, \"\", \"is_active\", m_is_active))\n")
        FH.write("    begin\n")
        FH.write("      if (m_is_active != m_config.is_active)\n")
        FH.write("        `uvm_warning(get_type_name(), \"is_active field in config_db conflicts with config object\")\n")
        FH.write("    end\n")
        FH.write("    else \n")
        FH.write("      m_is_active = m_config.is_active;\n")
        FH.write("  end\n")
        FH.write("  return uvm_active_passive_enum'(m_is_active);\n")
        FH.write("endfunction : get_is_active\n")
        FH.write("\n")
        FH.write("\n")

    self.insert_inc_file(FH,"","agent_inc_after_class",agent)

    FH.write("`endif // " + agent['agent_name'].upper()+ "_AGENT_SV\n")
    FH.write("\n")
    FH.close()


  def gen_seq_lib(self,ag):
    agent = self.db[ag]
    tb    = self.db['top']
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_seq_lib.sv")
    FH=file.open('w')
    self.write_file_header(FH, agent, agent['agent_name']+"_seq_lib.sv", "Sequence for agent "+ agent['agent_name'] )

    FH.write("`ifndef " + agent['agent_name'].upper()+ "_SEQ_LIB_SV\n")
    FH.write("`define " + agent['agent_name'].upper()+ "_SEQ_LIB_SV\n")
    FH.write("\n")
    FH.write("class " + agent['agent_name'] + "_default_seq extends uvm_sequence #(" + agent['item'] + ");\n")
    FH.write("\n")
    FH.write("  `uvm_object_utils(" + agent['agent_name'] + "_default_seq)\n")
    FH.write("\n")
    FH.write("  "+ agent['agent_name'] + "_config  m_config;\n")
    FH.write("\n")
    FH.write("  extern function new(string name = \"\");\n")
    FH.write("  extern task body();\n")
    FH.write("\n")
    FH.write("`ifndef UVM_POST_VERSION_1_1\n")
    FH.write("  // Functions to support UVM 1.2 objection API in UVM 1.1\n")
    FH.write("  extern function uvm_phase get_starting_phase();\n")
    FH.write("  extern function void set_starting_phase(uvm_phase phase);\n")
    FH.write("`endif\n")
    FH.write("\n")
    FH.write("endclass : " + agent['agent_name'] + "_default_seq\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function " + agent['agent_name'] + "_default_seq::new(string name = \"\");\n")
    FH.write("  super.new(name);\n")
    FH.write("endfunction : new\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("task " + agent['agent_name'] + "_default_seq::body();\n")
    FH.write("  `uvm_info(get_type_name(), \"Default sequence starting\", UVM_HIGH)\n")
    FH.write("\n")
    FH.write("  req = " + agent['item'] + "::type_id::create(\"req\");\n")
    FH.write("  start_item(req); \n")
    FH.write("  if ( !req.randomize() )\n")
    FH.write("    `uvm_error(get_type_name(), \"Failed to randomize transaction\")\n")
    FH.write("  finish_item(req); \n")
    FH.write("\n")
    FH.write("  `uvm_info(get_type_name(), \"Default sequence completed\", UVM_HIGH)\n")
    FH.write("endtask : body\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("`ifndef UVM_POST_VERSION_1_1\n")
    FH.write("function uvm_phase " + agent['agent_name'] + "_default_seq::get_starting_phase();\n")
    FH.write("  return starting_phase;\n")
    FH.write("endfunction: get_starting_phase\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function void " + agent['agent_name'] + "_default_seq::set_starting_phase(uvm_phase phase);\n")
    FH.write("  starting_phase = phase;\n")
    FH.write("endfunction: set_starting_phase\n")
    FH.write("`endif\n")
    FH.write("\n")
    FH.write("\n")

    self.insert_inc_file(FH,"","agent_seq_inc",agent)

    FH.write("`endif // " + agent['agent_name'].upper()+ "_SEQ_LIB_SV\n")
    FH.write("\n")
    FH.close()

  def gen_env(self,ag):
    agent = self.db[ag]
    tb    = self.db['top']

    if edef(agent,'agent_has_env' ,"NO"): return

    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_env.sv")
    FH=file.open('w')
    self.write_file_header(FH, agent, agent['agent_name']+"_env.sv", "Environment for agent "+ agent['agent_name'] )

    FH.write("`ifndef " + agent['agent_name'].upper()+ "_ENV_SV\n")
    FH.write("`define " + agent['agent_name'].upper()+ "_ENV_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH,"","agent_env_inc_before_class",agent)

    FH.write("class " + agent['agent_name'] + "_env extends uvm_env;\n")
    FH.write("\n")
    FH.write("  `uvm_component_utils(" + agent['agent_name'] + "_env)\n")
    FH.write("\n")
    FH.write("  extern function new(string name, uvm_component parent);\n")
    FH.write("\n")

    for i in range(0,agent['number_of_instances']):
        suffix = calc_suffix(i, agent['number_of_instances'])

        align("  " + agent['agent_name'] + "_config "  , "m_" + agent['agent_name'] + suffix + "_config;"  , "")
        align("  " + agent['agent_name'] + "_agent "   , "m_" + agent['agent_name'] + suffix + "_agent;"   , "")
        align("  " + agent['agent_name'] + "_coverage ", "m_" + agent['agent_name'] + suffix + "_coverage;", "")
        if defined ( agent , 'reg_access_mode'):
            align("  " + agent['agent_name']            + "_env_coverage " , "m_"        + agent['agent_name'] + suffix + "_env_coverage;", "")
            align("  " + agent['reg_access_block_type'] + "              " , "regmodel[" + suffix + "];  // Register model"               , "")
            align("\n", "", "")
            align("  reg2" + agent['agent_name'] + "_adapter ", "m_reg2" + agent['agent_name'] + suffix + ";", "")
#            align("  uvm_reg_predictor #(" + agent['item'] + "_types{" + agent['agent_name'] + "}) ", "m_" + agent['agent_name'] + "2reg_predictor[" + suffix + "];", "")

        align("\n", "", "")

    gen_aligned(FH)
    #add any other agents (" + agent['env_agents'] + " is hash of ref to array)


    if defined (agent,'env_agents'):
        for extra_agent in  agent['env_agents']:
            log("adding extra agent "+ extra_agent + "\n")
            FH.write("  " + extra_agent + "_config    m_" + extra_agent + "_config;\n")
            FH.write("  " + extra_agent + "_agent     m_" + extra_agent + "_agent;\n")
            FH.write("  " + extra_agent + "_coverage  m_" + extra_agent + "_coverage;\n")
            FH.write("\n")
    if not edef( agent,'agent_env_generate_methods_inside_class',"NO"):
        if not edef(tb,'comments_at_include_locations',"NO") :
            FH.write("  // You can remove build_phase and connect_phase by setting agent_env_generate_methods_inside_class = no in file " + agent['tpl'] + "\n\n")
        FH.write("  extern function void build_phase(uvm_phase phase);\n")
        FH.write("  extern function void connect_phase(uvm_phase phase);\n")
        FH.write("\n")

    self.insert_inc_file(FH,"  ","agent_env_inc_inside_class",agent)

    FH.write("endclass : " + agent['agent_name'] + "_env \n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function " + agent['agent_name'] + "_env::new(string name, uvm_component parent);\n")
    FH.write("  super.new(name, parent);\n")
    FH.write("endfunction : new\n")
    FH.write("\n")
    FH.write("\n")
    if not edef(agent,'agent_env_generate_methods_after_class',"NO"):

        if not edef( tb, 'comments_at_include_locations',"NO"):
            FH.write("// You can remove build_phase and connect_phase by setting agent_env_generate_methods_after_class = no in file " + agent['tpl'] + "\n\n")

        FH.write("function void " + agent['agent_name'] + "_env::build_phase(uvm_phase phase);\n")
        FH.write("\n")

        self.insert_inc_file(FH,"  ","agent_env_prepend_to_build_phase",agent)

        for i in range(0,agent['number_of_instances']):
            suffix = calc_suffix(i, agent['number_of_instances'])
            if (i > 0): FH.write("\n")

            FH.write("  if (!uvm_config_db #(" + agent['agent_name'] + "_config)::get(this, \"\", \"config" + suffix + "\", m_" + agent['agent_name'] + suffix + "_config))\n")
            FH.write("    `uvm_error(get_type_name(), \"Unable to get config from configuration database\")\n")
            if defined(agent,'reg_access_mode'):
                FH.write("  regmodel[" + suffix + "] = m_" + agent['agent_name'] + suffix + "_config.regmodel;\n" )
            FH.write("\n")
            FH.write("  uvm_config_db #(" + agent['agent_name'] + "_config)::set(this, \"m_" + agent['agent_name'] + suffix + "_agent\", \"config\", m_" + agent['agent_name'] + suffix + "_config);\n")
            FH.write("  if (m_" + agent['agent_name'] + suffix + "_config.is_active == UVM_ACTIVE )\n")
            FH.write("    uvm_config_db #(" + agent['agent_name'] + "_config)::set(this, \"m_" + agent['agent_name'] + suffix + "_agent.m_sequencer\", \"config\", m_" + agent['agent_name'] + suffix + "_config);\n")
            FH.write("  uvm_config_db #(" + agent['agent_name'] + "_config)::set(this, \"m_" + agent['agent_name'] + suffix + "_coverage\", \"config\", m_" + agent['agent_name'] + suffix + "_config);\n")
            if defined ( agent , 'reg_access_mode'):
                FH.write("  uvm_config_db #(" + agent['agent_name'] + "_config)::set(this, \"m_" + agent['agent_name'] + suffix + "_env_coverage\", \"config\", m_" + agent['agent_name'] + suffix + "_config);\n")

            FH.write("\n")
            FH.write("  m_" + agent['agent_name'] + suffix + "_agent    = " + agent['agent_name'] + "_agent   ::type_id::create(\"m_" + agent['agent_name'] + suffix + "_agent\", this);\n")
            FH.write("\n")
            FH.write("  m_" + agent['agent_name'] + suffix + "_coverage = " + agent['agent_name'] + "_coverage::type_id::create(\"m_" + agent['agent_name'] + suffix + "_coverage\", this);\n")
            if defined ( agent , 'reg_access_mode'):
                FH.write("  m_" + agent['agent_name'] + suffix + "_env_coverage  = " + agent['agent_name'] + "_env_coverage::type_id::create(\"m_" + agent['agent_name'] + suffix + "_env_coverage\", this);\n")
                FH.write("  m_reg2" + agent['agent_name'] + suffix + "           = reg2" + agent['agent_name'] + "_adapter ::type_id::create(\"m_reg2" + agent['agent_name'] + suffix + "\", this);\n")
                FH.write("\n")
                FH.write("  m_" + agent['agent_name'] + "2reg_predictor[" + suffix + "] = ")
                FH.write("uvm_reg_predictor #(" + agent['item'] + "_types{" + agent['agent_name'] + "})::type_id::create(\"m_" + agent['agent_name'] + "2reg_predictor[" + suffix + "]\", this);\n")


        if defined(agent,'env_agents'):

            FH.write("\n")
            FH.write("  // Additional agents")
            for extra_agent in  agent['env_agents']:
                FH.write("\n")
                FH.write("  if (!uvm_config_db #(" + extra_agent + "_config)::get(this, \"\", \"config\", m_" + extra_agent + "_config))\n")
                FH.write("    `uvm_error(get_type_name(), \"Unable to get " + extra_agent + "_config from configuration database\")\n")
                FH.write("\n")
                FH.write("  uvm_config_db #(" + extra_agent + "_config)::set(this, \"m_" + extra_agent + "_agent\", \"config\",  m_" + extra_agent + "_config);\n")
                FH.write("  if (m_" + extra_agent + "_config.is_active == UVM_ACTIVE )\n")
                FH.write("    uvm_config_db #(" + extra_agent + "_config)::set(this, \"m_" + extra_agent + "_agent.m_sequencer\", \"config\",  m_" + extra_agent + "_config);\n")
                FH.write("  uvm_config_db #(" + extra_agent + "_config)::set(this, \"m_" + extra_agent + "_coverage\", \"config\",  m_" + extra_agent + "_config);\n")
                FH.write("\n")
                FH.write("  m_" + extra_agent + "_agent    = " + extra_agent + "_agent   ::type_id::create(\"m_" + extra_agent + "_agent\", this);\n")
                FH.write("  m_" + extra_agent + "_coverage = " + extra_agent + "_coverage::type_id::create(\"m_" + extra_agent + "_coverage\", this);\n")

        FH.write("\n")

        self.insert_inc_file(FH,"  ","agent_env_append_to_build_phase",agent)

        FH.write("endfunction : build_phase\n")
        FH.write("\n")
        FH.write("\n")
        FH.write("function void " + agent['agent_name'] + "_env::connect_phase(uvm_phase phase);\n")
        FH.write("\n")
        for i in range(0,agent['number_of_instances']):
            suffix = calc_suffix(i, agent['number_of_instances'])
            align("  m_" + agent['agent_name'] + suffix + "_agent", ".analysis_port.connect(m_" + agent['agent_name'] + suffix + "_coverage.analysis_export);", "")
            if defined ( agent , 'reg_access_mode'):
                align("  m_" + agent['agent_name'] + suffix + "_agent", ".analysis_port.connect(m_" + agent['agent_name'] + "2reg_predictor" + suffix + ".bus_in);", "")
                align("  m_" + agent['agent_name'] + suffix + "_agent", ".analysis_port.connect(m_" + agent['agent_name'] + suffix + "_env_coverage.analysis_export);", "")
                align("  m_" + agent['agent_name'] + suffix + "_env_coverage.regmodel = regmodel" + suffix + ";\n", "", "")

        if defined(agent,'env_agents'):
            for extra_agent in  agent['env_agents']:
                align("  m_" + extra_agent + "_agent", ".analysis_port.connect(m_" + extra_agent + "_coverage.analysis_export);", "")

        gen_aligned(FH)
        FH.write("\n")

        self.insert_inc_file(FH,"  ","agent_env_append_to_connect_phase",agent)

        FH.write("endfunction : connect_phase\n")
        FH.write("\n")
        FH.write("\n")

    self.insert_inc_file(FH,"","agent_env_inc_after_class",agent)

    FH.write("`endif // " + agent['agent_name'].upper()+ "_ENV_SV\n")
    FH.write("\n")
    FH.close()


  def gen_env_seq_lib(self,ag):
    agent = self.db[ag]
    tb    = self.db['top']
    if defined ( agent , 'reg_access_mode')  or edef(agent,'agent_has_env',"NO"):  return
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_env_seq_lib.sv")
    FH=file.open('w')
    self.write_file_header(FH, agent, agent['agent_name']+"_env_seq_lib.sv", "Sequence for agent "+ agent['agent_name'] )

    FH.write("`ifndef " + agent['agent_name'].upper()+ "_ENV_SEQ_LIB_SV\n")
    FH.write("`define " + agent['agent_name'].upper()+ "_ENV_SEQ_LIB_SV\n")
    FH.write("\n")
    FH.write("class "+ agent['agent_name'] + "_env_default_seq extends uvm_sequence #(uvm_sequence_item);\n")
    FH.write("\n")
    FH.write("  `uvm_object_utils(" + agent['agent_name'] + "_env_default_seq)\n")
    FH.write("\n")
    FH.write("  "+ agent['agent_name'] + "_env m_env;\n")
    FH.write("\n")
    FH.write("  extern function new(string name = \"\");\n")
    FH.write("  extern task body();\n")
    FH.write("\n")
    FH.write("`ifndef UVM_POST_VERSION_1_1\n")
    FH.write("  // Functions to support UVM 1.2 objection API in UVM 1.1\n")
    FH.write("  extern function uvm_phase get_starting_phase();\n")
    FH.write("  extern function void set_starting_phase(uvm_phase phase);\n")
    FH.write("`endif\n")
    FH.write("\n")
    FH.write("endclass : " + agent['agent_name'] + "_env_default_seq\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function  "+ agent['agent_name'] + "_env_default_seq::new(string name = \"\");\n")
    FH.write("  super.new(name);\n")
    FH.write("endfunction : new\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("task "+ agent['agent_name'] + "_env_default_seq::body();\n")
    FH.write("  `uvm_info(get_type_name(), \"Default sequence starting\", UVM_HIGH)\n")
    FH.write("\n")
    FH.write("  // Note: there can be multiple child sequences started concurrently within this fork..join\n")
    FH.write("  fork\n")
    for i in  range(0,agent['number_of_instances']):
        suffix = calc_suffix(i, agent['number_of_instances'])
        sequencer_instance_name = "m_env.m_"+ agent['agent_name'] + suffix + "_agent.m_sequencer"
        if ( i > 0 ): FH.write("\n")


        FH.write("    if (m_env.m_"+ agent['agent_name'] + suffix+"_config.is_active == UVM_ACTIVE)\n")
        FH.write("    begin\n")
        FH.write("      "+ agent['agent_name'] + "_default_seq seq;\n")
        FH.write("      seq = "+ agent['agent_name'] + "_default_seq::type_id::create(\"seq"+ suffix + "\");\n")
        FH.write("      seq.set_item_context(this, "+ sequencer_instance_name + ");\n")
        FH.write("      if ( !seq.randomize() )\n")
        FH.write("        `uvm_error(get_type_name(), \"Failed to randomize sequence\")\n")
        FH.write("      seq.m_config = m_env.m_"+ agent['agent_name'] + suffix + "_config;\n")
        FH.write("      seq.set_starting_phase( get_starting_phase() );\n")
        FH.write("      seq.start("+ sequencer_instance_name + ", this);\n")
        FH.write("    end\n")
    if defined(agent,'env_agents'):
      for extra_agent in  agent['env_agents']:
        sequencer_instance_name = "m_env.m_" + extra_agent + "_agent.m_sequencer"
        FH.write("\n")
        FH.write("    if (m_env.m_"+ extra_agent + "_agent.m_config.is_active == UVM_ACTIVE)\n")
        FH.write("    begin\n")
        FH.write("      "+ extra_agent + "_default_seq seq;\n")
        FH.write("      seq = "+ extra_agent + "_default_seq::type_id::create(\"seq\");\n")
        FH.write("      seq.set_item_context(this, "+ sequencer_instance_name + ");\n")
        FH.write("      if ( !seq.randomize() )\n")
        FH.write("        `uvm_error(get_type_name(), \"Failed to randomize sequence\")\n")
        FH.write("      seq.m_config = m_env.m_"+ extra_agent + "_agent.m_config;\n")
        FH.write("      seq.set_starting_phase( get_starting_phase() );\n")
        FH.write("      seq.start("+ sequencer_instance_name + ", this);\n")
        FH.write("    end\n")

    FH.write("  join\n")
    FH.write("\n")
    FH.write("  `uvm_info(get_type_name(), \"Default sequence completed\", UVM_HIGH)\n")
    FH.write("endtask : body\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("`ifndef UVM_POST_VERSION_1_1\n")
    FH.write("function uvm_phase "+ agent['agent_name'] + "_env_default_seq::get_starting_phase();\n")
    FH.write("  return starting_phase;\n")
    FH.write("endfunction: get_starting_phase\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function void "+ agent['agent_name'] + "_env_default_seq::set_starting_phase(uvm_phase phase);\n")
    FH.write("  starting_phase = phase;\n")
    FH.write("endfunction: set_starting_phase\n")
    FH.write("`endif\n")
    FH.write("\n")
    FH.write("\n")

    self.insert_inc_file(FH,"","agent_env_seq_inc",agent)

    FH.write("`endif // " + agent['agent_name'].upper()+ "_ENV_SEQ_LIB_SV\n")
    FH.write("\n")
    FH.close()


  def gen_agent_pkg(self,ag):
    agent = self.db[ag]
    tb    = self.db['top']
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/"
    file= Path(dir + agent['agent_name'] + "_pkg.sv")
    FH=file.open('w')
    self.write_file_header(FH, agent, agent['agent_name']+"_pkg.sv", "Package for  for agent "+ agent['agent_name'] )

    FH.write("package "+ agent['agent_name'] + "_pkg;\n")
    FH.write("\n")
    FH.write("  `include \"uvm_macros.svh\"\n")
    FH.write("\n")
    FH.write("  import uvm_pkg::*;\n")
    FH.write("\n")

    self.insert_inc_file(FH,"  ","common_define", tb,"dut")

    if mdefined(agent,'common_pkg','file'):
        FH.write("  import "+ agent['common_pkg']['name'] + "::*;\n" )
    if mdefined(agent,'common_env_pkg','file'):
        FH.write("  import "+ agent['common_env_pkg']['name'] + "::*;\n" )
    if mdefined(agent,'reg_access_mode'):
        FH.write("  import regmodel_pkg::*;\n" )

    if mdefined(agent,'env_agents'):
        for extra_agent in agent['env_agents']:
            FH.write("  import "+ extra_agent + "_pkg::*;\n")

    FH.write("\n")
    FH.write("  `include \"" + agent['item']       + ".sv\"\n")
    FH.write("  `include \"" + agent['agent_name'] + "_config.sv\"\n")
    FH.write("  `include \"" + agent['agent_name'] + "_driver.sv\"\n")
    FH.write("  `include \"" + agent['agent_name'] + "_monitor.sv\"\n")
    FH.write("  `include \"" + agent['agent_name'] + "_sequencer.sv\"\n")
    FH.write("  `include \"" + agent['agent_name'] + "_coverage.sv\"\n")
    if edef( agent ,'agent_generate_scoreboard_class' , "YES"):
        FH.write("  `include \"" + agent['agent_name'] + "_scoreboard.sv\"\n")

#    for ref_model_name in agent_pkg_include
#        FH.write("  `include \""+ ref_model_name + ".sv\"\n")
#    }
    FH.write("  `include \"" + agent['agent_name'] + "_agent.sv\"\n")
    FH.write("  `include \"" + agent['agent_name'] + "_seq_lib.sv\"\n")

    if defined ( agent , 'reg_access_mode'):
        FH.write("  `include \"reg2" + agent['agent_name'] + "_adapter.sv\"\n")
        FH.write("  `include \"" + agent['agent_name'] + "_env_coverage.sv\"\n")

    if not edef( agent,'agent_has_env', "NO"):
        FH.write("  `include \"" + agent['agent_name'] + "_env.sv\"\n")
        FH.write("  `include \"" + agent['agent_name'] + "_env_seq_lib.sv\"\n")

    FH.write("\n")
    FH.write("endpackage : "+ agent['agent_name'] + "_pkg\n")
    FH.close()


  def gen_agent_test(self,ag):
    agent = self.db[ag]
    tb    = self.db['top']
    dir = agent['project'] + "/tb/" + agent['agent_name']+ "/sv/test/"
    top = agent['agent_name'] + "_test"

    file= Path(dir + agent['agent_name'] + "_test.sv")
    FH=file.open('w')
    self.write_file_header(FH, agent, agent['agent_name']+"_test.sv", "Test for agent "+ agent['agent_name'] )

    #gen_top_pkg( agent ); #$dir,$top)
    #gen_agent_test_env( dir, top, "agent_test" ,\tb['top_env'])

    FH.write("\n")
    FH.close()

  def generate_agents (self,ag):

    self.gen_agent_dir(ag)
    log("Create the agent files\n")
    self.gen_if(ag)
    self.gen_bfm(ag)
    self.gen_seq_item(ag)
    self.gen_config(ag)
    self.gen_driver(ag)
    self.gen_monitor(ag)
    self.gen_sequencer(ag)
    self.gen_cov(ag)
    self.gen_sb(ag)
    self.gen_agent(ag)
    self.gen_seq_lib(ag)
    self.gen_env(ag)
    self.gen_env_seq_lib(ag)
    self.gen_agent_pkg(ag)
#    self.gen_agent_test(ag)

  def gen_template(self,name,ref):

    tb_fname = ref['project']+"/tb/include/" + ref['agent_name'] +'/'+ ref[name]['file']
    inc_fname = ref['inc_path']+"/" + ref['agent_name'] +'/'+ ref[name]['file']
    ref['tmplt'] ={}
    ref['tmplt']['tb_fname']  = tb_fname
    ref['tmplt']['inc_fname'] = inc_fname

    if template.is_member(name):
      template(name,ref)
    elif template.is_member('template_prototype'):
      template('template_prototype',ref,name)
    else: # not used ! real fallback solution
      print (name,template.is_member(name))
      Path(tb_fname).touch()
      Path(inc_fname).touch()

  def _insert_inc_file (self, FH, indent, param_name, ref, x=0):
    #print (indent, param_name)
    fname  = None
    inline = 0

    if (defined(param_name) and param_name in ref ):
      if defined(ref[param_name],'file') :
        fname = ref[param_name]['file']
        if ref[param_name]['inline'] != "0" : inline = ref[param_name]['inline']
        else: inline = ""

    if defined(fname):
       self.gen_template(param_name,ref)

    if defined(fname):
      fname =  ref['agent_name']+'/'+fname
      fullname = ref['project'] + "/tb/include/"+fname
      fn = Path(fullname)
      if fn.exists():

        if defined(inline) and str(inline).upper() == "INLINE" :
          TH = fn.open()
          if param_name != "file_header_inc" :
            FH.write(indent+"// Start of inlined include file "+ fullname + "\n")
          for line in TH :
              FH.write(indent + line)
          if param_name != "file_header_inc" :
            FH.write("\n"+ indent + "// End of inlined include file\n")
          FH.write("\n")

        else:

          FH.write(indent+"`include \""+ fname + "\"\n")
          FH.write("\n")

      else:
        #check_file(fullname)
        if defined(inline) and str(inline).upper() == "INLINE" :
          if param_name!="file_header_inc":
            FH.write(indent+"// Start of inlined include file "+ fullname + "\n" )
          FH.write(indent+"// ERROR : File "+ fullname + " not found \n")
          if param_name!="file_header_inc":
            FH.write(indent+"// End of inlined include file\n" )
          FH.write("\n")

        else:

          FH.write(indent+"// ERROR: `include \""+ fname + "\"; "+ fullname + " not found\n")
          FH.write("\n")

    else:
      if defined(param_name) and param_name != "" :
        if not edef( ref,'comments_at_include_locations', "NO" ):
          FH.write(indent+"// You can insert code here by setting "+ str(param_name) + " in file "+ str(ref['tpl']) + "\n\n")


  def write_file_header (self,FH,ref,fname,description):

    if edef(ref, 'generate_file_header' , "YES" ):

      inline = "INLINE"

      self.insert_inc_file(FH,"", "file_header_inc", ref)

      FH.write("//=============================================================================\n")


      if defined(ref,'copyright') or defined(ref,'tb_description'):
        if defined(ref,'copyright'):
          FH.write("// Copyright  : "+ ref['copyright'] + "\n"      )
        if defined(ref,'tb_description'):
          FH.write("// Prj.Descr  : "+ ref['tb_description'] + "\n" )
          FH.write("//=============================================================================\n")

      FH.write("// Project    : " + ref['project'] + "\n")
      FH.write("//\n")
      FH.write("// File Name  : "+ fname + "\n")
      FH.write("//\n")
      if defined(ref,'author'):
        FH.write("// Author     : Name   : "+ ref['author'] + "\n")
      if defined(ref,'email'):
        FH.write("//              Email  : "+ ref['email'] + "\n")
      if defined(ref,'tel'):
        FH.write("//              Tel    : "+ ref['tel'] + "\n")
      if defined(ref,'dept'):
        FH.write("//              Dept   : "+ ref['dept'] + "\n")
      if defined(ref,'company'):
        FH.write("//              Company: "+ ref['company'] + "\n")
      if defined(ref,'year'):
        FH.write("// Year       : "+ ref['year'] + "\n")
      if defined(ref,'script_version'):
        FH.write("// Script     : "+ ref['script_version'] + "\n")
      if defined(ref,'repository_version'):
        FH.write("// Repository : "+ ref['repository_version'] + "\n")
      FH.write("//\n")
      if defined(ref,'version'):
        FH.write("// "+ ref['copyright'] + "      Version:   "+ ref['version'] + "\n")
      if defined(ref,'code_version'):
        FH.write("// "+ ref['copyright'] + " Code Version:   "+ ref['code_version'] + "\n")
      if defined(ref,'test_spec_version'):
        FH.write("// "+ ref['copyright'] + " TestSpec. V.:   "+ ref['test_spec_version'] + "\n")
      FH.write("//\n")

      datestr = "on "+ ref['date']
      if edef( ref ,'print_date' , "NO"): datestr = ""
      FH.write("// Code created by UVM Code Generator version "+ ref['VERNUM'] +" "+ datestr + "\n")
      FH.write("//=============================================================================\n")
      if defined(ref,'description'):
        FH.write("// Description: "+ ref['description'] + "\n"  )
      FH.write("// Description: "+ description + "\n")
      FH.write("//=============================================================================\n")
      FH.write("\n")


if __name__ == '__main__':

  f=open('uvm_db.json')
  db = json.load(f)

  skeys = list(db.keys())

  skeys.sort()
  print(skeys)

  obj = AGENT(db)
  regmodel = 0
  print("---------------for------------------------")

  for ag in skeys:
    if ag == 'top': continue
    print ("generate agent ", ag )

    obj.generate_agents(ag)
    print("---------------------------------------")


