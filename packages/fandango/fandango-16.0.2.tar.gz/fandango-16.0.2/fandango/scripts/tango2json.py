#!/usr/bin/env python3

import fandango as fn
import sys,json,gzip

__doc__ = """
Usage:

 > tango2json.py [--compress] [--commands] [--properties] [--attributes] "filename.json" dev/name/1 "dev/exp/*"
 
Attribute config is not exported unless devices are exported!
 
To reload the data from ipython:

  import json
  f = open('filename.json')
  data = eval(json.load(f,encoding='latin-1'))
  f.close()
  
  print(data.keys())
  
"""

def main():
  args,params,devs,data = [],[],[],fn.CaselessDict()

  t0 = fn.now()
  i = 1
  source = ''

  while i<len(sys.argv):
    a = sys.argv[i]
    if a.startswith('-'):
      if a == '--source':
        i+=1
        source = sys.argv[i]
      else:
        params.append(a)
    else:
      args.append(a)
    i+=1

  if not args[1:]:
    print(__doc__)
    sys.exit(-1)

  if not source:
    #servers = [d.split('/',1)[1].lower() for d in fn.find_devices('dserver/*/*')]
    for mask in args[1:]:
      exported = '--attributes' in params
      print("mask is %s, exported=%s" % (mask,exported))
      if mask.count('/')==1 and not fn.isRegexp(mask.split('/',1)[0]):
        servers = fn.Astor(mask)
        server_devs = servers.get_all_devices() + ['dserver/'+d for d in servers.keys()]
        devs.extend([d for d in server_devs if not exported or fn.check_device(d)])
      devs.extend(fn.get_matching_devices(mask,exported=exported))
  else:
    raise 'Reading attr config from file not implemented'

  filename = args[0] if '--compress' not in params else args[0]+'.gz'

  print('Exporting %d devices to %s'%(len(devs),filename))
  print(devs[:10],'...')

  for d in devs:
    if d not in data:
      try:
          data[d] = fn.tango.export_device_to_dict(d,
              commands = '--commands' in params,
              properties = '--properties' in params
              )
      except:
          print('%s export failed!!!' % d)
          print(fn.except2str())
          break

  data = fn.dict2json(data) #Do not convert, just filters

  if '--compress' in params:
    try:
      jdata = json.dumps(data,encoding='latin-1')
    except:
      jdata = json.dumps(data)
    f = gzip.open(filename,'wb')
    f.write(jdata)
    f.close()
  else:
    try:
      json.dump(data,open(filename,'w'),encoding='latin-1')
    except:
      json.dump(data,open(filename,'w'))

  print('Finished in %d seconds.'%(fn.now()-t0))
  print(fn.shell_command('ls -lah %s'%filename))

if __name__ == '__main__':
  main()
