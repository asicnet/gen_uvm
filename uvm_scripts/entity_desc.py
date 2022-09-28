# -*- coding: utf-8 -*-
# Copyright © 2022 Helmut Steinbach

import os, os.path
import sys
import io
import re

import vhdl_parser as vhdl
import verilog_parser as vlog

class entity_desc():
  '''
  The class generate: ./entity_desc.txt
                      
  eg. entity_desc.entity_desc(file,info=True).create()                    
  '''
  
  def __init__(self,fname,vhdl=False,vlog=False,info=False,no_create=False):
    self.fname = fname
    self.vhdl  = vhdl
    self.vlog  = vlog
    self.info  = info
    self.no_create = no_create    


  def create_objs(self):
  
    ftype = None
    
    # check file extension
    if vhdl.is_vhdl(self.fname):
      ftype ='vhdl'
    elif vlog.is_verilog(self.fname):
      ftype ='vlog'
      
    #overwrite ftype  
    if self.vhdl:
      ftype ='vhdl'
    elif self.vlog:
      ftype = 'vlog'
    
    #create a data object with the Extractor  
    if ftype =='vhdl':
      objs = vhdl.VhdlExtractor().extract_objects(self.fname)
    elif ftype == 'vlog':
      objs = vlog.VerilogExtractor().extract_objects(self.fname)
    else:
      print('File Type Error! call:  '+sys.argv[0]+'  --help  for more information \n\n' );exit()  
    
    # print a info of the object content  
    if self.info:
      print('\n') 
      for component in objs:
        if component.kind == 'entity' or component.kind == 'module' :
          print('  {}: "{}":'.format(component.kind.capitalize(),component.name))
          
          if component.kind == 'entity':
            print('    Generics:')
          if component.kind == 'module' :
            print('    Parameters:')
            
          for generic in component.generics:
            if generic.default_value: generic.default_value = "= "+str(generic.default_value)
            else: generic.default_value = ''
            print('\t{:30}{:8} {} {} {}'.format(generic.name, generic.mode, generic.data_type, generic.default_value, generic.desc))
          
          print('    Ports:')
          for port in component.ports:
            if port.default_value: port.default_value = "= "+str(port.default_value)
            else: port.default_value = ''
            print('\t{:30}{:8} {} {} {}'.format(port.name, port.mode, port.data_type , port.default_value, port.desc))
        else:
          print(component)
                
        print('\n') 
    return objs 


  def execute(self,objs):

    if self.no_create:
      print("stop execution")
      return
          
    for component in objs:
        
      self.gw=1
      self.gl = len(component.generics)-1
      for generic in component.generics:
        if (len(generic.name) > self.gw):
          self.gw = len(generic.name) 
      self.gw+=2
        
      self.pw=1  
      self.pl = len(component.ports)-1
      for port in component.ports:
        if (len(port.name) > self.pw):
          self.pw = len(port.name) 
       
      self.rw=1  
      for port in component.ports:
        rng = port.range      
        if (len(rng) > self.rw):
          self.rw = len(rng) 
          
      self.comp_desc(component)
    
    
  def comp_desc(self,component):          
    fh = open('entity_desc.txt','w')  
      
    fh.write("ENTITY = "+ component.name + "\n\n")
    if (component.generics):
      define = {}
      for generic in component.generics:
        fs = 'DEV = {:'+str(self.gw)+'} {} {}\n'
        dev = 'd_'+re.sub(r'^g_','',generic.name)
        define[generic.name] = dev
        if generic.desc: 
          generic.desc = re.sub('--','#--',generic.desc)
        fh.write(fs.format( dev, generic.default_value,  generic.desc))
      fh.write('\n')
      
      for generic in component.generics:
        fs = 'PAR = {:'+str(self.gw)+'} {} {}\n'
        
        fh.write(fs.format( generic.name, generic.default_value,  generic.desc))
        
      fh.write('\n')


    clock = ['clk  ']
    reset = ['rst_n']
    if (component.ports):
      clock.append('#')
      reset.append('#')          
      for port in component.ports:
        if re.search(r'clock|clk',port.name):
          clock.append(port.name)
        if re.search(r'reset|rst',port.name):
          reset.append(port.name)
      
      
    fh.write('!clock_reset active reset\n\n')

    fh.write('  clock         '+' '.join(clock) +'\n')
    fh.write('  reset         '+' '.join(reset) +'\n')

    fh.write(f'\n!{component.name}_agent active # | passive \n\n')

    if (component.ports):
      for port in component.ports:
        fs = '  {:' + str(self.pw) + '} {:' + str(self.pw) + '} {} {:' + str(self.rw) + '} {} {} \n'
        if port.desc: 
          port.desc = re.sub('--','#--',port.desc)
          
        rng = port.range
        if rng: 
          for i in define:
            rng =re.sub(fr'\b{i}\b',fr'`{define[i]}',rng)
            
        default_value = port.default_value
        if default_value: 
          for i in define:
            default_value =re.sub(fr'\b{i}\b',fr'`{define[i]}',default_value)
          default_value = ':= '+default_value
          
        fh.write(fs.format(port.name,port.name,port.mode,rng,default_value,port.desc))
       
    fh.write('\n\n')
    fh.close()
    
  
  def create(self):
    objs = self.create_objs()
    self.execute(objs)
    return self

if __name__ == '__main__':

  print('\n  not usable alone !\n')
