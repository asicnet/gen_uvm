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

""" Generator module to create an uvm Top-Level directory

uvm_top.py 
Version 1.0.0

"""

from header_cfg import *

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
  print("-- use ",tmplt_include_file_name)
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
  print("\n!!! Es wird das interne uvm_template verwendet !!!\n\n")

from uvm_base import *

class TOP(UVM_BASE):
  '''Class for TOP Generator
  The the data base is given to create a top directory structure
  '''

  def __init__(self, database, verbose='info',ind=3):
      '''Define objekt variables and print debug infos
      '''
      UVM_BASE.__init__(self, database, verbose,ind)
      #UVM_BASE.__init__( self, self.db, verbose=self.verbose,ind=self.ind)

      #self.verbose = verbose
      #self.ind=ind
      #self.db = database
      #self.tb = database['top']
      #if ind:
      #    self.indstr=' '*ind
      #
      #if severityLevel(self.verbose,'debug'):
      #    class_name = self.__class__.__name__
      #    print_fc(class_name + ' created','gr')

  def gen_top_dir(self,ag):
    top = self.db[ag]
    log( "Reading: top\n" + top['agent_name'])
    dir = top['project']+"/tb/"+top['agent_name']
    self.dir = dir
    log( "dir: ",dir,"\n")
    makedir( dir,       )
    makedir( dir + "/sv")
    if edef (top,'top_has_test' , "YES"):
        makedir( dir + "/sv/test")
        makedir( dir + "/sv/test/sequences")
        makedir( dir + "/sv/test/tests")
        makedir( dir + "/sv/test/tests_sequences")



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

  def insert_inc_file_ (self, FH, indent, param_name, ref, tbdir=""):
    #print (indent, param_name)
    fname = None
    dname = fname
    inline = 0

    if (defined(param_name) and param_name in ref ):
      if defined(ref[param_name],'file') :
        fname = ref[param_name]['file']
        dname = fname
        if ref[param_name]['inline'] != "0" : inline = ref[param_name]['inline']
        else: inline = ""
         
    if defined(fname):
       self.gen_template(param_name,ref)  # kann sein dass common_define nicht geht!

    if defined(fname):
      if defined(tbdir) and tbdir == "dut":
        fname    =  "../"+tbdir+'/'+fname
        fullname = ref['project'] + "/dut/"+dname
      else:  
        fname    = ref['agent_name']+'/'+fname
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

  def gen_regmodel(self):
        print ("Register Model is not implemented yet!")
#        tb = self.db['top']
#        db = self.db
#        #gen_regmodel_pkg()
#        #for agent in reg_access_mode
#
#        for ag in db:
#            agent = db['ag']
#            agent_name = agent['agent_name']
#            #gen_env()
#            #gen_regmodel_adapter()
#            #gen_regmodel_coverage()
#            #gen_regmodel_seq_lib()
#
#
#  def gen_regmodel_pkg(self,a)
#  def gen_env(self,a)
#  def gen_regmodel_adapter(self,a)
#  def gen_regmodel_coverage(self,a)
#  def gen_regmodel_seq_lib(self,a)

  def extra_checking_for_additional_agents (self):
    tb = self.db['top']
    db = self.db

    tb['top_env_agents']=[]

    for agent in tb['stand_alone_agents']:
      if not( defined (tb,'agent_parent') and agent in tb['agent_parent']):
        tb['top_env_agents'].append( agent )

    # Check for agent with agent_has_env = yes being used as an additional_agent
    for agent in tb['agent_list']:
      if mdefined ( tb , 'agent_parent', agent):
        for saa in tb['stand_alone_agents']:
          if not re.search(f'{agent}', saa):
            warning_prompt("Agent "+ agent + " is used as an additional_agent (in "+ tb['agent_parent'][agent] + ") and hence should itself have agent_has_env = no")

        if mdefined( db , agent ,'number_of_instances') and db[agent]['number_of_instances'] > 1 :
          warning_prompt("Agent "+ agent + " is used as an additional_agent (in "+ tb['agent_parent'][agent] + ") and hence should itself have number_of_instances = 1")


