import logging, multiprocessing, os, sys, json, importlib, traceback, time

def processTask(task):
  sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'consumers/'))
  logFormat = ('%(asctime)s - %(levelname)s - %(name)s - %(funcName)s: %(message)s')
  logging.basicConfig(level=logging.INFO, format=logFormat)
  consumer = getattr(importlib.import_module(task['consumer']), task['consumer'])(task)
  try:
    consumer.run()
  except KeyboardInterrupt:
    consumer.stop()

scriptPath = os.path.dirname(os.path.realpath(__file__))
configPath = os.path.join(scriptPath, 'config.json')
config = open(configPath).read()
config = json.loads(config)

multiprocessing.log_to_stderr()

pool = multiprocessing.Pool(len(config['tasks']))
processes = []
#processTask(config['tasks'][0])
for task in config['tasks']:
  processes.append(pool.apply_async(processTask, [task]))
pool.close()
pool.join()

for process in processes:
  process.get()
