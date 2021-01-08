
exclude_list = ['test','','my_label','test1']











import pandas as pd
import copy
import arrow
import datetime
import argparse
from numpy.random import uniform
import matplotlib


parser = argparse.ArgumentParser()
parser.add_argument('-w','--weeks', nargs='?', type = int, const = 0, help = 'How many weeks ago?', default = 0)
parser.add_argument('-d','--days',  nargs='?', type = int, const = 0, help = 'How many days ago?' , default = 0)
parser.add_argument('-f','--format', nargs='?', required = True, help = 'Choose either "d" for days or "w" for weeks')
parser.add_argument('-p','--plot', nargs = '?', type = int, const = 1, help = 'Set this to True to remove the plot', default = 0)
parser.add_argument('-c','--fraction', nargs = '?', type = int, const = 0, help = 'Set this to 1 to display fraction', default = 0)
args = parser.parse_args()

true_list = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']
label_list = exclude_list
shift_times = {"weeks":args.weeks, "days": args.days}

if args.format == 'w':
  y_axis_format = 3600
  y_axis_label = "Hours"
  span_format = 'week'
  span_format_2 = 'day'
  x_ticks = ['Mon', 'Tue', 'Wed','Thu','Fri','Sat','Sun']


else:
  y_axis_format = 60
  y_axis_label = "Minutes"
  span_format = 'day'
  span_format_2 = 'hour'

def gethour_ls(hour_ls, app_list):
    
    if args.format == "w":
        return hour_ls + [app_list[i][0].strftime("%a") for i in range(len(app_list))]
        
    else:
        return hour_ls + [app_list[i][0].hour for i in range(len(app_list))]

def correct_columns(df):
    hour_ls = []
    time_ls = []
    label_ls = []

    rand_array = uniform(low = 0, high = 0.1, size = (1,len(df))) # To make the values distinct from each other
    dt_array = [datetime.timedelta(seconds = i) for i in rand_array[0]]

    df['start'] = df['start'].to_numpy() + dt_array

    for num, index  in enumerate(df.index):

        start = df['start'][index]
        end = df['end'][index]

        app_list = [list(i) + [df['label'][index]] for i in arrow.Arrow.span_range(span_format_2,start,end)]
    
    

        app_list[0][0] = arrow.get(start)
        app_list[-1][-2] = arrow.get(end)
        
        hour_ls = gethour_ls(hour_ls, app_list)
        time_ls = time_ls + [(app_list[i][1] - app_list[i][0]).total_seconds() / y_axis_format for i in range(len(app_list))]
        label_ls = label_ls + [app_list[i][2] for i in range(len(app_list))]


    return pd.DataFrame({'Span':hour_ls, 'Total':time_ls, 'Label':label_ls}) 
    return pd.DataFrame({'Span':hour_ls, 'Total':time_ls, 'Label':label_ls}).groupby(by = 'Span').sum() 


def stack_format(df_group):

    df2 = df_group.groupby(['Span', 'Total', 'Label'])['Span'].count().unstack('Label').fillna(0)
    df3 = df2.index.get_level_values('Total').to_numpy().reshape(len(df2),1) * df2

    return df3.reset_index().drop(['Total'], axis = 1).groupby('Span').sum()

arrow_lw = arrow.now('Europe/London').shift(**shift_times).floor(span_format)
dt_lw = datetime.datetime.strptime(str(arrow_lw),'%Y-%m-%dT%H:%M:%S%z')
arrow_up = arrow.now('Europe/London').shift(**shift_times).ceil(span_format)
dt_up = datetime.datetime.strptime(str(arrow_up),'%Y-%m-%dT%H:%M:%S.%f%z')



df_raw = pd.read_csv("times.csv", names = ["start","end","label"])
df = copy.deepcopy(df_raw)


form = '%Y-%m-%d %H:%M:%S %z'
df['start'] = pd.to_datetime(df['start'], format = form) # Transforms to a datetime format
df['end'] = pd.to_datetime(df['end'], format = form)


df_na = df[df['label'].notna()] # Drops all  NaN values

df_lab = df_na[~df_na['label'].isin(label_list)] # Drop all which are in the label list

df_recent = df_lab[df_lab['start'] > dt_lw] # Exclude values before lower limit
df_recent = df_recent[df_recent['start'] < dt_up] # Exclude values after upper limit



df_group = correct_columns(df_recent)
df_group_stack = stack_format(df_group)
df_group_stack_sorted_summed = df_group_stack.sum(axis=1)
df_group_stack_sorted_summed_notnowork = df_group_stack.drop(['notwork'],axis=1, errors='ignore').sum(axis=1)


if len(df_group) < 1:
    print("Empty")

elif not args.plot:
    tot_sec = df_group['Total'].sum() * y_axis_format
    print("Total {}:{:02d}".format(int(tot_sec//3600),int(tot_sec/60 %60)))

    tot_sec_notnowork = df_group_stack_sorted_summed_notnowork.sum() * y_axis_format
    print("Total work {}:{:02d}\n".format(int(tot_sec_notnowork//3600),int(tot_sec_notnowork/60 %60)))

    for col in df_group_stack:
        frac = df_group_stack[col].sum() * y_axis_format / tot_sec * 100
        print("{}: {:.1f}%".format(col, frac))

    if args.format == "w":
        df_group_stack.index = df_group_stack.index.str.strip()
        df_group_stack = df_group_stack.reindex(x_ticks)
        df_group_stack_sorted_summed = df_group_stack.sum(axis=1)
        df_group_stack_sorted_summed_notnowork = df_group_stack.drop(['notwork'],axis=1, errors='ignore').sum(axis=1)


    if args.fraction:
        print("")
        st = ""
        st+="     {:}".format("    ".join(df_group_stack))
        for index, values in df_group_stack.iterrows():
            st+="\n{}".format(index)

            for key, value in zip(values.keys(),values):

                if value != value:
                    st+= "    {} ".format("NA")
                    continue

                if args.format == "w":
                    st += "{:4}:{:02d}".format(int(value),int(value*60 %60))
                else:
                    st+= "    {:02d}".format(int(value))
        print(st)

        print("\n    Total notnowork")
        for label_notnowork, value_summed_notnowork in zip(df_group_stack_sorted_summed_notnowork.keys(),df_group_stack_sorted_summed_notnowork):

            if args.format == "w":
                print("{}  {}:{:02d}".format(label_notnowork,int(value_summed_notnowork),int(value_summed_notnowork*60 %60)))
            else:
                print("{}  {:02d}".format(label_notnowork,int(value_summed_notnowork)))

        print("\n    Total")
        for label, value_summed in zip(df_group_stack_sorted_summed.keys(),df_group_stack_sorted_summed):

            if args.format == "w":
                print("{}  {}:{:02d}".format(label,int(value_summed),int(value_summed*60 %60)))
            else:
                print("{}  {:02d}".format(label,int(value_summed)))

else:
    #matplotlib.use('tkagg')
    import matplotlib.pyplot as plt
    df_group_stack.plot.bar(stacked = True)
    plt.xlabel("")
    plt.ylabel(y_axis_label)
    tot_sec = df_group['Total'].sum() * y_axis_format
    plt.title("Total {}:{:02d}".format(int(tot_sec//3600),int(tot_sec/60 %60)))
    plt.show()






