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

""" Helper module to parse tpl file and create a database

gen_create_db.py 
Version 1.0.1

"""
from header_cfg import *

import datetime
import re
import os
import sys
import json
import datetime
now = str(datetime.datetime.now())
now =re.sub(':[^:]*$','',now)

global_continuous = 0

from uvm_support import * # global functions

VERSTR =  "ASICNET 2022-07-01"
VERNUM =  "1.0.1"

class PARSE_TPL():
  '''Class for TPL file parser
  The the data base is processed and given to the uvm_execution()
  '''

  def __init__(self,resdb, verbose='info',ind=3,file='common.tpl', name='common'):
      '''Define objekt variables and print debug infos
      '''
      self.testCaseId = '0.0'
      self.verbose = verbose
      self.ind=ind
      self.resdb=resdb
      self.file = file
      self.name = name

      self.flag_values   = []
      self.normal_values = []
      self.array_values  = []
      self.hash_values   = []
      self.include_files = []
      self.tpl_values    = {}

      self.fdb      = []
      self.inline   = 0

      if ind:
          self.indstr=' '*ind

      if severityLevel(self.verbose,'debug'):
          class_name = self.__class__.__name__
          print_fc(class_name + ' created','gr')

  def parse_file (self):
    file = self.file
    cnt=0
    try:
      fh = open(file, 'r')
    except IOError:
      pexit ("ERROR: File "+ file + " not exists !\n")

    for line in fh:
      cnt+=1
      if re.search(r'^\s*#'    , line): continue #comment line starts with "#"
      #if re.search(r'^\s*\/\/' , line): continue #comment line starts with "//"
      if re.search(r'^\s+$'    , line): continue #blank line
      line = re.sub(r'[\r\n]+' ,  '', line )     #delete EOL
      line = re.sub(r'\s*#.*$' ,  '', line )     #delete trailing comments with "#"
      #line = re.sub(r'\s*\/\/.*$','', line )     #delete trailing comments with "//"
      line = re.sub(r'^\s*'   ,'' , line)
      line = re.sub(r'\s*$'   ,'' , line)
      line = re.sub(r'\s*=\s*','=', line)
      if re.match(r'^(\w+)=' , line ) :
        #print ( line )
        self.fdb.append(line)
      else:
        pexit ("ERROR: Exiting due to Error: bad entry in line "+str(cnt)+" of "+file+": "+ line )

  def parse_normal_values (self,db):
    h={}
    for entry in self.fdb:

      res = re.search(r'^(\w+)=(.*)',entry)
      (param_name,param_value) = (res.group(1).lower(),res.group(2))
      for parameter in self.normal_values:
        if re.search(r'\b%s\b'%parameter,param_name) :
          h[param_name] = param_value
    for x in h:
      db[x]=h[x]
    return h

  def parse_flag_values (self,db):
    h={}

    for entry in self.fdb:
      res = re.search(r'^(\w+)=(.*)',entry)
      (param_name,param_value) = (res.group(1),res.group(2))
      for parameter in self.flag_values:
       if re.search(r'\b%s\b'%parameter,param_name):
          h[param_name.lower()] = param_value.upper()

    for x in h:
      db[x]=h[x]
    return h

  def parse_array_values (self,db):
    h={}
    for entry in self.fdb:
      res = re.search(r'^(\w+)=(.*)',entry)
      (param_name,param_value) = (res.group(1),res.group(2))

      for parameter in self.array_values:
        if re.search(r'\b%s\b'%parameter,param_name):
          if param_name.lower()in h :
            h[param_name.lower()].append(param_value)
          else:
            h[param_name.lower()] = [param_value]
    for x in h:
      db[x]=h[x]
    return h

  def parse_hash_values (self,db):
    h={}
    for entry in self.fdb:
      res = re.search(r'^(\w+)=(.*)',entry)
      (param_name,param_value) = (res.group(1),res.group(2))
      for parameter in self.hash_values:
        if re.search(r'\b%s\b'%parameter,param_name):
          tmp =  re.search(r'(\S+)\s*,\s*(.*)',param_value)
          h[param_name.lower()] = {tmp.group(1):tmp.group(2)}
    for x in h:
      db[x]=h[x]
    return h

  def parse_include_files (self,db):
    h={}
    for entry in self.fdb:
      res = re.search(r'^(\w+)=(.*)',entry)
      (param_name,param_value) = (res.group(1),res.group(2))
      #print(param_name,"--",param_value)
      for parameter in self.include_files:
        if re.search(r'\b%s\b'%parameter,param_name):

          tmp =  re.search(r'([\w\.\/]+)\s*(,|\s)?\s*(\w*)',param_value)
          h[param_name.lower()] = {"file":tmp.group(1),"inline":0}
          if tmp.group(3): h[param_name.lower()]["inline"] = tmp.group(3)

    for x in h:
      db[x]=h[x]
    return h

  def create_db (self):
      tplobj = {}

      self.parse_file()
      self.parse_flag_values  (tplobj)
      self.parse_normal_values(tplobj)
      self.parse_include_files(tplobj)
      self.parse_array_values (tplobj)
      self.parse_hash_values  (tplobj)
      return tplobj


