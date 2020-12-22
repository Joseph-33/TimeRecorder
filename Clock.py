import sys
import select
import os
import arrow
import time
import math

my_label = " ".join(sys.argv[1:])

dt_format = 'YYYY-MM-DD HH:mm:ss ZZ'

i = 0
start_time = time.time()
start_dt = arrow.now('Europe/London').format(dt_format)

def ti(x):
    minute = " {:02d}:{:02d} {}".format(math.floor((x%3600)/60),x%60,my_label)
    hour = " {:02d}:{:02d}:{:02d} {}".format(math.floor(x/3600),math.floor((x%3600)/60),x%60,my_label)
    
    if x/3600 >= 1:
        return hour
    
    return minute


while True:

    if i % 10 == 0:
        os.system('printf "\033c"')
    
    print(ti(i), end='\r')
    i+=1
    time.sleep(1-(time.time() - start_time-i))
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        
        end_dt = arrow.now('Europe/London').format(dt_format)
        
        with open("times.csv",'a') as file:
            file.write("\n{},{},{}".format(start_dt, end_dt, my_label))
        
        
        break
        
        


print("{} seconds".format(i))

