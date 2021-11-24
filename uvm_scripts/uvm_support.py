#!/usr/bin/env python3.9
# -*- coding: utf8 -*-
""" Collection of simple functions

uvm_support.py 
Version 0.1.0

"""

import re

pp_list = []

def align(*p):
  global pp_list
  pp = []
  for s in p:
    pp.append(s)
  pp_list.append(pp)

def gen_aligned (FH):
  global pp_list
  FH.write(get_pretty(pp_list))
  pp_list = []

def get_aligned ():
  global pp_list

  txt = get_pretty(pp_list)
  pp_list = []
  return txt

def get_pretty (ppl):
  maxrow = len(ppl)
  maxcol = 0
  for i in range(0 ,len(ppl)) :
    le = len(ppl[i])
    if ( le > maxcol): maxcol = le

  for col in range(0,maxcol):
      maxlen = 0
      for row in range(0 ,maxrow) :
        try:
          l = len(ppl[row][col])
        except:
          ppl[row].append("\n")
          l=0
        if ( l > maxlen): maxlen = l

      for row in range(0 ,maxrow) :
        x = maxlen-len(ppl[row][col])+1
        sep = ''
        for o in range(0,x) :
          sep += ' '
        ppl[row][col] += sep

  txt = ""
  for row in range(0,maxrow):
    line = ""
    for col in range(0,maxcol):
      line += ppl[row][col]
    line = re.sub(r'\s*$','',line)
    txt += line+"\n"

  return txt

def get_pretty_inv(ppl):
  maxrow = len(ppl)
  maxcol = 0
  for i in range(0 ,len(ppl)) :
    l = len(ppl[i])
    if ( l > maxcol): maxcol = l

  for row in range(0,maxrow):
      maxlen = 0
      for col in range(0 ,maxcol) :
        try:
          l = len(ppl[row][col])
        except:
          ppl[row].append("\n")
          l=0
        if ( l > maxlen): maxlen = l

      for col in range(0 ,maxcol) :
        x = maxlen-len(ppl[row][col])+1
        sep = ''
        for o in range(0,x) :
          sep += ' '
        ppl[row][col] += sep

  txt = ""
  for col in range(0,maxcol):
    line = ""
    for row in range(0 ,maxrow) :
      line += ppl[row][col]
    line = re.sub(r'\s*$','',line)
    txt += line+"\n"

  return(txt)



def edef (ref,i,n):
  try:    v = ref[i]
  except: v = "YES"
  if ( v == n ): return 1
  else:          return 0

def mdefined(var,*name):
  if type(var) == type(None) : return 0
  for i in name:
    if defined (var,i):
      var = var[i]
    else:
      return 0
  return 1


def defined(var,name=None):
  if type(var) == type(None) : return 0
  if name != None:
    if type(var) == dict:
      if name in var:
        if var[name] != None: return 1
    if type(var) == list:
      if len(var)>name and var[name] != None: return 1
    if type(var)== tuple:
      if len(var)>name and var[name] != None: return 1
    return 0
  return 1

def sjoin(sep,list):
  s='';
  for i in list:
    s+=str(i)+sep
  return s

def die (b,*messages):
  if not b:
    message = sjoin(' ',messages)
    print_fc( "DIE! "+ message ,'re')
    exit()


if __name__ == '__main__':
  pass