class uvm_create_db ():

  global global_continuous

  def __init__(self,common_tpl,agent_tpl):

    self.db = {}
    if common_tpl:
      self.tb = self.parse_common_template(common_tpl)
    else:
      pexit("No common tb is given!")

    #json.dump(self.tb,open("self_tb.json","w"),indent=4,sort_keys=True);exit()

    self.after_parse_common(self.tb)
    self.db[self.tb['agent_name']] = self.tb
    if not agent_tpl:
      agent_tpl = self.tb['ctpl']

    if agent_tpl:
      agent_tpl.sort()
      for a in agent_tpl:
        #name = re.sub(r'\..*','',a)
        agent = self.parse_agent_template(a)
        self.after_parse_agent(agent,self.tb)
        self.db[agent['agent_name']] = agent
    else:
      pexit("No agent is given!")

  def get_db(self):
    return self.db

  def create_db (self, tpldef , name, template_name ):

    obj = PARSE_TPL(0,verbose='info',file=template_name)

    obj.flag_values   = tpldef['flag_values'  ]
    obj.normal_values = tpldef['normal_values']
    obj.array_values  = tpldef['array_values' ]
    obj.hash_values   = tpldef['hash_values'  ]
    obj.include_files = tpldef['include_files']

    return obj.create_db()


  def parse_common_template (self,template_name):

    top_def = {}

    top_def['flag_values'] = [
         "framework",
         "update_include",
         "print_date",
         "regmodel_file",
         "backup",
         "no_logfile",
         "comments_at_include_locations",
         "generate_file_header",
         "split_transactors",
         "dual_top",
         "nested_config_objects",
         "tb_generate_run_test",
         "th_generate_clock_and_reset",
         "test_generate_methods_inside_class",
         "test_generate_methods_after_class",
         "top_env_generate_methods_inside_class",
         "top_env_generate_methods_after_class",
         "top_env_generate_end_of_elaboration",
         "top_env_generate_run_phase",
         "top_env_config_generate_methods_inside_class",
         "top_env_config_generate_methods_after_class",
         "top_env_generate_scoreboard_class",
         "top_env_scoreboard_generate_methods_inside_class",
         "top_env_scoreboard_generate_methods_after_class"
    ]

    top_def['normal_values'] = [
         "os",
         "dut_source_path",
         "source_list_file",
         "inc_path",
         "project",
         "prefix",
         "top_reg_block_type",
         "tmplt_include_file",
         "tool",
         "copyright",
         "author",
         "email",
         "tel",
         "dept",
         "company",
         "year",
         "script_version",
         "version",
         "repository_version",
         "code_version",
         "test_spec_version",
         "dut_top",
         "sb_top",
         "dut_hdl_com",
         "dut_name",
         "dut_pfile",
         "period",
         "reset_time",
         "timeunit",
         "timeprecision",
         "top_name",
         "top_factory_set",
         "uvm_cmdline",
         "dut_iname",
         "top_default_seq_count",
         "top_pkg_include",
         "syosil_scoreboard_src_path",
         "description",
         "tpl_top_active_agent"
    ]

    top_def['include_files'] = [
           "tb_inc_inside_module",
           "tb_inc_before_run_test",
           "tb_prepend_to_initial",
           "th_inc_inside_module",
           "file_header_inc",
           "test_inc_inside_class",
           "test_inc_before_class",
           "test_inc_after_class",
           "test_prepend_to_build_phase",
           "test_append_to_build_phase",
           "top_env_inc_before_class",
           "top_env_inc_inside_class",
           "top_env_inc_after_class",
           "top_env_prepend_to_build_phase",
           "top_env_append_to_build_phase",
           "top_env_append_to_connect_phase",
           "top_env_append_to_run_phase",
           "top_env_config_append_to_new",
           "top_env_config_inc_before_class",
           "top_env_config_inc_inside_class",
           "top_env_config_inc_after_class",
           "top_seq_inc",
           "top_env_scoreboard_inc_before_class",
           "top_env_scoreboard_inc_inside_class",
           "top_env_scoreboard_inc_after_class",
           "top_env_scoreboard_inc_class",
           "common_define",
           "common_pkg",
           "common_pre_pkg",
           "common_env_pkg"
           ]

    # array_values ?? trans_var trans_meta trans_enum_var trans_enum_meta trans_var_constraint if_port
    top_def['array_values'] = [
         "config_var",
         "vlog_option",
         "vcom_option",
         "vsim_option",
         "vopt_option",
         "ref_model_input",
         "ref_model_output",
         "ref_model_compare_method",
         "ref_model_inc_before_class",
         "ref_model_inc_inside_class",
         "ref_model_inc_after_class",
         "tpl",
         "tmplt_test_case"
    ]

    top_def['hash_values'] = []

    tb = self.create_db(top_def,"dut_top",template_name)
    if defined(tb,'tpl'):
      tb['ctpl'] = tb['tpl']
    self.set_default_tb_values(tb)
    tb['tpl'] = template_name
    log ( "prefix for top-level names: " + tb['top_name'])
    tb["agent_name"] = tb['top_name']
    return tb


  def parse_agent_template (self, template_name):
    agent_def = {}

    agent_def['flag_values'] = [
       "agent_has_env",
       "agent_has_test",
       "uvm_seqr_class",
       "agent_is_active",
       "agent_checks_enable",
       "agent_coverage_enable",
       "agent_scoreboard_enable",
       "generate_interface_instance",
       "agent_generate_methods_inside_class",
       "agent_generate_methods_after_class",
       "agent_scoreboard_generate_methods_inside_class",
       "agent_scoreboard_generate_methods_after_class",
       "agent_env_generate_methods_inside_class",
       "agent_env_generate_methods_after_class",
       "adapter_generate_methods_inside_class",
       "adapter_generate_methods_after_class",
       "trans_generate_methods_inside_class",
       "trans_generate_methods_after_class",
       "agent_config_generate_methods_inside_class",
       "agent_config_generate_methods_after_class",
       "agent_cover_generate_methods_inside_class",
       "agent_cover_generate_methods_after_class",
       "reg_cover_generate_methods_inside_class",
       "reg_cover_generate_methods_after_class",
       "agent_generate_scoreboard_class",
       "agent_pkg_include",
       "generate_file_header",
       "agent_has_active_reset"
    ]

    agent_def['normal_values'] = [
       "agent_name",
       "byo_interface",
       "if_clock",
       "if_reset",
       "agent_factory_set",
       "uvm_reg_data",
       "uvm_reg_addr",
       "uvm_reg_kind",
       "trans_item",
       "reg_access_mode",
       "reg_access_name",
       "reg_access_map",
       "reg_access_block_instance",
       "reg_access_block_type",
       "description",
       "additional_agent",
       "number_of_instances"
    ]

    agent_def['include_files'] = [
       "agent_inc_before_class",
       "agent_inc_inside_class",
       "agent_inc_after_class",
       "driver_inc_before_class",
       "driver_inc_inside_class",
       "driver_inc_after_class",
       "monitor_inc_before_class",
       "monitor_inc_inside_class",
       "monitor_inc_after_class",
       "if_inc_inside_interface",
       "if_inc_before_interface",
       "file_header_inc",
       "trans_inc_before_class",
       "trans_inc_inside_class",
       "trans_inc_after_class",
       "sequencer_inc_before_class",
       "sequencer_inc_inside_class",
       "sequencer_inc_after_class",
       "agent_env_inc_before_class",
       "agent_env_inc_inside_class",
       "agent_env_inc_after_class",
       "adapter_inc_before_class",
       "adapter_inc_inside_class",
       "adapter_inc_after_class",
       "agent_config_inc_before_class",
       "agent_config_inc_inside_class",
       "agent_config_inc_after_class",
       "agent_cover_inc_before_class",
       "agent_cover_inc_inside_class",
       "agent_cover_inc_after_class",
       "reg_cover_inc_before_class",
       "reg_cover_inc_inside_class",
       "reg_cover_inc_after_class",
       "agent_inc_inside_bfm",
       "agent_prepend_to_build_phase",
       "agent_append_to_build_phase",
       "agent_append_to_connect_phase",
       "agent_copy_config_vars",
       "agent_env_seq_inc",
       "agent_env_prepend_to_build_phase",
       "agent_env_append_to_build_phase",
       "agent_env_append_to_connect_phase",
       "agent_cover_inc",
       "driver_inc",
       "monitor_inc",
       "reg_seq_inc",
       "reg_cover_inc",
       "agent_seq_inc",
       "agent_scoreboard_inc_before_class",
       "agent_scoreboard_inc_inside_class",
       "agent_scoreboard_inc_after_class"
    ]

    agent_def['array_values'] = [
       "trans_var",
       "trans_meta",
       "trans_enum_var",
       "trans_enum_meta",
       "trans_var_constraint",
       "config_var",
       "if_port",
       "if_map"
    ]

    agent_def['hash_values'] = []

    agent = self.create_db(agent_def,"agent_name",template_name)
    self.set_default_agent_values(agent)
    log( "prefix for top-level names: "+agent['agent_name'])
    agent['tpl'] = template_name
    return agent


  def set_default_tb_values(self,ref):
    if not ( "dut_top" in ref                           ): pexit("The DUT top level name must be defined within teh common tpl file! dut_top = <entity_nme>")
    if not ( "top_name" in ref                          ): ref["top_name"]                          = 'top'
    if not ( "date" in ref                              ): ref["date"]                              = "localtime = " + now
    if not ( "project" in ref                           ): ref["project"]                           = ref['dut_top'] +"_tb"
    if not ( "backup" in ref                            ): ref["backup"]                            = "yes"
    if not ( "version" in ref                           ): ref["version"]                           = "0.0.1"
    if not ( "inc_path" in ref                          ): ref["inc_path"]                          = "include"
    if not ( "dut_source_path" in ref                   ): ref["dut_source_path"]                   = "dut"
    if not ( "source_list_file" in ref                  ): ref["source_list_file"]                  = "files.f"
    if not ( "tpl" in ref                               ): ref["tpl"]                               = "common.tpl"
    if not ( "dut_iname" in ref                         ): ref["dut_iname"]                         = "uut"
    if not ( "timeunit" in ref                          ): ref["timeunit"]                          = "1ps"
    if not ( "timeprecision" in ref                     ): ref["timeprecision"]                     = "1ps"
    if not ( "period" in ref                            ): ref["period"]                            = "20ns"
    if not ( "reset_time" in ref                        ): ref["reset_time"]                        = "75ns"
    if not ( "dut_hdl_com" in ref                       ): ref["dut_hdl_com"]                       = "vcom"
    if not ( "tool" in ref                              ): ref["tool"]                              = "questa"
    if not ( "framework" in ref                         ): ref["framework"]                         = "NO"
    if not ( "update_include" in ref                    ): ref["update_include"]                    = "YES"
    if not ( "print_date" in ref                        ): ref["print_date"]                        = "YES"
    if not ( "dut_pfile" in ref                         ): ref["dut_pfile"]                         = "pinlist.txt"
    if not ( "prefix" in ref                            ): ref["prefix"]                            = "top"
    if not ( "no_logfile" in ref                        ): ref["no_logfile"]                        = "NO"
    if not ( "top_env_generate_scoreboard_class" in ref ): ref["top_env_generate_scoreboard_class"] = "NO"
    if not ( "top_env_scoreboard_inc_class" in ref      ): ref["top_env_scoreboard_inc_class"]      = "NO"
    if not ( "comments_at_include_locations" in ref     ): ref["comments_at_include_locations"]     = "YES"
    if not ( "sb_top" in ref                            ): ref["sb_top"]                            = "top"
    if not ( "sb_top_full" in ref                       ): ref["sb_top_full"]                       = ref["sb_top"]+"_scoreboard.sv"
    if not ( "generate_file_header" in ref              ): ref["generate_file_header"]              = "YES"
    if not ( "split_transactors" in ref                 ): ref["split_transactors"]                 = "NO"
    if not ( "script_version" in ref                    ): ref["script_version"]                    = VERNUM
    if not ( "description" in ref                       ): ref["description"]                       = "UVM_TEMPLATE_GENERATOR"
    if not ( "os" in ref                                ): ref["os"]                                = sys.platform
    if not ( "tmplt_include_file" in ref                ): 
      if 'tmplt_include_file' in globals():
        ref["tmplt_include_file"]                = tmplt_include_file
      else:  
        ref["tmplt_include_file"]                = "uvm_template"
    ref["os"] = ref["os"].upper()
    ref["tmplt_include_file"] = ref["tmplt_include_file"].split('.')[0]
    ref['period'] = re.sub(r'\s*','',ref['period'])

  def set_default_agent_values (self,ref):
    if not ( "agent_name" in ref                       ): ref["agent_name"]                      = "myagent"
    if not ( "agent_if" in ref                         ): ref["agent_if"]                        = "myagent_if"
    if not ( "trans_item" in ref                       ): ref["trans_item"]                      = "item"
    if not ( "item" in ref                             ): ref["item"]                            = "item"
    if not ( "regmodel" in ref                         ): ref["regmodel"]                        = 0
    if not ( "dut_pfile" in ref                        ): ref["dut_pfile"]                       = "pinlist.txt"
    if not ( "regmodel_file" in ref                    ): ref["regmodel_file"]                   = "regmodel.sv"
    if not ( "template_name" in ref                    ): ref["template_name"]                   = "myagent.tpl"
    if not ( "template_list" in ref                    ): ref["template_list"]                   = ""
    if not ( "dual_top" in ref                         ): ref["dual_top"]                        = "NO"
    if not ( "split_transactors" in ref                ): ref["split_transactors"]               = "NO"
    if not ( "generate_scoreboard_class" in ref        ): ref["generate_scoreboard_class"]       = "NO"
    if not ( "generate_file_header" in ref             ): ref["generate_file_header"]            = "YES"
    if not ( "comments_at_include_locations" in ref    ): ref["comments_at_include_locations"]   = "YES"
    if not ( "number_of_instances" in ref              ): ref["number_of_instances"]             = 1
    if not ( "uvm_seqr_class" in ref                   ): ref["uvm_seqr_class"]                  = "NO"
    if not ( "agent_is_active" in ref                  ): ref["agent_is_active"]                 = "UVM_ACTIVE"
    if not ( "agent_has_active_reset" in ref           ): ref["agent_has_active_reset"]          = "NO"
    if not ( "agent_has_env" in ref                    ): ref["agent_has_env"]                   = "NO"
    #if not ( "additional_agent" in ref                 ): ref["additional_agent"]                = None
    if not ( "agent_checks_enable" in ref              ): ref["agent_checks_enable"]             = "YES"
    if not ( "agent_coverage_enable" in ref            ): ref["agent_coverage_enable"]           = "YES"
    if not ( "agent_generate_scoreboard_class" in ref  ): ref["agent_generate_scoreboard_class"] = "NO"
    if not ( "agent_scoreboard_enable" in ref          ): ref["agent_scoreboard_enable"]         = "NO"
    if not ( "trans_var" in ref                        ): ref["trans_var"]                       = []
    if not ( "trans_meta" in ref                       ): ref["trans_meta"]                      = []
    if not ( "trans_enum_var" in ref                   ): ref["trans_enum_var"]                  = []
    if not ( "trans_enum_meta" in ref                  ): ref["trans_enum_meta"]                 = []
    if not ( "trans_var_constraint" in ref             ): ref["trans_var_constraint"]            = []
    if not ( "config_var" in ref                       ): ref["config_var"]                      = []
    if not ( "if_port" in ref                          ): ref["if_port"]                         = []
    if not ( "if_map" in ref                           ): ref["if_map"]                          = []

    ref["number_of_instances"] = int(ref["number_of_instances"])
    ref["agent_is_active"] = ref["agent_is_active"].upper()

  def die (self,name):
    pexit ("Exiting due to Error: bad entry for param_name in ",name,"!\n")

  def after_parse_common(self,tb):

    param_name  = ''
    param_value = ''

    tb['VERNUM'] = VERNUM

    #check for top-level factory overrides
    param_name  = "top_factory_set"
    try:
      param_value = tb[param_name]
      res = re.search(r'\s*(\w+)(\s+|\s*,\s*)([\w\.]+)',param_value)
      if res:
        tb[param_name][res.group(1)] = res.group(3)
        log( "%s = %s %s" % (param_name, res.group(1), res.group(3) ) )
      else:
        die(tb['template_name'])
    except: pass

    #check for ref_model inputs
    param_name  = "ref_model_input"
    try:
      param_list = tb[param_name]
      for param_value in param_list:
        res = re.search(r'\s*(\w+)(\s+|\s*,\s*)([\w\.]+)',param_value )
        if res:
          try:    tb[ref_model][res.group(1)]
          except: tb[ref_model][res.group(1)] = res.group(3)
          log( "%s = %s %s" % (param_name, res.group(1), res.group(3) ) )
        else:
          die(tb['template_name'])
    except: pass

