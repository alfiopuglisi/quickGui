
def task(qin, qout):

   while True:
       cmd = qin.get()
       if cmd is None:
           break
       try:
           qout.put(eval(cmd))
       except Exception:
           pass


