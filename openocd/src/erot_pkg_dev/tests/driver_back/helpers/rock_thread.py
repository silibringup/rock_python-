import sys
import threading
from sys import settrace
from RoPy import rpinfo
import time

class rock_thread(threading.Thread):
  def __init__(self, name,*args, **keywords):
    threading.Thread.__init__(self, *args, **keywords)
    self.name   = name
    self.killed = False
    self.in_transport_routine = 0
 
  def start(self):
    self.__run_backup = self.run
    self.run = self.__run     
    threading.Thread.start(self)

  def __run(self):
    sys.settrace(self.globaltrace)
    threading.currentThread().name = self.name
    self.__run_backup()
    self.run = self.__run_backup
 
  def globaltrace(self, frame, event, arg):
    code = frame.f_code
    func_name = code.co_name
    line_no = frame.f_lineno
    if func_name == 'transport':
      if event == 'call' :
        self.in_transport_routine = 1
      if event == 'return' :
        self.in_transport_routine = 0

    if self.killed and (self.in_transport_routine == 0) :
      raise SystemExit()   
    return self.globaltrace
 
  def kill(self):
    self.killed = True
    cur_time = time.time()
    self.join()
    rpinfo(f"Thread {self.name} was Killed using {int(1000.0*(time.time()-cur_time))} ms")