##    try:
##      tb['common_pkg']['name'] = re.sub(r'\.sv', '' , tb['common_pkg']['file'] )
##    except: pass
##    
##    try:
##      tb['common_env_pkg']['name'] = re.sub(r'\.sv', '' , tb['common_env_pkg']['file'] )
##    except: pass

    #check for ref_model outputs
    param_name  = "ref_model_output"
    try:
      param_value = tb[param_name]
      res =re.search(r'\s*(\w+)(\s+|\s*,\s*)([\w\.]+)', param_value)
      if res:
          try:    tb[ref_model][res.group(1)]
          except: tb[ref_model][res.group(1)] = 1

          tb[param_name][res.group(1)].append(res.group(3))
          log( "%s = %s %s" % (param_name, res.group(1), res.group(3) ) )
      else:
        die (tb['template_name'])
    except: pass


    #check for ref_model compare method
    param_name  = "ref_model_compare_method"
    try:
      param_value = tb[param_name]
      res = re.search(r'\s*(\w+)(\s+|\s*,\s*)([\w\.]+)',param_value)
      if res:
          try:     tb[ref_model][res.group(1)]
          except:  tb[ref_model][res.group(1)] = 1
          tb[param_name][res.group(1)] = res.group(3)
          log( "%s = %s %s" % (param_name, res.group(1), res.group(3) ) )
      else:
        die (tb['template_name'])
    except: pass

    if ( edef(tb , 'top_env_generate_methods_after_class' , "NO" )):

      if defined(tb,'top_env_prepend_to_build_phase'):
        pexit ("ERROR in "+tb['tpl']+": top_env_prepend_to_build_phase cannot be used in combination with top_env_generate_methods_after_class = no")


      if defined(tb,'top_env_append_to_build_phase'):
        pexit ("ERROR in "+tb['tpl']+": top_env_append_to_build_phase cannot be used in combination with top_env_generate_methods_after_class = no")


      if defined(tb,'top_env_append_to_connect_phase'):
        pexit ("ERROR in "+tb['tpl']+": top_env_append_to_connect_phase cannot be used in combination with top_env_generate_methods_after_class = no")


      if defined(tb,'top_env_append_to_run_phase'):
        pexit ("ERROR in "+tb['tpl']+": top_env_append_to_run_phase cannot be used in combination with top_env_generate_methods_after_class = no")


      if ( edef(tb , 'test_generate_methods_after_class' , "NO" ) ):

        if defined(tb,'test_prepend_to_build_phase'):
          pexit ("ERROR in "+tb['tpl']+": test_prepend_to_build_phase cannot be used in combination with test_generate_methods_after_class = no")


        if defined(tb,'test_append_to_build_phase'):
          pexit ("ERROR in "+tb['tpl']+": test_append_to_build_phase cannot be used in combination with test_generate_methods_after_class = no")


    if ( tb['split_transactors'] == "YES" ):
      tb['dual_top'] = "YES"

    if defined(tb,'vlog_option'): tb['vlog_option'] = sjoin(' ',tb['vlog_option'])
    else: tb['vlog_option'] = ""

    if defined(tb,'vcom_option'): tb['vcom_option'] = sjoin(' ',tb['vcom_option'])
    else: tb['vcom_option'] = ""

    if defined(tb,'vsim_option'): tb['vsim_option'] = sjoin(' ',tb['vsim_option'])
    else: tb['vsim_option'] = ""

    if defined(tb,'vopt_option'): tb['vopt_option'] = sjoin(' ',tb['vopt_option'])
    else: tb['vopt_option'] = ""

    tb['env_list']        = []
    tb['env_list_agent']  = {}

  def after_parse_agent(self,agent,tb):
    global global_continuous
