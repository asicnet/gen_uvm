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

""" Helper module to parse tpl file and create a easier uvm testbech.

header_cfg.py 
Version 1.0.0

"""
from os.path import join #, dirname
from os      import environ
import sys

PROJECT_NAME     = "PROJECT_NAME"                # change to your project
                                                 
copyright        = "My copyright string"         # change to your or other company
author           = "My name"                     # change to your First Name and Name
email            = "My email"                    # change to your email address
tel              = "My telephone"
dept             = "My department"               
company          = "My company"                  # change to your company
year             = "My year"
version          = "Version_string"
                 
clock            = "clk"                         # overwrite the default "clock"     
reset            = "rst_n"                       # overwrite the default "reset"        
clock_reset      = "clock_reset"                 # name of agent module for clock-reset-driver
tmplt_include_file = 'uvm_template'     # "uvm_template"  ,<project>_template       
                                        # create a own project template and change the name
                                        # You can overwrite the filename with environment variable set tmplt_include_file_name=uvm_template                                            

json_enable      = 0                    # 0 = None , 1 = create file , 2 = print to STDOUT , 3 booth
## perl
#tool             = "perl" 
#genscript        = "easier_uvm_gen.pl"  
#python
tool             = sys.executable # used python path
genscript        = "gen_uvm.py"     

#script_path      = environ.get( "GEN_UVM_PATH", join("..","..") )
script_path      = "D:/github.com/gen_uvm/uvm_scripts"
compatible       = 0                    # 0 -> not compatible : 1 -> compatible to easier_uvm
                                        # 1 use inclued/<agent>/ folder
uvmf = False