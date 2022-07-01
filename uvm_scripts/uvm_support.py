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

""" Collection of simple functions

uvm_support.py 
Version 1.0.1

"""

import re
import sys
import os
import pathlib
import shutil


traceFiles = [sys.stdout]

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


def pj (tb):
  #print (tb)
  print (json.dump(tb,sys.stdout,indent=3,sort_keys=True))
  return 1

def log (*line):
  message = sjoin(' ',line)
  fh = open("uvm_gen.log","a")
  fh.write(message);fh.write('\n');
  ##print_fc(message,'green');

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

def form (decl):
  decl = re.sub(r'(\s*);(\s*)',';',decl)
  decl = re.sub(r'//\s*','',decl)
  decl = re.sub(r';(.+)',';   // \g<1>',decl)
  decl = re.sub(r'\s*$','',decl)
  decl = re.sub(r'^\s*','  ',decl)

  return decl



def sjoin(sep,list):
  s='';
  for i in list:
    s+=str(i)+sep
  return s

def dircopy (ffrom,fto):

  if ffrom == fto:
    print ("Cant Copy same dir!", ffrom," => ",fto)
    return
  from_file = pathlib.Path(ffrom)
  to_file   = pathlib.Path(fto)
  print(f"copy {from_file} to {to_file} ")
  try:
    #3.9
    shutil.copytree(from_file, to_file, dirs_exist_ok=True)
  except:
    print(f"  delete {to_file} and copy from {from_file}")
    shutil.rmtree(fto)
    shutil.copytree(from_file, to_file)

def makedir ( dir ):
  fdir = pathlib.Path(dir)
  if not fdir.exists():
    fdir.mkdir(0o755,parents=True, exist_ok=True)
    #print (fdir)

def check_dir ( dir ):
  makedir ( dir )

def _warning_prompt (all,global_continuous,*messages):
  message = sjoin(' ',messages)
  if global_continuous == 0:
    print_fc( "WARNING! "+ message ,'re')

    if (all == True): choise = "all"
    else: choise = input("Continue? (y/n) or [all]!  [n] >> ")
    if (choise == 'all'): global_continuous = 1
    if (global_continuous == 0):
        if choise.lower() != 'y': pexit( "UVM CODE NOT GENERATED DUE TO ERRORS!")
    return  global_continuous

def warning_prompt (*messages,doit=False):
  message = sjoin(' ',messages)
  print_fc( "WARNING! "+ message ,'re')
  if doit:
    print("Code will be generated!\n")
  else:
    choise = input("Continue? (y/n)!  [n] >> ")
    if choise.lower() != 'y': pexit( "UVM CODE NOT GENERATED DUE TO ERRORS!")

def pexit ( *messages):
  message = sjoin(' ',messages)
  print_fc( "DIE! "+ message ,'re')
  exit()

def calc_suffix(i,n):
    if (n == 1): suffix = ""
    else:        suffix = "_"+str(i)
    return suffix

def die (b,*messages):
  if not b:
    message = sjoin(' ',messages)
    print_fc( "DIE! "+ message ,'re')
    exit()


def check_file ( fname, mode=1):

  fn = pathlib.Path(fname)
  if fn.exists():
    return 1
  else:
    warning_prompt("SPECIFIED FILE "+ fname + " NOT FOUND")

  if ( mode == 1 ):
      FH = fn.open("w")
      FH.write('')
      FH.close()
  else:
    if fn.exists(): return 1
    else: return 0

'''
sub check_dir {
    my @dname = @_
    my $dname = join "/", @dname
    if not (-e "${dname}") {
        warning_prompt("SPECIFIED DIR $dname NOT FOUND")
        $dname = ''
        foreach my $dn (@dname) {
            $dname .= $dn
            if not( -e ${dname} ) { my $r = mkdir( ${dname}, 0755 ); }
            $dname .= '/'
        }
    }
}


sub exeq {
     my ($i, $n) = @_
     if ( defined $i and $i == $n) { return 1; }
     else { return 0; }
}

sub edef {
     my ($i, $n) = @_
     if not (defined $i) {$i = "YES"}
     if ( $i == $n) { return 1; }
     else { return 0; }
}

sub dedef {
     my ($i, $n) = @_
     if not (defined $i) {return 0}
     if ( $i == $n) { return 1; }
     else { return 0; }
}


sub ndef {
     my ($i, $n) = @_
     if not (defined $i) {$i = "YES"}
     if ( $i!=$n) { return 1; }
     else { return 0; }
}

sub dndef {
     my ($i, $n) = @_
     if not (defined $i) {return 0}
     if ( $i!=$n) { return 1; }
     else { return 0; }
}


sub dbp {
  my $db = shift
  if (defined $opt_debug) {print Dumper $db ;}
}
'''