#sub extra_checking_for_additional_agents {
#  my tb = shift;
#  my db = shift;
#
#    foreach my $agent (@{tb->{stand_alone_agents}}) {
#        push( @{tb->{top_env_agents}}, $agent )
#          unless grep( /$agent/, keys(%{tb->{agent_parent}}) );
#    }
#
#    # Check for agent with agent_has_env = yes being used as an additional_agent
#    foreach my $agent (@{tb->{agent_list}}) {
#        if ( exists tb->{agent_parent}{$agent} ) {
#            unless ( grep( /$agent/, @{tb->{stand_alone_agents}} ) ) {
#                warning_prompt("Agent ${agent} is used as an additional_agent (in tb->{agent_parent}{$agent}) and hence should itself have agent_has_env = no");
#            }
#            if ( db->{$agent}->{number_of_instances} > 1 ) {
#                warning_prompt("Agent ${agent} is used as an additional_agent (in tb->{agent_parent}{$agent}) and hence should itself have number_of_instances = 1");
#            }
#        }
#    }
#}
#



  def gen_top_config(self):
    db = self.db
    tb = self.db['top']

    dir = tb['project'] + "/tb/" + tb['top_name']+ "/sv/"
    file= Path(dir + tb['top_name'] + "_config.sv" )
    FH = file.open('w')
    self.write_file_header(FH, tb, tb['top_name']+"_config.sv", "Configuration for  "+ tb['top_name'] )

    FH.write("`ifndef " + tb['top_name'].upper()+ "_CONFIG_SV\n")
    FH.write("`define " + tb['top_name'].upper()+ "_CONFIG_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH,"", "top_env_config_inc_before_class", tb)

    FH.write("class "+ tb['top_name'] + "_config extends uvm_object;\n")
    FH.write("\n")
    FH.write("  // Do not register config class with the factory\n")
    FH.write("\n")

    all_agent_ifs = len(tb['agent_list'])#all_agent_ifs ??

    if edef(tb,'nested_config_objects',"YES"):

      for i in range(0,all_agent_ifs): #all_agent_ifs ??
          agent = tb['agent_list'][i]               #agent_list??
          ref = db[agent]

          for j in range(0,ref['number_of_instances']):
              suffix = calc_suffix(j, ref['number_of_instances'])
              align("  rand "+ agent + "_config  ", "m_"+ agent + suffix + "_config;", "")
      gen_aligned(FH)
      FH.write("\n")
    else:

        for i in range(0,all_agent_ifs):
            agent = tb['agent_list'][i]
            ref = db[agent]

            for j in range(0,ref['number_of_instances']):
                suffix = calc_suffix(j, ref['number_of_instances'])
                align("  virtual "+ tb['all_agent_ifs'][i] + "  ", agent+suffix+"_vif;", "")

        for i in range(0,all_agent_ifs):
            agent = tb['agent_list'][i]
            ref = db[agent]
            for j in range(0,ref['number_of_instances']):
                suffix = calc_suffix(j, ref['number_of_instances'])
                align("  uvm_active_passive_enum  ", "is_active_"+ agent+suffix, "= UVM_ACTIVE;")

        for i in range(0,all_agent_ifs):
            agent = tb['agent_list'][i]
            ref = db[agent]
            for j in range(0,ref['number_of_instances']):
                suffix = calc_suffix(j, ref['number_of_instances'])
                align("  bit  ", "checks_enable_"+ agent+suffix + ";", "")

        for i in range(0,all_agent_ifs):
            agent = tb['agent_list'][i]
            ref = db[agent]
            for j in range(0,ref['number_of_instances']):
                suffix = calc_suffix(j, ref['number_of_instances'])
                align("  bit  ", "coverage_enable_"+ agent+suffix + ";", "")
                align("  int  ", "build_in_bug_"+ agent+suffix + ";", "")
                align("  int  ", "execution_mode_"+ agent+suffix + ";", "")

        for i in range(0,all_agent_ifs):
            agent = tb['agent_list'][i]
            ref = db[agent]
            for j in range(0,ref['number_of_instances']):
                suffix = calc_suffix(j, ref['number_of_instances'])
                align("  bit  ", "coverage_enable_"+ agent+suffix + ";", "")

        gen_aligned(FH)
        FH.write("\n")

    if not (defined(tb, 'config_var') and tb['config_var']):
        FH.write("  // You can insert variables here by setting config_var in file "+ tb['tpl'] + "\n")

    for var_decl in  tb['config_var']:
        ar = var_decl.split('=')
        align("  ", ar[0], " = ", ar[1])
    gen_aligned(FH)
    FH.write("\n")

    cvar={}
    for var_decl in  tb['config_var']:
        print (var_decl)
        res = re.search(r'([\[\]\w]+)\s*=\s*(.+)',var_decl)
        if res: cvar[res.group(1)] = res.group(2)
        else: print ("Error in var_decl :" ,var_dec)
          
    if not edef(tb,'top_env_config_generate_methods_inside_class',"NO"):
        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("  // You can remove new by setting top_env_config_generate_methods_inside_class = no in file "+ tb['tpl'] + "\n\n")

        FH.write("  extern function new(string name = \"\");\n")
        FH.write("\n")

    self.insert_inc_file(FH,"  ",  "top_env_config_inc_inside_class", tb)

    FH.write("endclass : " + tb['top_name'] + "_config \n")
    FH.write("\n")
    FH.write("\n")

    if not edef(tb,'top_env_config_generate_methods_after_class',"NO"):
        if not edef(tb,'comments_at_include_locations' ,"NO"):
            FH.write("// You can remove new by setting top_env_config_generate_methods_after_class = no in file "+ tb['tpl'] + "\n\n")

        FH.write("function "+ tb['top_name'] + "_config::new(string name = \"\");\n")
        FH.write("  super.new(name);\n")
        FH.write("\n")
        if edef(tb,'nested_config_objects' ,"YES"):
            for i in range(0,all_agent_ifs):
                agent = tb['agent_list'][i]
                ref = db[agent]
                for j in range(0,ref['number_of_instances']):
                    suffix = calc_suffix(j, ref['number_of_instances'])
                    align("  m_" + agent+suffix + "_config ", "= new(\"m_" + agent+suffix + "_config\");", "")

                    value=None

                    if defined ( ref , 'agent_is_active'):
                        value = ref['agent_is_active']
                    else :
                        value = "UVM_ACTIVE"
                    align("  m_" + agent+suffix + "_config.is_active ", "= "+ value + ";", "")

                    if edef(ref,'agent_checks_enable',"NO"):
                        value = "0"
                    else :
                        value = "1"
                    align("  m_" + agent+suffix + "_config.checks_enable ", "= "+ value + ";", "")

                    if edef(ref,'agent_coverage_enable',"NO"):
                        value = "0"
                    else :
                        value = "1"
                    align("  m_" + agent+suffix + "_config.coverage_enable ", "= "+ value + ";", "")
                                        
                    value = agent+"_if"+suffix
                    align("  m_" + agent+suffix + "_config.if_name ", "= \""+ value + "\";", "")

                    if defined(cvar,'build_in_bug'):
                        value = "build_in_bug"
                    else :
                        value = "0"
                    align("  m_" + agent+suffix + "_config.build_in_bug ", "= "+ value + ";", "")

                    if defined(cvar,'execution_mode'):
                        value = "execution_mode"
                    else :
                        value = "0"
                    align("  m_" + agent+suffix + "_config.execution_mode ", "= "+ value + ";", "")

                    if edef(ref,'agent_scoreboard_enable',"NO"):
                        value = "0"
                    else :
                        value = "1"
                    align("  m_" + agent+suffix + "_config.scoreboard_enable ", "= "+ value + ";", "")
                    
                    align()
            gen_aligned(FH)

        self.insert_inc_file(FH,"  ",  "top_env_config_append_to_new", tb)
        FH.write("endfunction : new\n")
        FH.write("\n")
        FH.write("\n")

    self.insert_inc_file(FH,"",  "top_env_config_inc_after_class", tb)
    FH.write("`endif // " + tb['top_name'].upper()+ "_CONFIG_SV\n")
    FH.write("\n")
    FH.close()



  def gen_port_converter(self):

    db = self.db
    tb = self.db['top']

    if not defined(tb , 'ref_model'):  return

    dir = tb['project'] + "/tb/" + tb['top_name']+ "/sv/"
    file= Path(dir + "port_converter.sv" )
    FH = file.open('w')
    self.write_file_header(FH, tb, "port_converter.sv", "Analysis port type converter class for use with Syosil scoreboard")
    if not defined (tb,'syosil_scoreboard_src_path'):
        warning_prompt("ref_model specified in "+ tb['tpl'] + " but 'syosil_scoreboard_src_path' has not been defined")

    FH.write("`ifndef PORT_CONVERTER_SV\n")
    FH.write("`define PORT_CONVERTER_SV\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("class port_converter #(type T = uvm_sequence_item) extends uvm_subscriber #(T);\n")
    FH.write("  `uvm_component_param_utils(port_converter#(T))\n")
    FH.write("\n")
    FH.write("  // For connecting analysis port of monitor to analysis export of Syosil scoreboard\n")
    FH.write("\n")
    FH.write("  uvm_analysis_port #(uvm_sequence_item) analysis_port;\n")
    FH.write("\n")
    FH.write("  function new(string name, uvm_component parent);\n")
    FH.write("    super.new(name, parent);\n")
    FH.write("    analysis_port = new(\"a_port\", this);\n")
    FH.write("  endfunction\n")
    FH.write("\n")
    FH.write("  function void write(T t);\n")
    FH.write("    analysis_port.write(t);\n")
    FH.write("  endfunction\n")
    FH.write("\n")
    FH.write("endclass\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("`endif // PORT_CONVERTER_SV\n")
    FH.write("\n")
    FH.close()


  def gen_ref_model(self):

    db = self.db
    tb = self.db['top']

    if not defined(tb , 'ref_model'):  return

    for ref_model_name in tb[ref_model]:

      dir = tb['project'] + "/tb/" + tb['top_name']+ "/sv/"
      file= Path(dir + ref_model_name + ".sv" )
      FH = file.open('w')
      self.write_file_header(FH, tb,  ref_model_name + ".sv",  "Reference model for use with Syosil scoreboard")

      if not defined(tb,'syosil_scoreboard_src_path') :
          warning_prompt("ref_model specified in tb['tpl'] but 'syosil_scoreboard_src_path' has not been defined")

      FH.write("`ifndef " + ref_model_name.upper() + "_SV\n")
      FH.write("`define " + ref_model_name.upper() + "_SV\n")
      FH.write("\n")

      insert_inc_file("",  "ref_model_inc_before_class", tb)

      FH.write("\n")

      i = 0
      for inpt in ref_model_inpts[ref_model_name]:
          FH.write("`uvm_analysis_imp_decl(_"+ ref_model_name + "_"+ i + ")\n")
          i+=1

      FH.write("\n")
      FH.write("class "+ ref_model_name + " extends uvm_component\n")
      FH.write("  `uvm_component_utils("+ ref_model_name + ")\n")
      FH.write("\n")
      i = 0
      for inpt in ref_model_inpts[ref_model_name]:
          if not defined(agent_type_by_inst,inpt):
              warning_prompt("ref_model_inpt inpt specified in "+ tb['tpl'] + " cannot be found as the instance name of an agent in the generated code")

          agent[agent_name] = agent_type_by_inst[inpt]
          FH.write("  uvm_analysis_imp_"+ ref_model_name + "_"+ i + " #("+ agent[item] + "_types "+ agent[agent_name]+ ", "+ ref_model_name + ") analysis_export_"+ i + "// inpt\n")
          i+=1

      FH.write("\n")
      i = 0
      for outpt in ref_model_outpts[ref_model_name]:
          agent[agent_name] = agent_type_by_inst[outpt]
          if edef (agent,agent_name, "") :
              warning_prompt("ref_model_inpt outpt specified in "+ tb['tpl'] + " cannot be found as the instance name of an agent in the generated code")

          FH.write("  uvm_analysis_port #(uvm_sequence_item) analysis_port_"+ i + "// outpt\n")
          i+=1

      FH.write("\n")
      FH.write("  extern function new(string name, uvm_component parent)\n")

      i = 0
      for inpt in ref_model_inpts[ref_model_name]:
          agent[agent_name] = agent_type_by_inst[inpt]

          FH.write("  extern function void write_"+ ref_model_name + "_"+ i + "(inpt " + agent[item] +'_types '+ agent[agent_name] + " t)\n")
          i+=1


      FH.write("\n")

      #insert_ref_file("  ", ref_model_inc_inside_class[ref_model_name], ref_model_inc_inside_inline[ref_model_name], "ref_model_inc_inside_class", tb['tpl'])
      print ("insert_ref_file not implemented")
      FH.write("endclass\n")
      FH.write("\n")
      FH.write("\n")
      FH.write("function "+ ref_model_name + "::new(string name, uvm_component parent)\n")
      FH.write("  super.new(name, parent)\n")
      i = 0
      for inpt in ref_model_inpts[ref_model_name]:
          FH.write("  analysis_export_i = new(\"analysis_export_i\", this)\n")
          i+=1

      i = 0
      for outpt in ref_model_outpts[ref_model_name]:
          FH.write("  analysis_port_i   = new(\"analysis_port_"+ i + "\",   this)\n")
          i+=1

      FH.write("endfunction : new\n")
      FH.write("\n")
      FH.write("\n")

      #insert_ref_file("", ref_model_inc_after_class[ref_model_name], ref_model_inc_after_inline[ref_model_name], "ref_model_inc_after_class", tb['tpl'])
      print ("insert_ref_file not implemented")

      FH.write("`endif // " + uc(ref_model_name) + "_SV\n")
      FH.write("\n")




  def gen_top_sb(self):

    db = self.db
    tb = self.db['top']

    dir = tb['project'] + "/tb/" + tb['top_name']+ "/sv/"
    file= Path(dir + tb['sb_top'] + "_scoreboard.sv" )
    FH = file.open('w')
    self.write_file_header(FH, tb, tb['sb_top']+"_scoreboard.sv", "Scoreboard for "+ tb['dut_top'] )

    FH.write("`ifndef " + tb['sb_top'].upper()+ "_SCOREBOARD_SV\n")
    FH.write("`define " + tb['sb_top'].upper()+ "_SCOREBOARD_SV\n")
    FH.write("\n")
    if not defined(tb,'top_env_scoreboard_inc_before_class'): tb['top_env_scoreboard_inc_before_class']={}
    tb['top_env_scoreboard_inc_before_class']['agent_list'] = tb['agent_list']
    tb['top_env_scoreboard_inc_before_class']['sb_top'] = tb['sb_top']
    self.insert_inc_file(FH,"  ", "top_env_scoreboard_inc_before_class", tb)
    FH.write(f"class {tb['sb_top']}_scoreboard extends uvm_scoreboard;\n")
    FH.write("\n")
    FH.write("  `uvm_component_utils(" + tb['sb_top'] + "_scoreboard)\n")
    FH.write("\n")

    for agent in  tb['agent_list']:
        for i in range(0,db[agent]['number_of_instances']):
            suffix = calc_suffix(i, db[agent]['number_of_instances'])
            FH.write(f"  `uvm_analysis_imp_decl(_{agent}{suffix})\n")

    for agent in  tb['agent_list']:
        for i in range(0,db[agent]['number_of_instances']):
            suffix = calc_suffix(i,db[agent]['number_of_instances'])
            FH.write(f"  uvm_analysis_imp_{agent}{suffix} #({db[agent]['item']},{tb['sb_top']}_scoreboard) analysis_export_{agent}{suffix} = new (\"analysis_export_{agent}{suffix}\",this); \n")

    FH.write("\n")
    for agent in  tb['agent_list']:
        for i in range(0,db[agent]['number_of_instances']):
            suffix = calc_suffix(i, db[agent]['number_of_instances'])
            align(f"  {agent}_config ", f"m_{agent}{suffix}_config;", "")
            align(f"  {db[agent]['item']} ", f"m_{agent}{suffix}_item;\n", "")

    gen_aligned(FH)
    if not edef(tb,'top_env_scoreboard_generate_methods_inside_class',"NO" ):
        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("  // You can remove new, write, and report_phase by setting top_scoreboard_generate_methods_inside_class = no in file "+tb['tpl']+"\n\n")

        FH.write("\n")
        for agent_name in tb['agent_list']:
          if db[agent_name]["number_of_instances"]>1:
            for i in range(0,db[agent_name]["number_of_instances"]):
              FH.write(f" {agent_name}  int write_{agent_name}_{i}_cnt     = 0;\n")
          else:
            FH.write(f"  int write_{agent_name}_cnt     = 0;\n")

        FH.write("\n")
        FH.write("  extern function new(string name, uvm_component parent);\n")
        for agent_name in tb['agent_list']:
            FH.write(f"  extern function void write_{agent_name}(input " + db['agent_name']['item'] + " t);\n")

        FH.write("  extern function void build_phase(uvm_phase phase);\n")
        FH.write("  extern function void report_phase(uvm_phase phase);\n")
        FH.write("\n")


    tb['top_env_scoreboard_inc_inside_class']['agent_list'] = tb['agent_list']
    tb['top_env_scoreboard_inc_inside_class']['sb_top'] = tb['sb_top']
    self.insert_inc_file(FH,"  ", "top_env_scoreboard_inc_inside_class", tb)
    FH.write("endclass : " + tb['sb_top'] + "_scoreboard \n")
    FH.write("\n")
    FH.write("\n")
    if not edef(tb,'top_env_scoreboard_generate_methods_after_class',"NO" ):
        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("// You can remove new, write, write_drv and report_phase by setting top_env_scoreboard_generate_methods_after_class = no in file "+tb['tpl']+"\n\n")

        FH.write("function tb['sb_top']_scoreboard::new(string name, uvm_component parent);\n")
        FH.write("  super.new(name, parent);\n")
        FH.write("endfunction : new\n")
        FH.write("\n")
        FH.write("\n")

        for agent_name in  tb['agent_list']:
            FH.write(f"function void {tb['sb_top']}_scoreboard::write_{agent_name}(input {db['agent_name']['item']} t);\n")
            #FH.write("  //if (m_config.scoreboard_enable)\n")
            FH.write(f"  begin\n")
            FH.write(f"    {db['agent_name']['item']} item = t;\n")
            FH.write(f"    \$cast(item,t.clone());\n")
            FH.write(f"    //\$display(\"{agent_name} \",item.sprint());\n")
            FH.write(f"    write_{agent_name}_cnt++;\n")
            FH.write(f"  end\n")
            FH.write(f"endfunction : write_{agent_name}\n")
            FH.write(f"\n")

        FH.write("function void "+tb['sb_top']+"_scoreboard::build_phase(uvm_phase phase);\n")
        for agent_name in tb['agent_list']:
            FH.write(f"  if (!uvm_config_db #({agent_name}_config)::get(this, \"\", \"config\", m_{agent_name}_config))\n")
            FH.write(f"    `uvm_error(get_type_name(), \"{agent_name} config not found\")\n")

        FH.write("endfunction : build_phase\n")
        FH.write("\n")

        w=[]
        wd=[]
        for a in tb['agent_list']:
          w.append("write_{a}_cnt")
          ws.append("write_{a}_drv_cnt")
        for a in {w,wd}:
          str1 += a + '  = %0d  '
          str2 += a + ','

        FH.write(f"function void {tb['sb_top']}_scoreboard::report_phase(uvm_phase phase);\n")
        FH.write(f"    `uvm_info(get_type_name(), \"Scoreboard is enabled for this agent\", UVM_MEDIUM)\n")
        FH.write(f"    `uvm_info(get_type_name(), $sformatf(\"{str1}\",{str2}), UVM_MEDIUM)\n")
        FH.write("endfunction : report_phase\n")
        FH.write("\n")
        FH.write("\n")

    if defined (tb,'top_env_scoreboard_inc_after_class'):
      tb['top_env_scoreboard_inc_after_class']['agent_list'] = tb['agent_list']
      tb['top_env_scoreboard_inc_after_class']['sb_top'] = tb['sb_top']
    self.insert_inc_file(FH,"  ", "top_env_scoreboard_inc_after_class", tb)

    FH.write("`endif // " + tb['sb_top'].upper()+ "_SCOREBOARD_SV\n")
    FH.write("\n")
    FH.close()





  def gen_top_env(self):

    db = self.db
    tb = self.db['top']

    dir = tb['project'] + "/tb/" + tb['top_name']+ "/sv/"
    file= Path(dir + tb['top_name'] + "_env.sv" )
    FH = file.open('w')
    self.write_file_header(FH, tb, tb['top_name']+"_env.sv", "Environment for "+ tb['top_name'] )

    FH.write("`ifndef " + tb['top_name'].upper()+ "_ENV_SV\n")
    FH.write("`define " + tb['top_name'].upper()+ "_ENV_SV\n")
    FH.write("\n")
    self.insert_inc_file(FH,"",  "top_env_inc_before_class", tb)
    FH.write("class "+ tb['top_name'] + "_env extends uvm_env;\n")
    FH.write("\n")
    FH.write("  `uvm_component_utils(" + tb['top_name'] + "_env)\n")
    FH.write("\n")
    FH.write("  extern function new(string name, uvm_component parent);\n")
    FH.write("\n")
    if defined ( tb , 'env_list'):
        FH.write("  // Child environments\n" )
        for agent_env in  tb['env_list']:
            align("  "+agent_env, "m_"+ agent_env + ";", "")

        align("\n", "", "")

    for aname in  tb['agent_list']:
        agent = db[aname]
        for i in range(0,agent['number_of_instances']):
            suffix = calc_suffix(i, agent['number_of_instances'])
            if defined(tb,'top_env_agents') and aname not in tb['top_env_agents']:
                align("  "+aname+"_config  ", f"m_{aname}{suffix}_config;", "")

    align("\n", "", "")
    align("  // Child agents\n", "", "")
    if defined(tb,'top_env_agents'):
      for aname in  tb['top_env_agents']:
          agent = db[aname]
          for i in range(0,agent['number_of_instances']):
              suffix = calc_suffix(i, agent['number_of_instances'])
              align(f"  {aname}_config  "  , f"m_{aname}{suffix}_config;"  , "")
              align(f"  {aname}_agent  "   , f"m_{aname}{suffix}_agent;"   , "")
              align(f"  {aname}_coverage  ", f"m_{aname}{suffix}_coverage;", "")
              align("\n", "", "")

    if edef(tb,'top_env_generate_scoreboard_class', "YES"):
        align("\n  // Scoreboard   \n", "", "")
        align(f"  {tb['sb_top']}_scoreboard ", f"m_{tb['sb_top']}_scoreboard;", "")
        align("  ", " ", " ")

    align("\n  // Config   \n", "", "")
    align(f"  {tb['top_name']}_config ", "m_config;\n", "")
    align("  ", " ", " ")
    gen_aligned(FH)
    if not edef(tb,'top_env_generate_methods_inside_class',"NO"):

        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("\n  // You can remove build/connect/run_phase by setting top_env_generate_methods_inside_class = no in file "+ tb['tpl'] + "\n\n")

        FH.write("  extern function void build_phase(uvm_phase phase);\n")
        FH.write("  extern function void connect_phase(uvm_phase phase);\n")

        if not edef(tb,'top_env_generate_end_of_elaboration',"NO"):
            FH.write("  extern function void end_of_elaboration_phase(uvm_phase phase);\n")

        if not edef(tb,'top_env_generate_run_phase',"NO"):
            FH.write("  extern task          run_phase(uvm_phase phase);\n")

        FH.write("\n")


    self.insert_inc_file(FH,"  ",  "top_env_inc_inside_class", tb)
    FH.write("endclass : " + tb['top_name'] + "_env \n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function "+ tb['top_name'] + "_env::new(string name, uvm_component parent);\n")
    FH.write("  super.new(name, parent);\n")
    FH.write("endfunction : new\n")
    FH.write("\n")
    FH.write("\n")
    if not edef(tb,'top_env_generate_methods_after_class',"NO"):
        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("// You can remove build/connect/run_phase by setting top_env_generate_methods_after_class = no in file "+ tb['tpl'] + "\n\n")

        FH.write("function void "+ tb['top_name'] + "_env::build_phase(uvm_phase phase);\n")
        FH.write("  `uvm_info(get_type_name(), \"In build_phase\", UVM_HIGH)\n")
        FH.write("\n")
        self.insert_inc_file(FH,"  ", "top_env_prepend_to_build_phase", tb)
        FH.write(f"  if (!uvm_config_db #({tb['top_name']}_config)::get(this, \"\", \"config\", m_config)) \n")
        FH.write(f"    `uvm_error(get_type_name(), \"Unable to get {tb['top_name']}_config\")\n")
        for aname in  tb['agent_list']:
            agent = db[aname]
            for i in range(0,agent['number_of_instances']):
                suffix = calc_suffix(i, agent['number_of_instances'])
                align("\n", "", "")
                if edef(agent,'nested_config_objects',"YES"):
                    align(f"  m_{aname}{suffix}_config ", f"= m_config.m_{aname}{suffix}_config;", "")

                else:
                    align(f"  m_{aname}{suffix}_config "           , f"= new(\"m_{aname}{suffix}_config\");", "")
                    align(f"  m_{aname}{suffix}_config.vif "       , f"= m_config.{aname}{suffix}_vif;", "")
                    align(f"  m_{aname}{suffix}_config.is_active " , f"= m_config.is_active_{aname}{suffix};", "")

                if not  edef(agent,'nested_config_objects',"YES"):
                    align(f"  m_{aname}{suffix}_config.checks_enable "  , f"= m_config.checks_enable_{aname}{suffix};", "")
                    align(f"  m_{aname}{suffix}_config.coverage_enable ", f"= m_config.coverage_enable_{aname}{suffix};", "")
                    align(f"  m_{aname}{suffix}_config.build_in_bug "   , f"= m_config.build_in_bug_{aname}{suffix};", "");
                    align(f"  m_{aname}{suffix}_config.execution_mode " , f"= m_config.execution_mode_{aname}{suffix};", "");

                gen_aligned(FH)

            FH.write("\n")
            self.insert_inc_file(FH,"  ","agent_copy_config_vars",agent)
            for i in range(0,agent['number_of_instances']):
                suffix = calc_suffix(i, agent['number_of_instances'])
                if defined(agent,'stand_alone_agents'):
                    aname = agent['stand_alone_agents'][0]
                    # agent_has_env = no
                    if defined(tb,'top_env_agents') and aname in tb['top_env_agents']:
                        # Agent instantiated at top level. Need to set config for agent
                        align(f"  uvm_config_db #({aname}_config)::set(this, \"m_{aname}{suffix}_agent\", \"config\", m_{aname}{suffix}_config);\n", "", "")
                        align(f"  if (m_{aname}{suffix}_config.is_active == UVM_ACTIVE )\n", "", "")
                        align(f"    uvm_config_db #({aname}_config)::set(this, \"m_{aname}{suffix}_agent.m_sequencer\", \"config\", m_{aname}{suffix}_config);\n", "", "")
                        align(f"  uvm_config_db #({aname}_config)::set(this, \"m_{aname}{suffix}_coverage\", \"config\", m_{aname}{suffix}_config);\n", "", "")
                        if edef( tb ,'top_env_generate_scoreboard_class' , "YES"):
                            align(f"  uvm_config_db #({aname}_config)::set(this, \"m_{tb['sb_top']}_scoreboard\", \"config\", m_{aname}{suffix}_config);\n", "", "")
                    elif defined(agent,'agent_parent'):

                        # additional_agent. Need to set config for env that contains agent
                        align(f"  uvm_config_db #({aname}_config)::set(this, \"m_{agent['agent_parent']}_env\", \"config\", m_{aname}_config);\n", "", "")

                else:
                    # agent_has_env = yes. Add config to agent's own env
                    align(f"  uvm_config_db #({aname}_config)::set(this, \"m_{aname}_env\", \"config{suffix}\", m_{aname}{suffix}_config);\n", "", "")
                    if edef( tb ,'top_env_generate_scoreboard_class' , "YES"):
                      align(f"  uvm_config_db #({aname}_config)::set(this, \"m_top_scoreboard\", \"config\", m_{aname}_config);\n", "", "")
                      FH.write("\n")

                gen_aligned(FH)


        FH.write("\n")
        for agent in tb['agent_list']:
          if agent not in tb['stand_alone_agents']:
            align(f"  m_{agent}_env ", f"= {agent}_env", f"::type_id::create(\"m_{agent}_env\", this);")

        if defined(tb,'top_env_agents'):
          for aname in  tb['top_env_agents']:
              agent = db[aname]
              for i in range(0,agent['number_of_instances']):
                  suffix = calc_suffix(i, agent['number_of_instances'])
                  align("\n", "", "")
                  align(f"  m_{aname}{suffix}_agent ",    f"= {aname}_agent   ", f"::type_id::create(\"m_{aname}{suffix}_agent\", this);")
                  align(f"  m_{aname}{suffix}_coverage ", f"= {aname}_coverage", f"::type_id::create(\"m_{aname}{suffix}_coverage\", this);")

        if edef( tb ,'top_env_generate_scoreboard_class' , "YES"):
            align("  m_"+ tb['sb_top'] + "_scoreboard ", "= "+ tb['sb_top'] + "_scoreboard", "::type_id::create(\"m_"+ tb['sb_top'] + "_scoreboard\", this);")

        align("\n", "", "")
        gen_aligned(FH)
        FH.write("\n")
        self.insert_inc_file(FH,"  ", "top_env_append_to_build_phase", tb)
        FH.write("endfunction : build_phase\n")
        FH.write("\n")
        FH.write("\n")
        FH.write("function void "+ tb['top_name'] + "_env::connect_phase(uvm_phase phase);\n")
        FH.write("  `uvm_info(get_type_name(), \"In connect_phase\", UVM_HIGH)\n")
        for aname in  tb['agent_list']:
          if mdefined ( db , aname,'env_list') and len(db[aname]['env_list']) > 0 :
            for env in  db[aname]['env_list']:
              FH.write(f"  `uvm_info(get_type_name(), $sformatf(\"m_{env}: %p\\n\",m_{env}), UVM_HIGH)\n")

        FH.write("\n")
        if edef( tb ,'top_env_generate_scoreboard_class' , "YES") :
          for aname in  tb['agent_list']:
            if mdefined (db , aname,'env_list') and len(db[aname]['env_list']) > 0 :
              for env in  db[aname]['env_list']:
                FH.write(f"  m_{env}.m_" + db[aname]['env_list_agent'][env] + "_agent.analysis_port.connect(m_top_scoreboard.analysis_export_" + db[aname]['env_list_agent'][env]+" );\n")

              FH.write("\n")
        if defined (tb,'top_env_agents'):
          for aname in tb['top_env_agents']:
            agent = db[aname]
            for i in range(0,agent['number_of_instances']):
                suffix = calc_suffix(i, agent['number_of_instances'])
                FH.write(f"  m_{aname}{suffix}_agent.analysis_port.connect(m_{aname}{suffix}_coverage.analysis_export);\n")
                if edef( tb ,'top_env_generate_scoreboard_class' , "YES"):
                    FH.write(f"  m_{aname}{suffix}_agent.analysis_port.connect(m_"+ tb['sb_top'] + f"_scoreboard.analysis_export_{aname}{suffix} );\n")

                FH.write("\n")
        if defined (tb,'top_env_append_to_connect_phase'):
          tb['top_env_append_to_connect_phase']['agent_list'] = tb['agent_list']
          tb['top_env_append_to_connect_phase']['sb_top'] = tb['sb_top']
        self.insert_inc_file(FH,"  ", "top_env_append_to_connect_phase",  tb)

        FH.write("endfunction : connect_phase\n")
        FH.write("\n")
        FH.write("\n")

        if not edef(tb,'top_env_generate_end_of_elaboration',"NO"):
            if not edef(tb,'comments_at_include_locations',"NO"):
                FH.write("// You can remove end_of_elaboration_phase by setting top_env_generate_end_of_elaboration = no in file "+ tb['tpl'] + "\n\n")

            FH.write("function void "+ tb['top_name'] + "_env::end_of_elaboration_phase(uvm_phase phase);\n")
            FH.write("  uvm_factory factory = uvm_factory::get();\n")
            FH.write("  `uvm_info(get_type_name(), \"Information printed from "+ tb['top_name'] + "_env::end_of_elaboration_phase method\", UVM_MEDIUM)\n")
            FH.write("  `uvm_info(get_type_name(), $sformatf(\"Verbosity threshold is %d\", get_report_verbosity_level()), UVM_MEDIUM)\n")
            FH.write("  uvm_top.print_topology();\n")
            FH.write("  factory.print();\n")
            FH.write("endfunction : end_of_elaboration_phase\n")
            FH.write("\n")
            FH.write("\n")

        if not edef(tb,'top_env_generate_run_phase',"NO"):
          if not edef(tb,'comments_at_include_locations',"NO"):
              FH.write("// You can remove run_phase by setting top_env_generate_run_phase = no in file "+ tb['tpl'] + "\n\n")

          FH.write("task "+ tb['top_name'] + "_env::run_phase(uvm_phase phase);\n")
          FH.write("  "+ tb['top_name'] + "_default_seq vseq;\n")
          FH.write("  vseq = "+ tb['top_name'] + "_default_seq::type_id::create(\"vseq\");\n")
          FH.write("  vseq.set_item_context(null, null);\n")
          FH.write("  if ( !vseq.randomize() )\n")
          FH.write("    `uvm_fatal(get_type_name(), \"Failed to randomize virtual sequence\")\n")
          for aname in   tb['agent_list']:
            agent = db[aname]
            if not defined(  agent , 'stand_alone_agents') or aname == "" :
              align(f"  vseq.m_{aname}_env ", f"= m_{aname}_env;", "")

          if defined (tb,'top_env_agents'):
            for aname in  tb['top_env_agents']:
              agent = db[aname]
              for i in range(0,agent['number_of_instances']):
                  suffix = calc_suffix(i, agent['number_of_instances'])
                  align(f"  vseq.m_{aname}{suffix}_agent ", f"= m_{aname}{suffix}_agent;", "")

          align("  vseq.m_config ", "= m_config;", "")
          gen_aligned(FH)
          FH.write("  vseq.set_starting_phase(phase);\n")
          FH.write("\n")
          self.insert_inc_file(FH,"  ", "top_env_append_to_run_phase", tb)
          if not edef(tb,'top_env_append_to_run_phase',"NO"):
            if not edef(tb,'comments_at_include_locations',"NO"):
                FH.write("  // You can remove vseq.start(null) by setting top_env_generate_vseq_start = no in file "+ tb['tpl'] + " if top_env_append_to_run_phase is set\n\n")

            FH.write("  vseq.start(null);\n\n")
          else:
            if not edef(tb,'top_env_generate_vseq_start',"NO"):
              if not edef(tb,'comments_at_include_locations',"NO"):
                FH.write("  // You can remove vseq.start(null) by setting top_env_generate_vseq_start = no in file "+ tb['tpl'] + " if top_env_append_to_run_phase is set\n\n")

              FH.write("  vseq.start(null);\n\n")
            else:
              FH.write("  //vseq.start(null);  //top_env_generate_vseq_start = NO ! \n\n")

          FH.write("endtask : run_phase\n")
          FH.write("\n")
          FH.write("\n")

    self.insert_inc_file(FH,"", "top_env_inc_after_class" , tb)
    FH.write("`endif // " + tb['top_name'].upper()+ "_ENV_SV\n")
    FH.write("\n")
    FH.close()




  def gen_top_seq_lib(self,regmodel=0):
    db = self.db
    tb = self.db['top']

    dir = tb['project'] + "/tb/" + tb['top_name']+ "/sv/"
    file= Path(dir + tb['top_name'] + "_seq_lib.sv" )
    FH = file.open('w')
    self.write_file_header(FH, tb, tb['top_name']+"_seq_lib.sv", "Environment for "+ tb['top_name'] )

    non_reg_env = []
    reg_env     = []
    tbname      = tb['top_name']

    FH.write("`ifndef " + tbname.upper()+ "_SEQ_LIB_SV\n")
    FH.write("`define " + tbname.upper()+ "_SEQ_LIB_SV\n")
    FH.write("\n")
    FH.write("class "+ tbname + "_default_seq extends uvm_sequence #(uvm_sequence_item);\n")
    FH.write("\n")
    FH.write("  `uvm_object_utils(" + tbname + "_default_seq)\n")
    FH.write("\n")
    if ( regmodel ):
        align("  " + top_reg_block_type, "regmodel;", "")

    align("  " + tbname + "_config", " m_config;\n", "")

    for aname in  tb['agent_list']:
        #[aname = agent['agent_name']
        if not aname in tb['stand_alone_agents']:
            align("  " + aname + "_env", " m_" + aname + "_env;", "")

    for aname in  tb['top_env_agents']:
      agent = db[aname]
      for i in range(0,agent['number_of_instances']):
        suffix = calc_suffix(i, agent['number_of_instances'])
        align("  " + aname + "_agent", " m_" + aname + suffix + "_agent;", "")
     # "env_list": [
     #    "adc7172_env"
     # ],
     # "env_list_agent": {
     #    "adc7172_env": "adc7172"
     # },

    for env in  tb['env_list']:
      agent_name = tb['env_list_agent'][env]
      if mdefined(tb , agent_name, 'reg_access_mode' ) :
          reg_env.append( agent_name )
          align("  " + agent_name+ "_default_seq", "m_" + agent_name+ "_seq;", "")

      else :    #env that does not access regmodel
          non_reg_env.append( agent_name )
          align("  " + agent_name+ "_env_default_seq", " m_" + agent_name+ "_env_seq;", "")


    gen_aligned(FH)
    FH.write("\n")
    FH.write("  // Number of times to repeat child sequences\n")
    if defined( tb,'top_default_seq_count'):
        FH.write("  int m_seq_count = "+ tb['top_default_seq_count'] + ";\n")
    else :
        FH.write("  int m_seq_count = 1;\n")
    FH.write("\n")

    if regmodel:
        FH.write("\n")
        FH.write("  // Example built-in register sequences\n")
        FH.write("  //uvm_reg_hw_reset_seq  m_reset_seq;\n")
        FH.write("  //uvm_reg_bit_bash_seq  m_bit_bash_seq;\n")
        FH.write("\n")

    FH.write("  extern function new(string name = \"\");\n")
    FH.write("  extern task body();\n")
    FH.write("  extern task pre_start();\n")
    FH.write("  extern task post_start();\n")
    FH.write("\n")
    FH.write("`ifndef UVM_POST_VERSION_1_1\n")
    FH.write("  // Functions to support UVM 1.2 objection API in UVM 1.1\n")
    FH.write("  extern function uvm_phase get_starting_phase();\n")
    FH.write("  extern function void set_starting_phase(uvm_phase phase);\n")
    FH.write("`endif\n")
    FH.write("\n")
    FH.write("endclass : " + tbname + "_default_seq\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function " + tbname + "_default_seq::new(string name = \"\");\n")
    FH.write("  super.new(name);\n")
    FH.write("endfunction : new\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("task " + tbname + "_default_seq::body();\n")
    FH.write("  `uvm_info(get_type_name(), \"Default sequence starting\", UVM_HIGH)\n")
    FH.write("\n")

    for env in  reg_env + non_reg_env :

        align("  m_" + env + "_env_seq = " + env + "_env_default_seq::type_id::create(\"m_" + env + "_env_seq\");")

        # For the purposes of random stability, although the virtual sequence is actually running on the null sequencer,
        # pretend instead that it is running on the sequencer of the agent.
        # If there are multiple instances of the agent, pick the first
        agent = db[env]
        suffix = calc_suffix(0, agent['number_of_instances'])
        sequencer_instance_name = "m_" + env + "_env.m_" + env + "" + suffix + "_agent.m_sequencer"
        align("  m_" + env + "_env_seq.set_item_context(this, "+sequencer_instance_name+");\n", "", "")
        align("  m_" + env + "_env_seq.set_starting_phase( get_starting_phase() );\n", "", "")

        if ( env in reg_env ):
            for i in range(0,agent['number_of_instances']):
                suffix = calc_suffix(i, agent['number_of_instances'])
                if defined ( env , 'reg_access_instance' ) and env['reg_access_instance']!="":
                    align("  m_" + env + "_env_seq.regmodel" + suffix + " ", "= regmodelenv['reg_access_instance']" + suffix + ";", "")
                else:
                    # If instance = "", use the top-level regmodel
                    align("  m_" + env + "_env_seq.regmodel" + suffix + " ", "= regmodel;", "")
                align("  m_" + env + "_env_seq.m_config" + suffix + " ", "= m_" + env + "_env.m_" + env + "" + suffix + "_agent.m_config;", "")
        align("\n", "", "")

    gen_aligned(FH)
    FH.write("\n")
    FH.write("  repeat (m_seq_count)\n")
    FH.write("  begin\n")
    vseq_list = []
    if (regmodel):
        for env in  (reg_env) :
            FH.write("    if ( !m_" + env + "_env_seq.randomize() )\n")
            FH.write("      `uvm_error(get_type_name(), \"Failed to randomize sequence\")\n")
            vseq_list.append("m_" + env + "_env_seq")

    for env in non_reg_env:
        vseq_list.append("m_" + env + "_env_seq")
        FH.write("    if ( !m_" + env + "_env_seq.randomize() )\n")
        FH.write("      `uvm_error(get_type_name(), \"Failed to randomize sequence\")\n")
        FH.write("    m_" + env + "_env_seq.m_env = m_" + env + "_env;\n")

    FH.write("    fork\n")
    for vseq in  vseq_list:
        FH.write("      "+ vseq + ".start(null, this);\n")

    for aname in  tb['top_env_agents']:
        agent = db[aname]
        for i in range(0,agent['number_of_instances']):
            suffix = calc_suffix(i, agent['number_of_instances'])
            sequencer_instance_name = "m_" + aname + "" + suffix + "_agent.m_sequencer"
            FH.write("      if (m_" + aname + "" + suffix + "_agent.m_config.is_active == UVM_ACTIVE)\n")
            FH.write("      begin\n")
            FH.write("        " + aname + "_default_seq seq;\n")
            FH.write("        seq = " + aname + "_default_seq::type_id::create(\"seq\");\n")
            FH.write("        seq.set_item_context(this, "+sequencer_instance_name+");\n")
            FH.write("        if ( !seq.randomize() )\n")
            FH.write("          `uvm_error(get_type_name(), \"Failed to randomize sequence\")\n")
            FH.write("        seq.m_config = m_" + aname + "" + suffix + "_agent.m_config;\n")
            FH.write("        seq.set_starting_phase( get_starting_phase() );\n")
            FH.write("        seq.start("+sequencer_instance_name+", this);\n")
            FH.write("      end\n")

    FH.write("    join\n")
    FH.write("  end\n")
    FH.write("\n")
    FH.write("  `uvm_info(get_type_name(), \"Default sequence completed\", UVM_HIGH)\n")
    FH.write("endtask : body\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("task " + tbname + "_default_seq::pre_start();\n")
    FH.write("  uvm_phase phase = get_starting_phase();\n")
    FH.write("  if (phase != null)\n")
    FH.write("    phase.raise_objection(this);\n")
    FH.write("endtask: pre_start\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("task " + tbname + "_default_seq::post_start();\n")
    FH.write("  uvm_phase phase = get_starting_phase();\n")
    FH.write("  if (phase != null) \n")
    FH.write("    phase.drop_objection(this);\n")
    FH.write("endtask: post_start\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("`ifndef UVM_POST_VERSION_1_1\n")
    FH.write("function uvm_phase " + tbname + "_default_seq::get_starting_phase();\n")
    FH.write("  return starting_phase;\n")
    FH.write("endfunction: get_starting_phase\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function void " + tbname + "_default_seq::set_starting_phase(uvm_phase phase);\n")
    FH.write("  starting_phase = phase;\n")
    FH.write("endfunction: set_starting_phase\n")
    FH.write("`endif\n")
    FH.write("\n")
    FH.write("\n")
    self.insert_inc_file(FH,"", "top_seq_inc", tb)
    FH.write("`endif // " + tbname.upper()+ "_SEQ_LIB_SV\n")
    FH.write("\n")
    FH.close()




  def gen_top_pkg(self):
    db = self.db
    tb = self.db['top']

    dir = tb['project'] + "/tb/" + tb['top_name']+ "/sv/"
    file= Path(dir + tb['top_name'] + "_pkg.sv" )
    FH = file.open('w')
    self.write_file_header(FH, tb, tb['top_name']+"_pkg.sv", "Environment for "+ tb['top_name'] )

    FH.write("package " + tb['top_name'] + "_pkg;\n")
    FH.write("\n")
    FH.write("  `include \"uvm_macros.svh\"\n")
    FH.write("\n")
    FH.write("  import uvm_pkg::*;\n")
    FH.write("\n")
    self.insert_inc_file(FH,"  ", "common_define", tb, "dut")
    try:
      if regmodel:
        FH.write("  import regmodel_pkg::*;\n")
    except: pass
    if mdefined (tb,'common_pkg','file'):
      FH.write("  import "+ tb['common_pkg']['name']+ "::*;\n")
    if mdefined (tb,'common_env_pkg','file'):
      FH.write("  import tb['common_env_pkg']['name']::*;\n")

    for agent in  tb['agent_list']:
        FH.write("  import "+ agent + "_pkg::*;\n")

    FH.write("\n")
    FH.write("  `include \"" + tb['top_name'] + "_config.sv\"\n")
    FH.write("  `include \"" + tb['top_name'] + "_seq_lib.sv\"\n")
#    if defined (ref_model ):
#        FH.write("  `include \"port_converter.sv\"\n")
#    }
#
#    for ref_model_name in ref_model :
#        FH.write("  `include \""+ ref_model_name + ".sv\"\n")
#    }
#    for ref_model_name in top_pkg_include:
#        FH.write("  `include \""+ ref_model_name + ".sv\"\n")
#    }
    if edef( tb ,'top_env_generate_scoreboard_class' , "YES"):
        FH.write("  `include \""+ tb['sb_top'] + "_scoreboard.sv\"\n")
    else:
      self.insert_inc_file(FH,"  ", 'top_env_scoreboard_inc_class',tb);
      
    FH.write("  `include \"" + tb['top_name'] + "_env.sv\"\n")
    FH.write("\n")
    FH.write("endpackage : " + tb['top_name'] + "_pkg\n")
    FH.write("\n")
    FH.close()




  def gen_top_test(self):

    db = self.db
    tb = self.db['top']
    
    dir = tb['project'] + "/tb/" + tb['top_name']+ "_test/sv/"
    file= Path(dir + tb['top_name'] + "_test.sv" )
    FH = file.open('w')
    self.write_file_header(FH, tb, tb['top_name']+"_test.sv", "Test class for  "+ tb['top_name'] )

    tbname = tb['top_name']
    FH.write("`ifndef " + tbname.upper()+ "_TEST_SV\n")
    FH.write("`define " + tbname.upper()+ "_TEST_SV\n")
    FH.write("\n")

    self.insert_inc_file(FH,"",  "test_inc_before_class", tb)

    FH.write("class "+ tbname + "_test extends uvm_test;\n")
    FH.write("\n")
    FH.write("  `uvm_component_utils(" + tbname + "_test)\n")
    FH.write("\n")
    FH.write("  "+ tbname + "_env m_env;\n")
    FH.write("\n")
    FH.write("  extern function new(string name, uvm_component parent);\n")
    FH.write("\n")
    if not edef(tb,'test_generate_methods_inside_class',"NO"):
        if not edef(tb,'comments_at_include_locations',"NO"):
          FH.write("  // You can remove build_phase method by setting test_generate_methods_inside_class = no in file "+ tb['tpl'] + "\n\n")

        FH.write("  extern function void build_phase(uvm_phase phase);\n")
        FH.write("\n")

    self.insert_inc_file(FH,"  ", "test_inc_inside_class", tb)

    FH.write("endclass : "+ tbname + "_test\n")
    FH.write("\n")
    FH.write("\n")
    FH.write("function "+ tbname + "_test::new(string name, uvm_component parent);\n")
    FH.write("  super.new(name, parent);\n")
    FH.write("endfunction : new\n")
    FH.write("\n")
    FH.write("\n")
    if not edef(tb,'test_generate_methods_after_class',"NO"):
        if not edef(tb,'comments_at_include_locations',"NO"):
            FH.write("// You can remove build_phase method by setting test_generate_methods_after_class = no in file "+ tb['tpl'] + "\n\n")

        FH.write("function void "+ tbname + "_test::build_phase(uvm_phase phase);\n")
        FH.write("\n")
        self.insert_inc_file(FH,"  ", "test_prepend_to_build_phase", tb)
        FH.write("  // You could modify any test-specific configuration object variables here\n")
        FH.write("\n")
        try:
          if regmodel:
            FH.write("  // Include reg coverage from the register model\n")
            FH.write("  uvm_reg::include_coverage(\"*\", UVM_CVR_ALL);\n")
        except: pass

        FH.write("\n")
        for aname in  tb['agent_name']:
          agent = tb['aname']
          for factory_override in agent['agent_factory_set']:   #ACHTUNG SORT
              if (factory_override!=""):
                  align("  "+ factory_override , "::type_id::set_type_override("+ agent['agent_factory_set'][factory_override] + "::get_type());", "")

        for factory_override in tb['top_factory_set']: #ACHTUNG SORT
            if (factory_override!=""):
                align("  "+ factory_override , "::type_id::set_type_override("+ tb['top_factory_set'][factory_override] + "::get_type());", "")

        gen_aligned(FH)
        FH.write("\n")
        FH.write("  m_env = "+ tbname + "_env::type_id::create(\"m_env\", this);\n")
        FH.write("\n")
        self.insert_inc_file(FH,"  ",  "test_append_to_build_phase", tb)
        FH.write("endfunction : build_phase\n")
        FH.write("\n")
        FH.write("\n")

    self.insert_inc_file(FH,"", "test_inc_after_class", tb)

    FH.write("`endif // " + tbname.upper()+ "_TEST_SV\n")
    FH.write("\n")
    FH.close()

  def gen_top_test_pkg(self):

    db = self.db
    tb = self.db['top']

    dir = tb['project'] + "/tb/" + tb['top_name']+ "_test/sv/"
    file= Path(dir + tb['top_name'] + "_test_pkg.sv" )
    FH = file.open('w')
    self.write_file_header(FH, tb, tb['top_name']+"_test_pkg.sv", "Test Package for "+ tb['top_name'] )

    tbname = tb['top_name']

    FH.write("`ifndef " + tbname.upper()+ "_TEST_PKG_SV\n")
    FH.write("`define " + tbname.upper()+ "_TEST_PKG_SV\n")
    FH.write("\n")
    FH.write("package " + tbname + "_test_pkg;\n")
    FH.write("\n")
    FH.write("  `include \"uvm_macros.svh\"\n")
    FH.write("\n")
    FH.write("  import uvm_pkg::*;\n")
    FH.write("\n")
    self.insert_inc_file(FH,"  ", "common_define", tb, "dut")

    try:
      if regmodel:
        FH.write("  import regmodel_pkg::*;\n\n")
    except: pass
    if mdefined (tb,'common_pkg','file'):
      FH.write("  import "+ tb['common_pkg']['name'] + "::*;\n"  )
    if mdefined (tb,'common_env_pkg','file'):
      FH.write("  import "+ tb['common_env_pkg']['name'] + "::*;\n" )
    for agent in  tb['agent_list']:
        FH.write("  import "+ agent + "_pkg::*;\n")

    FH.write("  import " + tbname + "_pkg::*;\n")
    FH.write("\n")
    FH.write("  `include \"" + tbname + "_test.sv\"\n")
    FH.write("\n")
    FH.write("endpackage : " + tbname + "_test_pkg\n")
    FH.write("\n")
    FH.write("`endif // " + tbname.upper()+ "_TEST_PKG_SV\n")
    FH.write("\n")
    FH.close()


  def gen_top_tb(self):

    db = self.db
    tb = self.db['top']

    dir = tb['project'] + "/tb/" + tb['top_name']+ "_tb/sv/"
    file= Path(dir + tb['top_name'] + "_tb.sv" )
    FH = file.open('w')
    self.write_file_header(FH, tb, tb['top_name']+"_tb.sv", "Testbench for "+ tb['top_name'] )

    tbname = tb['top_name']

    if edef( tb ,'split_transactors' , "YES" ):
      tb_module_name = tbname +"_untimed_tb"
      th_module_name = tbname +"_hdl_th"
    else:
      tb_module_name = tbname+"_tb"
      th_module_name = tbname+"_th"

    FH.write("module "+tb_module_name +";\n")
    FH.write("\n")
    FH.write("  timeunit      "+ tb['timeunit'] + ";\n")
    FH.write("  timeprecision "+ tb['timeprecision'] + ";\n")
    FH.write("\n")
    FH.write("  `include \"uvm_macros.svh\"\n")
    FH.write("\n")
    FH.write("  import uvm_pkg::*;\n")
    FH.write("\n")
    self.insert_inc_file(FH,"  ",  "common_define", tb, "dut")
    if tb['common_pkg']['file']:
      FH.write("  import "+ tb['common_pkg']['name'] + "::*;\n" )
    if mdefined(tb,'common_env_pkg','file'):
      FH.write("  import "+ tb['common_env_pkg']['name'] + "::*;\n")
    FH.write("  import "+ tbname + "_test_pkg::*;\n")
    FH.write("  import "+ tbname + "_pkg::"+ tbname + "_config;\n")
    FH.write("\n")
    FH.write("  // Configuration object for top-level environment\n")
    FH.write("  "+ tbname + "_config top_env_config;\n")
    FH.write("\n")
    if edef(tb,'dual_top',"YES" ):
        FH.write("  // Test harness\n")
        FH.write("  "+ th_module_name + " th();\n")
        FH.write("\n")

    self.insert_inc_file(FH,"  ", "tb_inc_inside_module", tb)
    if not edef(tb,'tb_generate_run_test', "NO" ):
      if not edef( tb,'comments_at_include_locations',"NO" ):
            FH.write("  // You can remove the initial block below by setting tb_generate_run_test = no in file "+ tb['tpl'] + "\n\n")

      FH.write("  initial\n")
      FH.write("  begin\n")
      self.insert_inc_file(FH,"    ", "tb_prepend_to_initial", tb)
      FH.write("    // Create and populate top-level configuration object\n")
      FH.write("    top_env_config = new(\"top_env_config\");\n")
      FH.write("    if ( !top_env_config.randomize() )\n")
      FH.write("      `uvm_error(\""+tb_module_name +"\", \"Failed to randomize top-level configuration object\" )\n")
      FH.write("\n")

      for i in range(0 ,len(tb['agent_list'])):  ### all_agent_ifs???
          agent_name = tb['agent_list'][i]
          agent = db[ agent_name ]
          for j in range (0,agent['number_of_instances']):
              suffix = calc_suffix(j, agent['number_of_instances'])
              test_harness_name = "th"
              if not edef(tb,'dual_top',"YES" ):
                  test_harness_name = th_module_name
              if edef(tb,'nested_config_objects', "YES" ):
                  if not edef( agent,'generate_interface_instance', "NO" ):
                      align(f"    top_env_config.m_{agent_name}{suffix}_config.vif ", f"= {test_harness_name}.{agent['if_instance_names'][j]};", "")
              else :
                  if not edef( agent,'generate_interface_instance', "NO" ):
                      align(f"    top_env_config.{agent_name}{suffix}_vif ", f"= {test_harness_name}.{agent['if_instance_names'][j]};", "")

                  if defined ( agent , 'agent_is_active'):
                      value = agent['agent_is_active']
                  else :
                      value = "UVM_ACTIVE"
                  align(f"    top_env_config.is_active_{agent_name}{suffix} ", f"= {value};", "")

                  if edef(agent,'agent_checks_enable', "NO" ):
                      value = "0"
                  else:
                      value = "1"
                  align(f"    top_env_config.checks_enable_{agent_name}{suffix} ", f"= {value};", "")

                  if edef( agent,'agent_coverage_enable', "NO" ):
                      value = "0"
                  else :
                      value = "1"
                  align(f"    top_env_config.coverage_enable_{agent_name}{suffix} ", f"= {value};", "")

                  if defined( agent,'agent_scoreboard_enable'):
                    if edef( agent['agent_scoreboard_enable'],agent , "YES" ):
                      value = "1"
                    else :
                      value = "0"
                  align(f"    top_env_config.scoreboard_enable_{agent_name}{suffix} ", f"= {value};", "")
                  align("\n", "", "")

      gen_aligned(FH)

      FH.write("\n")
      FH.write(f"    uvm_config_db #({tbname}_config)::set(null, \"uvm_test_top\", \"config\", top_env_config);\n")
      FH.write(f"    uvm_config_db #({tbname}_config)::set(null, \"uvm_test_top.m_env\", \"config\", top_env_config);\n")
      FH.write("\n")
      self.insert_inc_file(FH,"    ",  "tb_inc_before_run_test", tb)
      FH.write("    run_test();\n")
      FH.write("  end\n")
      FH.write("\n")

    FH.write("endmodule\n")
    FH.write("\n")
    FH.close()

  def gen_top_th(self):

    db = self.db
    tb = self.db['top']

    dir = tb['project'] + "/tb/" + tb['top_name']+ "_tb/sv/"
    file= Path(dir + tb['top_name'] + "_th.sv" )
    FH = file.open('w')
    self.write_file_header(FH, tb, tb['top_name']+"_th.sv", "TestHarness for "+ tb['top_name'] )

    self.insert_inc_file(FH,"  ",  "common_define", tb, "dut")

    tbname = tb['top_name']
    th_module_name = tbname + "_th"
    if edef( tb ,'split_transactors' , "YES" ):
      th_module_name = tbname=+"_hdl_th"

    FH.write("module "+th_module_name+";\n")
    FH.write("\n")
    FH.write("  timeunit      "+ tb['timeunit'] + ";\n")
    FH.write("  timeprecision "+ tb['timeprecision'] + ";\n")
    FH.write("\n")
    if mdefined(tb,'common_pkg','file'):
      FH.write("  import "+ tb['common_pkg']['name'] + "::*;\n")
    if mdefined(tb,'common_env_pkg','file'):
      FH.write("  import "+ tb['common_env_pkg']['name'] + "::*;\n")
    FH.write("\n")
    if not edef(tb,'th_generate_clock_and_reset', "NO"):
      if not edef(tb,'comments_at_include_locations', "NO"):
          FH.write("  // You can remove clock and reset below by setting th_generate_clock_and_reset = no in file "+ tb['tpl'] + "\n\n")

      FH.write("  // Example clock and reset declarations\n")
      FH.write("  logic clock = 1;\n")
      FH.write("  logic reset;\n")
      FH.write("\n")
      FH.write("  // Example clock generator process\n")
      FH.write("  always #("+ tb['period'] + "/2) clock = ~clock;\n")
      FH.write("\n")
      FH.write("  // Example reset generator process\n")
      FH.write("  initial\n")
      FH.write("  begin\n")
      FH.write("    reset = 0;         // Active low reset in this example\n")
      FH.write("    #"+ tb['reset_time'] + ";\n")
      FH.write("    reset = 1;\n")
      FH.write("  end\n")
      align("")

      for aname in tb['agent_list']:
        agent = db[aname]
        if defined ( agent , 'rlist'):
          rlist = agent['rlist']
          if len(rlist):
            i = 0
            while i < len(rlist):
              agent_name = rlist[i]
              if not edef(agent,'generate_interface_instance', "NO" ):
                for j in range(0,agent['number_of_instances']):
                  suffix = f"_{j}"
                  align(f"  assign {agent_name}_if{suffix}.{rlist[ i + 1 ]}", f" = {rlist[ i + 2 ]};")
              i = i + 3
      align("")

      for aname in  tb['agent_list']:
        agent = db[aname]
        if defined ( agent , 'clist'):
          clist = agent['clist']
          if len(clist):
            i = 0
            while i < len(clist):
              agent_name = clist[i]
              if not edef(agent,'generate_interface_instance', "NO" ):
                for j in range(0,agent['number_of_instances']):
                  suffix = f"_{j}"
                  align(f"  assign {agent_name}_if{suffix}.{clist[ i + 1 ]}", f" = {clist[ i + 2 ]};", "")
              i = i + 3
      align("")

      for agent_name in  tb['agent_list']:
        agent = db[agent_name]
        if defined ( agent , 'if_map'):
          for im in  agent['if_map']:
            im=re.sub(r"\s*,\s*",",",im)
            im=re.sub(r"\s*;?\s*$","",im)
            mlist = im.split(",")
            if not edef(agent,'generate_interface_instance', "NO" ):
              for j in range(0,agent['number_of_instances']):
                suffix = f"_{j}"
                try:
                  if ("if"+ suffix == mlist[2]):
                    align(f"  assign {agent_name}_if{suffix}.{mlist[0]}", f" = {mlist[1]};", "")
                except:
                  align(f"  assign {agent_name}_if{suffix}.{mlist[0]}", f" = {mlist[1]};", "")
          align("")        

      gen_aligned(FH)

    self.insert_inc_file(FH,"  ",  "th_inc_inside_module", tb)
    
    align("  // Pin-level interfaces connected to DUT\n", "", "")
    if not edef(tb,'comments_at_include_locations',"NO" ):
        align("  // You can remove interface instances by setting generate_interface_instance = no in the interface template file\n\n", "", "")
        align("")

    gen_aligned(FH)
     
    for agent_name in  tb['agent_list']:
        agent = db[agent_name]
        if not edef( agent,'generate_interface_instance', "NO" ):
            interface_type = agent_name+"_if"
            if defined ( agent , 'byo_interface'):
                interface_type = agent['byo_interface']

            for i in range(0,agent['number_of_instances']):
                suffix = f"_{i}"
                align("  "+ interface_type+ " " , agent_name+"_if"+ suffix + " ();", "")

    if edef( tb ,'split_transactors' , "YES" ):
        align("  // BFM interfaces that communicate with proxy transactors in UVM environment\n", "", "")
        for agent_name in  tb['agent_list']:
            agent = db[agent_name]
            for i in range(0,agent['number_of_instances']):
                suffix = f"_{i}"
                align("  "+ agent_name + "_bfm  ", agent_name+"_bfm"+ suffix + " ("+ agent_name + "_if"+ suffix + ");", "")
        align("")

    gen_aligned(FH)
    FH.write("\n  // DUT Instantiation\n\n")

    self.gen_dut_inst(FH)

    FH.write("\n")
    FH.write("endmodule\n")
    FH.write("\n")
    FH.close()

  def gen_pfile(self,dut_pfile):
    tb = self.db['top']
    PFH = dut_pfile.open("w")
    PFH.write( "## =================== Clock/Reset ================\n")
    PFH.write( f"#!{clock_reset}_if\n\n")
    PFH.write( f"{clock}    {clock}\n" )
    PFH.write( f"{reset}    {reset}\n\n")
    for agent_name in  tb['agent_list']:
      PFH.write( "!"+agent_name+"_if\n\n"   )
      PFH.write( "#vhdl_port_sig interface_sig\n\n"   )
    PFH.close()
    print("\n WARNING! generate new file! Edit file "+ str(dut_pfile) + "\n")


  def gen_dut_inst(self,FH):

    db = self.db
    tb = self.db['top']

    dut_file = Path("pinlist.txt")
    if defined (tb,'dut_pfile'):
      dut_file = Path(tb['dut_pfile'])

    if dut_file.exists():
      if 0 == os.path.getsize(dut_file):
        self.gen_pfile(dut_file)
    else:
      self.gen_pfile(dut_file)

    PFH = dut_file.open()


    param_list1 = []
    param_list2 = []
    param_list3 = []
    port_list1  = []
    port_list2  = []
    port_list3  = []

    count_of_trailing_comments = 0
    if_name = 0
    lines = PFH.readlines()
    for line in lines:
      line = re.sub(r"(#|//).*$","",line)
      res = re.search(r"^\s*$", line)
      if res : continue
      line = re.sub(r"[\r\n]*","",line)

      comments     = re.search(r"^\s*(//.*)",line)
      parameters   = re.search(r"^\s*PAR\s*(\||\=)\s*(\S+)\s+(\S+)",line)
#      ports        = re.search(r"^\s*(\S+)\s+(\S+)\s*",line)
      ports        = re.search(r"^\s*(\S+)\s+(\S+)\s*(.*)?",line)
      variable_dec = re.search(r"\s*DEC\s*(\||\=)\s*(.+)\s*",line)
      next_if_name = re.search(r"!(\w*)",line)

      if ( comments ) :
           port_list1.append("    "+comments.group(1))
           port_list2.append("")
           count_of_trailing_comments+=1

      elif ( parameters ) :
        param_list1.append("    ."+parameters.group(2))
        param_list2.append(f"({parameters.group(3)}),")

      elif ( ports ) :
          
          if (if_name) :
            port_list1.append("    ."+ports.group(1))
            port_list2.append(f"({if_name}.{ports.group(2)}),")
            if ports.group(3): port_list3.append("// "+ports.group(3))
          else:
            port_list1.append("    ."+ports.group(1))
            port_list2.append(f"({ports.group(2)}),")
            if ports.group(3): port_list3.append("// "+ports.group(3))

          count_of_trailing_comments = 0

      elif ( variable_dec ) :
          FH.write(f"  {variable_dec.group(2)}\n")

      elif ( next_if_name ):
        if_name = next_if_name.group(1)
        res = re.search(r"\d$",if_name)
        if not res:
            if_name += "_0"
        if (if_name) :

          agent_name = re.sub(r"_if$","",if_name)

          # The name in the pinlist file was originally an interface name but can now be a user-defined interface instance name instead
          if mdefined ( db , 'agent_name','if_instance_names') :
            if_name = db['agent_name']['if_instance_names'][0]

          log("Writing ports for interface "+ if_name + "\n")


    FH.write("  "+tb['dut_top'] + " ")
    if len(param_list1):
      FH.write("#(\n")
      param_list2[-1] = re.sub(r",","",param_list2[-1])                #remove trailing ','
      FH.write(get_pretty_inv([param_list1, param_list2, param_list3]))
      FH.write("  )\n  ")

    FH.write(tb['dut_iname']+" (\n")
    if len(port_list2):
      port_list2[-1] = re.sub(r",","",port_list2[-1])                #remove trailing ','
      FH.write(get_pretty_inv([port_list1, port_list2, port_list3]))
      FH.write("  );\n")

    PFH.close()

#    FH.write("  tb['dut_top'] ")
#    if (@param_list1) {
#        chop($param_list2[-1]);  #remove trailing ','
#        FH.write("#(\n")
#        pretty_print([\@param_list1, \@param_list2, \@param_list3])
#        FH.write("  )\n  ")
#    }
#    FH.write("tb['dut_iname'] (\n")
#    if (@port_list2) { chop($port_list2[-1-$count_of_trailing_comments]); }    #remove trailing ','
#    pretty_print([\@port_list1, \@port_list2, \@port_list3])
#    FH.write("  );\n")

  def generate_top (self):
    tb = self.db['top']
    self.gen_top_dir('top')
    log("Create the top files\n")
    if edef(tb,'regmodel',1):
      self.gen_regmodel()

    self.extra_checking_for_additional_agents()
    if defined(tb,'top_env_agents'):
      astr = ""
      for a in tb['top_env_agents']:
        astr += a
      log("top env agents = "+ astr + " \n")
    log("Generating testbench in "+ tb['project'] + "/tb\n")
    print("Generating testbench in         "+ tb['project'] + "/tb\n")

    tb['active_inst'] = {}
    tb['passive_inst'] = {}
    tb['all_inst'] = {}
    
    for ag in tb["agent_list"]:
      if edef(tb['active'], ag, "UVM_ACTIVE"):
        tb['active_inst'][ag] = []
        tb['all_inst'][ag] = []
        for i in self.db[ag]["instance_names"]:
          tb['active_inst'][ag].append(re.sub(r"_agent","",i))
          tb['all_inst']   [ag].append(re.sub(r"\bm_","",tb['active_inst'][ag][-1]))
      else:
        tb['passive_inst'][ag] = []
        tb['all_inst'][ag] = []
        for i in self.db[ag]["instance_names"]:
          tb['passive_inst'][ag].append(re.sub(r"_agent","",i))
          tb['all_inst']    [ag].append(re.sub(r"\bm_","",tb['passive_inst'][ag][-1]))
          

    self.gen_top_config()
    self.gen_port_converter()
    self.gen_ref_model()
    self.gen_top_sb()
    self.gen_top_env()
    self.gen_top_seq_lib()
    self.gen_top_pkg()
    self.gen_top_test()
    self.gen_top_test_pkg()
    self.gen_top_tb()
    self.gen_top_th()

    print("Generating testbench done!\n")
##==============================================================

if __name__ == '__main__':

  f=open('uvm_agent.json')
  db = json.load(f)

  skeys = list(db.keys())

  skeys.sort()
  print(skeys)

  obj = TOP(db)
  regmodel = 0
  print("---------------for------------------------")

  print ("generate TOP " )

  obj.generate_top()
  print("---------------------------------------")


