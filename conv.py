#!/usr/bin/python3
# File:     /src/vgallery/conv.py
# Author:   Kenson Man <kenson@mansonsolutions.hk>
# Date:     2020-06-13 23:45
# Desc:     Convert the unit to specific unit. e.g.: px to rem
#
import argparse, logging, os, re
parser = argparse.ArgumentParser()
parser.add_argument('--recursive', '-r', action='store_true', help='Convert the files recursivelly')
parser.add_argument('--from', '-f', default='px', help='The source unit; Default px')
parser.add_argument('--to', '-t', default='rem', help='The target unit; Default rem')
parser.add_argument('--factor', default=1, type=float, help='The factor to be multiplex before convert')
parser.add_argument('--verbosity', '-v', type=int, default=2, help='The verbosity when running; Default is 2')
parser.add_argument('--format', type=str, default="%(asctime)-15s %(message)s", help='The default logging format')
parser.add_argument('files', nargs='+', type=str, help='The target source file/folder')
args=parser.parse_args()

logging.basicConfig(format=args.format)
logger=logging.getLogger('vgallery.conv')
verbosity=int(args.verbosity)
if verbosity==3:
   logger.setLevel(logging.DEBUG)
elif verbosity==2:
   logger.setLevel(logging.INFO)
elif verbosity==1:
   logger.setLevel(logging.WARNING)
else:
   logger.setLevel(logging.ERROR)

listdir=lambda d: sorted( os.listdir(d) )
units={
   'px': {
      'rem': 0.0625,
      'pt': 0.74999943307122,
      'px': 1,
   }, 
   'rem': {
      'px': 16,
      'pt': 11.99999092914,
      'rem': 1,
   },
}


def convert( line ):
   m=re.search(r'\d+(\.\d+)?px', line)
   while m:
      trg=m.group()
      val=float(re.search(r'\d+(\.\d+)?', trg).group())
      val*=units[getattr(args, 'from')][getattr(args, 'to')]
      val*=getattr(args, 'factor')
      val="{0}rem".format(val)
      line='{0}{1}{2}'.format(line[0:m.start()], val, line[m.end():])
      m=re.search(r'\d+(\.\d*)?px', line)

   return line

def conv( target ):
   if os.path.isdir(target) and args.recursive:
      for f in listdir(target):
         conv(os.path.join(target, f))
   else:
      name=os.path.basename(target)
      if name.startswith('.'): return     #Ignore the hidden file
      if name=='Thumbs.db': return        #Ignore the Thumbs.db
      logger.info('Converting file: {0}'.format(target))
      lines=open(target, 'r').read()
      with open(target, 'w') as f:
         for ln in lines.splitlines():
            f.write( '{0}\n'.format( convert(ln) ) )

logger.warning('Converting file(s) {3} -- from {0} to {1} with {2} factor(s)'.format(getattr(args, 'from'), args.to, args.factor, args.files))
if hasattr(args.files, '__iter__') and hasattr(args.files, '__getitem__'):
   for f in args.files:
      conv(f)
