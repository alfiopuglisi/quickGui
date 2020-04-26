
def task_dispatch(qin, qout):

   while True:
       cmd = qin.get()
       if cmd is None:
           break
       try:
           qout.put('RESULT '+str(eval(cmd)))
       except Exception:
           pass