"""The module 'support_functions' includes functions and classes to print
colored messages to the terminal and html logfiles. Also a normal text file can
be written. The module use the sys and re module and all definitions of
'testscript_common' the class 'logFile' inherits form 'file'
"""

def severityLevel(a,b):
    ''' Return True if the the given level a is greater or equal than level b.
        The level order is 'info','verbose','critical','debug'}
    '''
    level = {'info':1,'verbose':2,'critical':3,'debug':4}
    if level[str(a)] >= level[str(b)]: return True
    else: return False



def userPrompt(message, prompt='Press <CR> to continue...', allowedAnswers=[]):
  """ prompt for user input

  examples: userPrompt('Disconnect cable')
            userPrompt('Please check LED', 'Is LED on? [y|n]', ['y', 'n'])

  @param message:        message (printed first)
  @param prompt:         prompt (printed after message)
  @param allowedAnswers: list of allowed answers (e.g. ['y', 'n'])
  """

  while len(select.select([sys.stdin.fileno()], [], [], 0.0)[0])>0:
    os.read(sys.stdin.fileno(), 4096) # flush stdin
  sys.stdin.flush()
  usrAnswer='\a'
  while not usrAnswer in allowedAnswers:
    print_c(message + "\n\033[5m" + prompt, escSeq='\033[1;37;44m')
    print ("\a\033[1;37;44m") # alert user
    sys.stdout.flush()
    usrAnswer = sys.stdin.readline().rstrip()
    print ("\033[0m")
    if len(allowedAnswers) == 0:
      break
  return usrAnswer


def escSeq(fg='fd', bg='bd', at='' ):
    """ Return an ansi color esc sequenze in the format \\033[0,'fg','bg','at'm

        Keyword arguments:
        fg -- foreground as sting
        bg -- backgroud  as string
        at -- attirbut   as string ',' seperated values
        Default is black on white. Possible color are re,gr,bl,ye,cy,ma and all
        with prefix 'l' for light like 'lre' , bk and wh for black and white,
        lgry and dgry for light and dark gray.
        The attributes are bol (bold) dim (italic) und (underlined) bli (blink)
        rev (reverse) hid (hidden)
        Example: escSeq('gr','lre',at='bol,und') return \\033[0,32;101;1;4m
        see http://misc.flogisoft.com/bash/tip_colors_and_formatting
        for possible formats


    """

    fgcolor={'bk':'30', 're':'31',  'gr':'32',  'ye':'33',  'bl':'34',
                        'ma':'35',  'cy':'36', 'lgry':'37','dgry':'90',
                        'lre':'91', 'lgr':'92', 'lye':'93', 'lbl':'94',
                        'lma':'95', 'lcy':'96',   'wh':'97',  'fd':'39'}

    bgcolor={'bk':'40', 're':'41',  'gr':'42',  'ye':'43', ' bl':'44',
                        'ma':'45',  'cy':'46', 'lgry':'47','dgry':'100',
                        'lre':'101','lgr':'102','lye':'103','lbl':'104',
                        'lma':'105','lcy':'106', 'wh':'107',  'bd':'49'}

    attrib={'bol':'1;','dim':'2;','und':'4;','bli':'5;','rev':'7;','hid':'8;','':''}

    try:
        fgc=fgcolor[fg]
    except:
        fgc='39'
    try:
        bgc=bgcolor[bg]
    except:
        pass

    att=''
    for i in str(at).split(','):
        try:
            att+=attrib[i]
        except:
            pass

    return('\033[0;'+att+str(fgc)+';'+str(bgc)+'m')  # bg and fg are always defined

def fc(message=None, fg='fd', bg='bd', at='' ):
    '''format and return the message with escSeq
    '''
    escs = escSeq(fg=fg, bg=bg, at=at )
    text = str(message)
    if text and text[-1] == '\n':
        return(escs+text[:-1]+'\033[0m\n')
    else:
        return(escs+text+'\033[0m')

def write_c(message=None, escSeq=None):
    """ print colorized message to definded trace files

    Keyword arguments:
    message -- string to print
    escSeq  -- escape sequence representing the color format
            (e.g. '\033[0,41m' for red background,
            default are the standard colors)
    """
    if os.name != 'posix': escSeq=None
    global traceFiles
    if not defined (traceFiles):
      traceFiles = [open ("traces.log","w")]
    for traceFile in traceFiles:
        text = str(message)
        if text:
            lf=''
            if escSeq:
                traceFile.write(escSeq)
            if text[-1] == '\n':
                lf = '\n'
                traceFile.write(text[:-1])
            else:
                traceFile.write(text)
            if escSeq:
                traceFile.write('\033[0m')
            traceFile.write(lf)
            traceFile.flush()


