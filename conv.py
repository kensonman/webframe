#!/usr/bin/python3
# File:     /src/vgallery/conv.py
# Author:   Kenson Man <kenson@mansonsolutions.hk>
# Date:     2020-06-13 23:45
# Desc:     Convert the unit to specific unit. e.g.: px to rem
#
import argparse, logging, os
parser = argparse.ArgumentParser()
parser.add_argument('--recursive', '-r', action='store_true', help='Convert the files recursivelly')
parser.add_argument('--from', '-f', default='px', help='The source unit; Default px')
parser.add_argument('--to', '-t', default='rem', help='The target unit; Default rem')
parser.add_argument('--fact', default=1, type=float, help='The fact to be multiplex before convert')
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


def conv( target ):
   if os.path.isdir(target):
      pass
   else:
      logger.info('Converting file: {0}'.format(target))

if hasattr(args.files, '__iter__') and hasattr(args.files, '__getitem__'):
   for f in args.files:
      conv(f)
