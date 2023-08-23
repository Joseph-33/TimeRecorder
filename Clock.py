import sys
import select
import os
import arrow
import time
import math

timezone = time.tzname[time.daylight]

my_label = " ".join(sys.argv[1:])
if not my_label.strip():
    print("Please add a label, you can do this by adding words after 'python Clock.py' ")
    sys.exit(0)

dt_format = 'YYYY-MM-DD HH:mm:ss ZZ'

i = 0
filename = "times.csv"
tmp_filename = ".tmp_times.csv"

def check_tmp():

    fileexists = os.path.isfile(tmp_filename)
    if fileexists:

        with open(tmp_filename,'r') as fil:
            content = fil.read()

        message = "The above time was found, this could be because the program didn't previously exit properly, would you like to append this to your {}? (y/n)\n".format(filename)
        input_message = content + "\n\n" + message

        ans = input(input_message)
        if ans.lower() == "y":
            with open(filename,'a') as fil:
                fil.write( "\n" + content)
        os.remove(tmp_filename)

def append_to_file(filename, content):
    with open(filename, 'a+') as file:
        file.seek(0, 2)  # Move to the end of the file
        
        # Check if the last line is empty or does not end with a newline
        file.seek(file.tell() - 1, 0)
        last_char = file.read(1)
        if last_char != '\n' and last_char != '':
            file.write('\n')
        
        file.write(content)

def ti(x):
    minute = " {:02d}:{:02d} {}".format(math.floor((x%3600)/60),x%60,my_label)
    hour = " {:02d}:{:02d}:{:02d} {}".format(math.floor(x/3600),math.floor((x%3600)/60),x%60,my_label)
    
    if x/3600 >= 1:
        return hour
    
    return minute

check_tmp()
start_time = time.time()
start_dt = arrow.now(timezone).format(dt_format)

while True:

    if i % 60 == 0:
        os.system('printf "\033c"')

        end_dt = arrow.now(timezone).format(dt_format) # Create a temporary file for if it id not saved properly.
        if i != 0:
            with open(tmp_filename,'w') as file:
                file.write("{},{},{}".format(start_dt, end_dt, my_label))

    
    print(ti(i), end='\r')
    i+=1
    time.sleep(1-(time.time() - start_time-i))
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        
        end_dt = arrow.now(timezone).format(dt_format)
        #append_to_file(filename, "\n{},{},{}".format(start_dt, end_dt, my_label))
        with open(filename,'a') as file:
            file.write("\n{},{},{}".format(start_dt, end_dt, my_label))

        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)
        
        
        break
        
        


print("{} seconds".format(i))