def print_ma(message):
    '''print message in magenta (198)'''
    write_c(message,escSeq='\033[38;5;198m')

def print_gr(message):
    '''print message in green (226)'''
    write_c(message,escSeq='\033[38;5;226m')

def print_ye(message):
    '''print message in yellow (82)'''
    write_c(message,escSeq='\033[38;5;82m')


def headline(message='',color=0):
    '''Print the message in a special colored headline

    Keyword arguments:
    message  -- sting to print
    color    -- range[0:41]
    '''
    color=int(color)
    if color <0 or color>40:
        color = 0
    colors = 16+6*(color)
    s=colors;e=colors+5
    for index in range(s, e+1):
        escSeq = '\033[48;5;%dm ' %(index)
        print_c('   ', escSeq)
    print_c(message ,escSeq)
    for index in range(e, s-1, -1):
        escSeq = '\033[48;5;%dm ' %(index)
        print_c('   ', escSeq)
    print


def print_fc(message, fg='fd', bg='bd', at=''):
    '''Print a colored message

    Use escSeq(...) and write_c(...) function and provides in addition to fg
    the color definitions 'light','dark','magenta','yellow','green' for print_c()
    from 'test_common' to emulate this function
'''
    colFormats = {'light'  : '\033[7;34m',
                  'dark'   : '\033[7;32m',
                  'magenta': '\033[38;5;198m',
                  'yellow' : '\033[38;5;226m',
                  'green'  : '\033[38;5;82m'}

    if fg in colFormats:
        escs = colFormats[fg]
    else:
        escs = escSeq(fg=fg, bg=bg, at=at)
    write_c(message+'\n', escs)

def print_msg(a,b,ind=''):
    '''print indended and formated message as table in yellow color'''
    print_fc(('%s%-45s %s' % (ind,a,b)),'ye')

def print_dbg(a,b,ind=''):
    '''print indended and formated debug message as table in red color'''
    print_fc(('%s%-45s %s' % (ind,a,b)),'re')

def comment(s,l,*sarg):
    '''print message surrounded by a box with given sign

    Keyword arguments:
    s  --  sign
    l  -- line length
    sarg -- string top print
    Example : comment('#',1,'comment')
    ###########
    # comment #
    ###########
'''
    ind=''
    strp=''

    if len(s):
     ind=s[:-1]
     strp=s[-1]

    cline = strp*l
    write_c('\n'+ind+cline+'\n')
    ml=[]
    for a in sarg:
        if type(a) == str:
            ml.append(a)
        elif type(a) == list:
            for i in a:ml.append(i)
        elif type(a) == tuple:
            ml.extend(a)
        elif type(a) == dict:
            for i in a:ml.append(str(i) + ': '+str(a[i]))
        else:
            ml.append(a)
    for item in ml:#sarg:
        item = str(item)
        el=0
        if re.search('\033\[',item):el=14
        write_c(ind+ strp+'  '+item+' '*(l-len(item)-4+el)+strp+'\n')
    write_c(ind+cline +'\n\n')

def readCsv(csvfile_in):
    '''Read a csv file and return tuple of 2 lists for valuelines and headline

    Keyword arguments:
    csvfile_in  --  file name for input
    deli        --  delimiter can be [,;\t]
    The delimiter is the first occur of [,;\\t].
'''
    import csv

    db = []
    rowNames = []
    if os.path.isfile(csvfile_in):
        with open(csvfile_in,'r') as infl:
            li=infl.readline()
            m = re.search('([,;\t])',li)
            if m :
                deli=m.group(0)
                rowNames = li.strip().split(deli)
            else:
                print_fc('No delimiter found! Search for [,;\\t] !')
                return ([],[])
        reader = csv.DictReader(open(csvfile_in,'rU'), delimiter=deli)
        # generead header
        for l in reader:
            db.append(l)
    else:
        print_fc('File ' + csvfile_in + ' not found!','re')
    return (db ,rowNames)


class logFile():
    """ Extend the file class to convert color formated messages with escSeq()
        for the terminal output to text.
        Used for log and report files.
    """

    def __init__(self, name, mode):
        self.fh = open(name, mode)

    def ansi2txt(self, s):
        ''' remove the escSeq() formats form the string'''
        ansi = re.sub('\033\\[([\\d;]*)m','',s)
        return ansi

    def write(self, s):
        '''write the modified string to file '''
        s = self.ansi2txt(s)
        file.write(self, s)



if __name__ == '__main__':
  pass