#TBD check_dir(tb['inc_path'],agent['agent_name'])
#TBD check_dir(tb['project'],"tb","include",agent['agent_name'])

    agent['project']              = tb['project']
    agent['inc_path']             = tb['inc_path']
    agent['print_date']           = tb['print_date']
    agent['copyright']            = tb['copyright']
    agent['author']               = tb['author']
    agent['email']                = tb['email']
    agent['tel']                  = tb['tel']
    agent['dept']                 = tb['dept']
    agent['company']              = tb['company']
    agent['year']                 = tb['year']
    agent['VERNUM']               = tb['VERNUM']
    agent['date']                 = tb['date']
    agent['version']              = tb['version']
    agent['script_version']       = tb['script_version']
    agent['repository_version']   = tb['repository_version']
    agent['code_version']         = tb['code_version']
    agent['test_spec_version']    = tb['test_spec_version']
    agent['tb_description']       = tb['description']
    agent['generate_file_header'] = tb['generate_file_header']
    agent['agent_if']             = agent['agent_name']+ "_if"
    agent['item']                 = agent['agent_name']+ '_' +agent['trans_item']

    agent['clock_array']          = []
    agent['clist']                = []
    agent['env_clock_list']       = ''
    agent['reset_array']          = []
    agent['rlist']                = []
    agent['env_reset_list']       = ''
    agent['env_list']             = []
    agent['env_list_agent']       ={}

    try:    agent['if_instance_names']
    except: agent['if_instance_names'] = []

    agent['if_instance_names'].append(agent['agent_if']+ "_0")
    #number of instances of the agent and its interface
    if defined( agent , 'number_of_instances' ):
      if ( agent['number_of_instances'] > 1):
        for a in range(1,agent['number_of_instances']):
            agent['if_instance_names'].append(agent['agent_if'] + "_" +str(a) )
      else: agent['number_of_instances'] = 1

    try:    tb['all_agent_ifs']
    except: tb['all_agent_ifs'] = []

    if ( tb['split_transactors'] == "YES" ):
        tb['all_agent_ifs'].append(agent['agent_name']+"_bfm" )
    else:
        tb['all_agent_ifs'].append( agent['agent_if'] )

    #check if other agents to be added to same env
    if defined( agent,'additional_agent'):
      try:    agent['additional_agents']
      except: agent['additional_agents'] = []
      try:    agent['parent']
      except: agent['parent'] = {}

      agent['additional_agents'].append(agent['additional_agent'])
      if not ( agent['additional_agent'] in agent['parent'] ):
        agent['parent'][ agent['additional_agent'] ] = agent['agent_name']

      else:
        warning_prompt("An agent should not appear as an additional_agent more than once:", agent['additional_agent'] ,"is an additional_agent in ",agent['agent_name'] +" and "+ agent['parent'][agent['additional_agent']])

    #check for if_clock
    if defined( agent,'if_clock'):
      agent['if_clock'] = re.sub(r'[\s;]','',agent['if_clock'])
      temp = agent['if_clock'].split(',')
      agent['clock'] = temp[0]
      if len(temp)>=2: agent['clock_port'] = temp[1]
      else:       agent['clock_port'] = 'clock'
      log( "IF_CLOCK: ",agent['clock'],' = ',agent['clock_port'])
      agent['clock_array'].append(agent['clock'])
      agent['env_clock_list'] += sjoin(' ',(agent['agent_name'],agent['clock'],agent['clock_port']))

      log( "env_clock_list: " , agent['env_clock_list'])

    if ( 'env_clock_list' in agent ):
      temp = re.sub(r'^\s*','',agent['env_clock_list'])
      temp = re.sub(r'\s*$','',temp)
      temp = re.sub(r'\s+','|',temp)
      agent['clist'] = temp.split('|')
      log( "clist :" + agent['env_clock_list'])

    #check for if_reset
    if defined( agent,'if_reset'):
      agent['if_reset'] = re.sub(r'[\s;]','',agent['if_reset'])
      temp = agent['if_reset'].split(',')
      agent['reset'] = temp[0]
      if len(temp)>=2: agent['reset_port'] = temp[1]
      else:       agent['reset_port'] = 'reset'
      log( "IF_RESET: ",agent['reset'],' = ',agent['reset_port'])

      agent['reset_array'].append(agent['reset'])
      agent['env_reset_list'] += sjoin(' ',(agent['agent_name'],agent['reset'],agent['reset_port']))

      log( "env_reset_list: " , agent['env_reset_list'])

    if ( 'env_reset_list' in agent ):
      temp = re.sub(r'^\s*','',agent['env_reset_list'])
      temp = re.sub(r'\s*$','',temp)
      temp = re.sub(r'\s+','|',temp)
      agent['rlist'] = temp.split('|')
      log( "rlist:" + agent['env_reset_list'])

    #check for active/passive agent
    if defined( agent,'agent_is_active' ):
      value = agent['agent_is_active']
      if ( value  != "UVM_ACTIVE" and value != "UVM_PASSIVE" ):
        warning_prompt("agent_is_active = ",value," ! must be either UVM_ACTIVE or UVM_PASSIVE in template file: ",agent['template_name'])
      if not defined(tb,'active'):tb['active'] = {}
      tb['active'][agent['agent_name']] = agent['agent_is_active']

    #check for reg_access (gives addr map in uvm_reg)
    if defined( agent,'reg_access_name' ):
      print("reg_access_name in "+ agent['template_name'] +"still works but is deprecated.")
      print("Use reg_access_mode instead. You can also set reg_access_block_type, reg_access_block_instance, and reg_access_map")
      res = re.search(r'\s*(\w+)(\s+|\s*,\s*)(\w+)', agent['reg_access_name'])
      if not res: pexit("Exiting due to Error: bad entry for ",agent['reg_access_name']," of ",agent['template_name'],"!")
      if not ( ndef(agent, 'reg_access_mode', res.group(3)) ):
        agent['reg_access_name'] = res.group(3)
      else:
        warning_prompt("reg_access_name sets mode to ",res.group(3)," in ",agent['template_name']," but it is already set to a different value!",  agent['reg_access_mode'])
      log("reg_access_name: ",agent['reg_access_mode'])

    #check for reg_access (gives addr map in uvm_reg)
    if defined( agent,'reg_access_name'):
      print("reg_access_name in ",agent['template_name']," still works but is deprecated.")
      print("Use reg_access_mode instead. You can also set reg_access_block_type, reg_access_block_instance, and reg_access_map")
      res = re.search(r'\s*(\w+)(\s+|\s*,\s*)(\w+)', agent['reg_access_name'] )
      if not res: pexit ("Exiting due to Error: bad entry for agent['reg_access_name'] of agent['template_name']!")
      if not ( ndef(agent,'reg_access_mode' , res.group(3) ) ):
        agent['reg_access_name'] = res.group(3)
      else:
        warning_prompt("reg_access_name sets mode to ",res.group(3)," in ",agent['template_name']," but it is already set to a different value!",  agent['reg_access_mode'])
      log( "reg_access_name: ",agent['reg_access_mode'])


    if defined( agent,'reg_access_block_type' ):
      res = re.search(r'\s*(\w+)', agent['reg_access_block_type'] )
      if not res: pexit ("Exiting due to Error: bad entry for agent['reg_access_block_type'] of agent['template_name']!")
      if not ( ndef(agent,'reg_access_block_type' , re.groupp(1)) ):
        agent['reg_access_block_type'] = re.groupp(1)
      else:
        warning_prompt("reg_access_block_type set to ",re.groupp(1)," in ",agent['template_name']," but it is already set to a different value!",  agent['reg_access_block_type'])
      log("reg_access_block_type: ",re.groupp(1))

    if defined( agent,'reg_access_block_instance'):
      res = re.search(r'\s*([\w\.]*)', agent['reg_access_block_instance'])
      if not res: pexit("Exiting due to Error: bad entry for ",agent['reg_access_block_instance']," of ",agent['template_name'],"!")
      instance = res.group(1)
      #if ( instance != "" ):
        #if ( substr($instance, 0, 1)!="." ):
        # instance = "."+instance
      if not ( ndef(agent,'reg_access_block_instance' , instance) ):
        agent['reg_access_block_instance'] = instance
      else:
        warning_prompt("reg_access_block_instance set to ",re.groupp(1)," in ",agent['template_name']," but it is already set to a different value",  agent['reg_access_block_instance'])
      log("reg_access_block_instance: ", instance)

    if defined( agent,'reg_access_mode'):
      res = re.search(r'\s*(\w+)', agent['reg_access_mode'] )
      if not res: pexit ("Exiting due to Error: bad entry for ",agent['reg_access_mode']," of ",agent['template_name'],"!")
      if not ( ndef( agent,'reg_access_mode' , res.group(1) )):
        agent['reg_access_mode'] = res.group(1)
      else:
        warning_prompt("reg_access_mode set to ",re.groupp(1)," in ",agent['template_name']," but it is already set to a different value",  agent['reg_access_mode'])
      log("reg_access_mode: ",res.group(1))

    #check for factory overrides
    if defined( agent,'agent_factory_set'):
      res = re.search(r'\s*(\w+)(\s+|\s*,\s*)(\w+)', agent['agent_factory_set'])
      if not res: pexit ("Exiting due to Error: bad entry for ",agent['agent_factory_set']," of ",agent['template_name'],"!")
      if (res.group(3)):
        N = res.group(3)
        if ( "user_defined_sequence_class" == N ): N = agent['agent_name'] + "_test_seq"
        agent['factory_set'][res.group(1)] = N
        agent['agent_seq_inc']['agent_factory_set'] = N
      else:
        agent['factory_set'][res.group(1)] = res.group(3)
        if res.group(3): agent['agent_seq_inc']['agent_factory_set'] = res.group(3)

    if ('reg_access_mode' in agent):

      agent['bus2reg_map'] = {'data' : agent['uvm_reg_data'],
                              'addr' : agent['uvm_reg_addr'],
                              'kind' : agent['uvm_reg_kind']
                             }

      if ( len(agent['additional_agents']) ):
          warning_prompt("additional_agent and reg_access_name/mode/type/instance are mutually exclusive and should not be used in the same template file: ",  agent['template_name'])

      if not ( 'reg_access_instance' in agent):
          agent['reg_access_instance'] = "."+agent['agent_name']

      if not ( 'reg_access_map' in agent):
          agent['reg_access_map'] = agent['agent_name']+"_map"

      if not ( 'reg_access_block_type' in agent):
          warning_prompt("reg_access_name or reg_access_mode are set without setting reg_access_block_type or regmodel_sub_block in template file: ",  agent['template_name'])

      if ( agent['number_of_instances'] > 1 ):
          warning_prompt("Agent ",agent['agent_name']," uses reg_access_* but has number_of_instances = ",agent['number_of_instances']," in ",agent['template_name'],
                         " reg_access_instance and reg_access_map will get the suffix _N. This will change in future versions of the generator.")

      if ( agent['agent_has_env'] == "NO" ):
            print("Forcing agent_has_env = yes for agent ",agent['agent_name']," because the agent uses register access")

      if ( agent['agent_has_env'] == "YES"):
        if ( edef(agent,'agent_is_active',"UVM_PASSIVE") ):
          warning_prompt("Agent ",agent['agent_name']," uses reg_access_* but has agent_is_active = UVM_PASSIVE in template file: ", agent['template_name'])
    else:
      if ( 'reg_access_block_type' in agent):
          warning_prompt("reg_access_block_type or regmodel_sub_block are set without setting reg_access_name or reg_access_mode in template file:", agent['template_name'])

      if ( 'reg_access_map' in agent):
          warning_prompt("reg_access_map is set without setting reg_access_name or reg_access_mode in template file:", agent['template_name'])

      if ( 'reg_access_instance' in agent):
          warning_prompt("reg_access_block_instance is set without setting reg_access_name or reg_access_mode in template file:", agent['template_name'])

    # Build hash of agent types indexed by agent instance name
    for i in range(0,agent['number_of_instances']):
      suffix = calc_suffix(i, agent['number_of_instances'])
      if ( edef(agent,'agent_has_env',"NO") ):
          instance = "m_"+agent['agent_name']+str(suffix)+"_agent"
      else:
          instance = "m_"+agent['agent_name']+"_env.m_"+agent['agent_name']+str(suffix)+"_agent"
      if not 'type_by_inst' in agent: agent['type_by_inst'] = {}
      agent['type_by_inst'][instance] = agent['agent_name']
      if not 'instance_names' in agent: agent['instance_names'] = []
      agent['instance_names'].append(instance)

    if edef(agent,'agent_has_env',"NO") :
      if not 'stand_alone_agents' in agent: agent['stand_alone_agents']=[]
      agent['stand_alone_agents'].append(agent['agent_name'])
    else:
        agent['env_list'].append(agent['agent_name']+"_env" )
        agent['env_list_agent'][agent['agent_name']+"_env"] = agent['agent_name']
        tb['env_list'].append(agent['agent_name']+"_env" )
        tb['env_list_agent'][agent['agent_name']+"_env"] = agent['agent_name']


    if ( 'additional_agents' in agent and len(agent['additional_agents']) ):
        # Array of additional_agents
        log(agent['agent_name'],"_env has other agents: ",agent['additional_agents'])
        # Hash env_agents needs to store a copy of the additional_agents array per-agent
        agent['copy_array'] = agent['additional_agents'].copy()
        if not 'env_agents' in agent:agent['env_agents']={}
        agent['env_agents'][agent['agent_name']+"_env"] = agent['copy_array']
        if ( edef(agent,'agent_has_env', "NO") ):
          warning_prompt("Agent ",agent['agent_name']," has an additional_agent ",agent['additional_agents']," and hence should have agent_has_env = yes")

        for extra_agent in agent['additional_agents']:
          if extra_agent != None:
            instance = "m_"+agent['agent_name']+"_env.m_"+extra_agent+"_agent"
            agent['type_by_inst'][instance] = agent['agent_name']
            agent['instance_names'].append(instance)

    if ( edef(agent,'agent_generate_methods_after_class', "NO") ):
        if ( 'agent_prepend_to_build_phase' in agent ):
          pexit("ERROR in ",agent['template_name'],". agent_prepend_to_build_phase cannot be used in combination with agent_generate_methods_after_class = no")

        if ( 'agent_append_to_build_phase' in agent ):
          pexit("ERROR in ",agent['template_name'],". agent_append_to_build_phase cannot be used in combination with agent_generate_methods_after_class = no")

        if ( 'agent_append_to_connect_phase' in agent ):
          pexit("ERROR in ",agent['template_name'],". agent_append_to_connect_phase cannot be used in combination with agent_generate_methods_after_class = no")


    if not ( edef(agent,'uvm_seqr_class',"YES") ):
      if ( 'agent_seqr_inc_before_class' in agent
        or 'agent_seqr_inc_inside_class' in agent
        or 'agent_seqr_inc_after_class'  in agent ):

        pexit("ERROR in ",agent['template_name'],". The sequencer_inc_before/inside/after_class include files can only be used in combination with uvm_seqr_class = yes")

    if ( edef (agent,'agent_env_generate_methods_after_class', "NO") ):
      if ( 'agent_env_prepend_to_build_phase' in agent):
        pexit( "ERROR in ",agent['template_name'],". agent_env_prepend_to_build_phase cannot be used in combination with agent_env_generate_methods_after_class = no")

      if ( 'agent_env_append_to_build_phase' in agent):
        pexit( "ERROR in ",agent['template_name'],". agent_env_append_to_build_phase cannot be used in combination with agent_env_generate_methods_after_class = no")

      if ( 'agent_env_append_to_connect_phase' in agent):
        pexit( "ERROR in ",agent['template_name'],". agent_env_append_to_connect_phase cannot be used in combination with agent_env_generate_methods_after_class = no")

    for i in ( "trans_var"           ,
               "trans_meta"          ,
               "trans_enum_var"      ,
               "trans_enum_meta"     ,
               "trans_var_constraint",
               "config_var"          ):
      p=0
      agent[i+'_default']=[]
      for v in agent[i]:
        v = re.sub(r';\s*$','',v)
        v = re.sub(r'\s*$','',v)
        res = re.search(r'(.*)\s*=\s*(.*)', v)
        if res:
          v = res.group(1) +' = '+ res.group(2)
          agent[i][p] = res.group(1)
          agent[i+'_default'].append(res.group(2))
        else:
          agent[i][p] = v
          agent[i+'_default'].append(None)
        p+=1

    if ( "if_port" in agent ):
      agent["port_list"]=[]

      for i in agent["if_port"]:
        resc = re.search(r'\b'+agent["clock"]+r'\b' ,i)
        resr = re.search(r'\b'+agent["reset"]+r'\b',i)
        if resc or resr:
          #print(resc,resr)
          continue
         
        port = {
          "io"      : "in",
          "rst_val" : "0",
          "rst_name": "",
          "range"   : ""
        }
        
        res   = re.search(r'(.*)\s*;\s*(.*)',i)
        logic = res.group(1).strip()
        val   = res.group(2).strip()
       
        #res = re.search(r'(.*\S)\s+(\w+)\s*(=(.*))?$',logic)
        res = re.search(r'(.*\S)\s+([\w\[:\]]+)\s*(=(.*))?',logic)
        #res = re.search(r'(.*\S)\s+(\w+)\s*(\[[\w: ]\])?\s*(=(.*))?$',logic)
        #res = re.search(r'(.*\S)\s+(\w+)\s*(\[[\w: ]\])?\s*(=(.*))?',logic)
        
        if res:
          port["logic"] = res.group(1)
          port["name"]  = res.group(2)
          port["default_val"] = res.group(4)
          port["rst_name"] = "rst_" + res.group(2).strip()
        else:
          pexit("error in ",agent['tpl']," in if_port = ",i)
          
        res = re.search(r'(\[.*\])',logic)
        if res:
          port["range"] = res.group(1)
          
        res = re.search(r'\bo_(\w+)',logic)
        if res: 
          port["io"] = "out"
          port["rst_name"] = "rst_" + res.group(1)

        res = re.search(r'//\s*(out|in|inout)\s*:=\s*(\S+)',val)
        if res: 
          port["io"]      = res.group(1).strip()
          port["rst_val"]  = res.group(2).strip()
       
        agent["port_list"].append(port)
    #print(agent["port_list"])

#----------------------------------------------------------------------
if __name__ == '__main__':

  from uvm_user_if    import * # for uvm_common uvm_main uvm_support!
  args = uvm_user_if(sys.argv[0]).args


  obj = uvm_create_db(args.common,args.agent)
  #obj = uvm_create_db('common.tpl',('mlvds.tpl','cfg_mem.tpl', 'target.tpl'))
  #-a mlvds.tpl cfg_mem.tpl target.tpl

  db = obj.get_db()
  if 0:
   for x in db:
    print ("\n\n==> ",x,"\n\n")
    for a in db[x]:
      print (a , db[x][a])


  json.dump(db,open("py_dump.json","w"),indent=3,sort_keys=True)
