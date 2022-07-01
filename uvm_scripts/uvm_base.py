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

""" Base Class for UVM

uvm_base.py 
Version 1.0.1

"""

from   uvm_support   import * # global functions
from pathlib import Path

class UVM_BASE:
  '''Class for Agent Generator
  The the data base is given to create a agent directory structure
  '''

  def __init__(self, database, verbose='info',ind=3):
      '''Define objekt variables and print debug infos
      '''
      self.verbose = verbose
      self.ind=ind
      self.db = database
      self.tb = database['top']
      if ind:
          self.indstr=' '*ind

      if severityLevel(self.verbose,'debug'):
          class_name = self.__class__.__name__
          print_fc(class_name + ' created','gr')


  def insert_inc_file (self, FH, indent, param_name, ref, tbdir=""):
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
