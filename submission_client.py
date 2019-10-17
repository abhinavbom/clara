import os
import sys
import socket
import argparse
import struct
import json
import time
import hashlib
import random
from conf import config
from datetime import datetime as dt

class FSFClient:
   def __init__(self, fullpath, filename, delete, source, archive, suppress_report, full, file, lambda_result):

         self.fullpath = fullpath
         self.filename = filename
         self.delete = delete
         self.source = source
         self.archive = archive
         self.suppress_report = suppress_report
         self.full = full
         self.file = file
         self.lambda_result = lambda_result
         # will hold host after verifying connection to server
         self.host = ''
         self.port = config.SERVER_CONFIG['PORT']
         self.logfile = config.CLIENT_CONFIG['LOG_FILE']
         self.server_list = config.SERVER_CONFIG['IP_ADDRESS']
         
   # Test connection to randomized server and rudimentary fail over
   def initiate_submission(self):
      
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      random.shuffle(self.server_list)
      attempts = 0
      
      for server in self.server_list:
          success = 1
          try:
              sock.connect((server, self.port))
          except:
              warning ='%s There was a problem connecting to %s on port %s. Trying another server. <WARN>\n' % (dt.now(), server, self.port)
              self.issue_error(warning)
              success = 0
              attempts += 1
          if success:
              self.host = server
              self.process_files(sock)
              break
          elif attempts == len(self.server_list):
              e = sys.exc_info()[0]
              error = '%s There are not servers available to send files too. Error: %s\n' % (dt.now(), e)
              self.issue_error(error)


   # Send files to server for processing and await results
   def process_files(self, sock):

      msg = '%sFSF_RPC%sFSF_RPC%sFSF_RPC%sFSF_RPC%sFSF_RPC%s' % (self.filename, self.source, self.archive, self.suppress_report, self.full, self.file)
      #print(msg)
      #print(type(msg))
      print("this is lambda data")
      print(self.lambda_result)
      buffer = struct.pack('>I', len(msg)) + 'FSF_RPC'.encode('utf-8') + msg.encode('utf-8')

      try:
         sock.sendall(buffer)
      except:
         e = sys.exc_info()[0]
         error = '%s There was a problem sending file %s to %s on port %s. Error: %s\n' % (dt.now(), self.filename, self.host, self.port, e)
         self.issue_error(error)

      finally:

         if self.delete:
            os.remove(self.fullpath)

         if not self.suppress_report:
            res = self.process_results(sock)

         return res
         sock.close()

   # Process the results sent back from the FSF server
   def process_results(self, sock):

      try:
         raw_msg_len = sock.recv(4)
         msg_len = struct.unpack('>I', raw_msg_len)[0]
         data = ''

         while len(data) < msg_len:
            recv_buff = sock.recv(msg_len - len(data))
            data += recv_buff
         data += self.lambda_result
         print (data)

         return data

         # Does the user want all sub objects?
         if self.full:
            # Generate dirname by calculating epoch time and hash of results
            dirname = 'fsf_dump_%s_%s' % (int(time.time()), hashlib.md5(data).hexdigest())
            self.dump_subobjects(sock, dirname)

      except:
         e = sys.exc_info()[0]
         error = '%s There was a problem getting data for %s from %s on port %s. Error: %s' % (dt.now(), self.filename, self.host, self.port, e)
         self.issue_error(error)

   # Dump all subobjects returned by the scanner server
   def dump_subobjects(self, sock, dirname):

      sub_status = sock.recv(4)
      if sub_status == 'Null':
         print ('No subobjects were returned from scanner for %s.' % self.filename)
         return

      os.mkdir(dirname)

      while self.full:
         raw_sub_count = sock.recv(4)
         sub_count = struct.unpack('>I', raw_sub_count)[0]
         raw_msg_len = sock.recv(4)
         msg_len = struct.unpack('>I', raw_msg_len)[0]
         data = ''

         while len(data) < msg_len:
            recv_buff = sock.recv(msg_len - len(data))
            data += recv_buff

         fname = hashlib.md5(data).hexdigest()
         with open('%s/%s' % (dirname, fname), 'w') as f:
            f.write(data)
            f.close

         if sub_count == 0:
            self.full = False

      print ('Sub objects of %s successfully written to: %s' % (self.filename, dirname))

   # Either log to log file or print to stdout depending on flags used
   def issue_error(self, error):

      if self.suppress_report:
         with open(self.logfile, 'a') as f:
            f.write(error)
            f.close()
      else:
         print (error)

if __name__ == '__main__':

   parser = argparse.ArgumentParser(prog='fsf_client', description='Uploads files to scanner server and returns the results to the user if desired. Results will always be written to a server side log file. Default options for each flag are designed to accommodate easy analyst interaction. Adjustments can be made to accommodate larger operations. Read the documentation for more details!')
   parser.add_argument('file', nargs='*', type=argparse.FileType('r'), help='Full path to file(s) to be processed.')
   parser.add_argument('--delete', default=False, action='store_true', help='Remove file from client after sending to the FSF server. Data can be archived later on server depending on selected options.')
   parser.add_argument('--source', nargs='?', type=str, default='Analyst', help='Specify the source of the input. Useful when scaling up to larger operations or supporting multiple input sources, such as; integrating with a sensor grid or other network defense solutions. Defaults to \'Analyst\' as submission source.')
   parser.add_argument('--archive', nargs='?', type=str, default='none', help='Specify the archive option to use. The most common option is \'none\' which will tell the server not to archive for this submission (default). \'file-on-alert\' will archive the file only if the alert flag is set. \'all-on-alert\' will archive the file and all sub objects if the alert flag is set. \'all-the-files\' will archive all the files sent to the scanner regardless of the alert flag. \'all-the-things\' will archive the file and all sub objects regardless of the alert flag.')
   parser.add_argument('--suppress-report', default=False, action='store_true', help='Don\'t return a JSON report back to the client and log client-side errors to the locally configured log directory. Choosing this will log scan results server-side only. Needed for automated scanning use cases when sending large amount of files for bulk collection. Set to false by default.')
   parser.add_argument('--full', default=False, action='store_true', help='Dump all sub objects of submitted file to current directory of the client. Format or directory name is \'fsf_dump_[epoch time]_[md5 hash of scan results]\'. Only supported when suppress-report option is false (default).')

   if len(sys.argv) == 1:
      parser.print_help()
      sys.exit(1)

   try:
      args = parser.parse_args()
   except IOError:
      e = sys.exc_info()[1]
      print ('The file provided could not be found. Error: %s' % e)
      sys.exit(1)

   if len(args.file) == 0:
      print ('A file to scan needs to be provided!')
   
   archive_options = ['none', 'file-on-alert', 'all-on-alert', 'all-the-files', 'all-the-things']
   if args.archive not in archive_options:
      print ('Please specify a valid archive option: \'none\', \'file-on-alert\', \'all-on-alert\', \'all-the-files\' or \'all-the-things\'.')
      sys.exit(1)
   
   for f in args.file:
      filename = os.path.basename(f.name)
      file = f.read()
      fsf = FSFClient(f.name, filename, args.delete, args.source, args.archive, args.suppress_report, args.full, file)
      fsf.initiate_submission()
