from src.modules.common import ScriptExtractor
import time


extractor = ScriptExtractor("dictionary_1.0.2.csv")

time_start = time.time()
script = extractor.get_script("script-0006")
time_end = time.time()
print(script)
print('time:', time_end-time_start)

time_start = time.time()
script = extractor.get_script("script-0006")
time_end = time.time()
print(script)
print('time:', time_end-time_start)

time_start = time.time()
script = extractor.get_script("script-0006")
time_end = time.time()
print(script)
print('time:', time_end-time_start)

time_start = time.time()
script = extractor.get_script("script-0007")
time_end = time.time()
print(script)
print('time:', time_end-time_start)