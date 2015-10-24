import sys
import MySQLdb
import numpy 
#################################################
#in this program ,we just want to save the svg picture but display the plot,
#because some environment don't support the gui,like ssh, so we use the 
#following two row to avoid matplotlib display
#Must be before importing matplotlib.pyplot or pylab!
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
###############################################
import time
from generateLink import *

def cal_mean_std(alist):
    temp_len = len(alist) 
    narray = numpy.array(alist)
    sum1 = narray.sum()
    narray2 = narray*narray
    sum2= narray2.sum()
    temp_mean = sum1/temp_len
    temp_std = (sum2/temp_len-temp_mean**2)**0.5
    return (temp_mean,temp_std)

def stat(columns_R_time,columns_C_time,columns_runtime):
    ###
    stat_interval_time = 1E9
    frequency = []
    mean = []
    std = []
    pre_i = 0
    temp_frequency = 0
    record_num = len(columns_R_time)
    total_run_time = columns_R_time[record_num-1]-columns_C_time[0]
    total_second =int(total_run_time/stat_interval_time)+1
    c_second = 0##current second
    ###c_p current point the return time    
    ###s_P start point
    ###e_p end point 
    ###start time int(columns_C_time[0]/1E9)*1E9
    s_p = stat_interval_time*c_second+int(columns_C_time[0]/1E9)*1E9
    e_p = stat_interval_time*(c_second+1)+int(columns_C_time[0]/1E9)*1E9
    
    #in order to find the pre_i and i ,we use a var location to represent them
    location=[]
    for i in range(0,record_num):
        c_p = columns_R_time[i]
    
        if (c_p<=e_p)and(c_p>s_p):
    	    temp_frequency += 1
        else:
	    (temp_mean,temp_std) = cal_mean_std(columns_runtime[pre_i:i])
       	    frequency.append(temp_frequency)
       	    mean.append(temp_mean)
       	    std.append(temp_std)
       	    location.append([pre_i,i])
       	    temp_frequency = 1
       	    pre_i = i

            second_need_skip = int((c_p-e_p)/stat_interval_time) + 1
    	    for j in range(0,second_need_skip-1):
    	        frequency.append(0)
    	        mean.append(0)
    	        std.append(0)
    	        location.append([0,0])#[0,0]means there are no function call in this time
    	
    	    s_p = s_p+second_need_skip*stat_interval_time
    	    e_p = e_p+second_need_skip*stat_interval_time
    	
    ###caculate the last item
    ###if pre_i is the last item,we would not calculate
    if pre_i!=record_num-1:
	(temp_mean,temp_std) = cal_mean_std(columns_runtime[pre_i:record_num-1])
        frequency.append(temp_frequency)
        mean.append(temp_mean)
        std.append(temp_std)
        location.append([pre_i,record_num])
    return (frequency,mean,std,location)

### rstart_time represent the 0 on x-axis 
def plotshow(frequency,mean,std,start_time):
    xData = numpy.arange(len(frequency))
    fig = plt.figure()
    figure = plt.gcf() # get current figure
    figure.set_size_inches(19, 10)
    ax1 = fig.add_subplot(311)
    ax1.plot(xData, frequency,'r',label="frequency")
    ax1.plot(xData, frequency,'b.')
    ax1.set_ylabel('frequency')
    ax1.set_xlabel('start_time: '+str(start_time)+'ns')
    
    ax2 = fig.add_subplot(312)
    ax2.plot(xData,mean,'g',label="mean")
    ax2.plot(xData,mean,'r.')
    ax2.set_ylabel('mean')
    ax2.set_xlabel('start_time: '+str(start_time)+'ns')
    
    ax3 = fig.add_subplot(313)
    ax3.plot(xData,std,'b',label="std")
    ax3.plot(xData,std,'r.')
    ax3.set_ylabel('std')
    ax3.set_xlabel('start_time: '+str(start_time)+'ns')
#    plt.show()
    plt.savefig('abc.svg')

### plot just one figure
def plotshow_one(stat_para,start_time,exception_type):
    
    xData = numpy.arange(len(stat_para))
    fig =  plt.figure()
    figure = plt.gcf() # get current figure
    figure.set_size_inches(19, 10)#the default dpi is 90,so the image size should be [19*90,10*90] of the inch size 19*10 
    ax = fig.add_subplot(111)
    ax.plot(xData, stat_para,'r',label=exception_type)
    ax.plot(xData, stat_para,'b.')
    ax.set_ylabel(exception_type)
    ax.set_xlabel('start_time: '+str(start_time)+'ns')
    pic_name = exception_type+'.svg' 
    plt.savefig(pic_name);


def generate_url(dlist_id):
    url = 'http://os.cs.tsinghua.edu.cn:280/lxr/systrace-perl?v=linux-3.5.4&\
f=&a=x86_32&path0=' + str(dlist_id-250)+'&path1='+str(dlist_id+250)


###restat frequency,mean,std heading time ,similar to the first statistics,but add the the condition pid fixed
###ex_pid_set:exception pid set
def restat_bypid(ex_pid_set,columns_pid,columns_R_time,columns_C_time,columns_runtime):
    set_len = len(ex_pid_set)
    temp_columns_R_time = [[] for i in range(set_len)]
    temp_columns_C_time = [[] for i in range(set_len)]
    temp_columns_runtime = [[] for i in range(set_len)]
    restat_result=[]
    pid_count = 0
    record_num = len(columns_R_time)
    for pid in ex_pid_set:
	for i in range(0,record_num):
            if columns_pid[i]==pid:
    	        temp_columns_R_time[pid_count].append(columns_R_time[i])
    	        temp_columns_C_time[pid_count].append(columns_C_time[i])
    	        temp_columns_runtime[pid_count].append(columns_runtime[i])
    	(frequency_temp,mean_temp,std_temp,location_temp) = stat(temp_columns_R_time[pid_count],temp_columns_C_time[pid_count],temp_columns_runtime[pid_count])
	
	restat_result.append([frequency_temp,mean_temp,std_temp,location_temp,temp_columns_R_time[pid_count][0]])
	pid_count+=1
    
    return restat_result

###
def get_dlistid_pid_set(loc,columns_pid,location,columns_dlist_id):
### loc: location of the max frequency
    pid_set = list(set(columns_pid[location[loc][0]:location[loc][1]]))
    pid_count=0
    result_dlistid_pid=[]
    for pid in pid_set:
        for i in range(location[loc][0],location[loc][1]):
            if columns_pid[i]==pid:
                result_dlistid_pid.append([columns_dlist_id[i],pid])
    return result_dlistid_pid
###    
def main(f_id,exception_type,restat_from_begin):
#    stat_interval_time = 1E9 
###    f_id =28489
    try:
        conn=MySQLdb.connect(host='localhost',user='cgrtl',passwd='9-410',db='aoquan',port=3306)
        cur=conn.cursor()
    ###
        cur.execute('select R_time,C_time,RunTime,pid,DLIST_id from `linux-3.5.4_R_x86_32_DLIST` where C_point=%s',(f_id))
        lines = cur.fetchall()
        record_num = len(lines)
        columns =[['',0] for i in range(record_num)]
        count = 0
        for line in lines:
    ### generate a fixed length str,for the convenience of comparing
    	    R_time = line[0]
    	    C_time = line[1]
    	    Runtime=line[2]
    	    pid = line[3]
	    dlist_id = line[4]
    	    columns[count] = [R_time,C_time,Runtime,pid,dlist_id]
    	    count+=1
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])    
    
    ### sort columns by C_time   
    columns.sort()
    columns_runtime = [i for i in range(record_num)]
    columns_C_time = [i for i in range(record_num)]
    columns_R_time = [i for i in range(record_num)]
    columns_pid = [i for i in range(record_num)]
    columns_dlist_id = [i for i in range(record_num)]
    
    for i in range(0,record_num):
        columns_R_time[i] =columns[i][0]
        columns_C_time[i] =columns[i][1]
        columns_runtime[i] = columns[i][2]
        columns_pid[i] = columns[i][3]
	columns_dlist_id[i] = columns[i][4]
   
    ###get the stat information and the corresponding location
    (frequency,mean,std,location) = stat(columns_R_time,columns_C_time,columns_runtime)
    ###in this program ,start time is the first time the function return minus 1E9
#    plotshow(frequency,mean,std,int(columns_R_time[0]/1E9)*1E9)
###################################################################################################################
    if exception_type=='frequency':
        plotshow_one(frequency,int(columns_R_time[0]/1E9)*1E9,'frequency')
        ###location of the max frequency
        loc_max_frequency = frequency.index(max(frequency))
        ###the set of pid which result in the frequency exception
        pid_frequency_set = list(set(columns_pid[location[loc_max_frequency][0]:location[loc_max_frequency][1]]))
        ###find exception by pid set,time is limited in the exception time
        restat_runtime=[[] for i in range(len(pid_frequency_set))]
        pid_count=0
        for pid in pid_frequency_set:
            for i in range(location[loc_max_frequency][0],location[loc_max_frequency][1]):
                if columns_pid[i]==pid:
                    restat_runtime[pid_count].append(columns_runtime[i])
            pid_count+=1
	dlistid_set_per_second=[]
	for loc in range(0,len(frequency)):
	    dlistid_set_per_second.append(get_dlistid_pid_set(loc,columns_pid,location,columns_dlist_id))
	generateLink("frequency",dlistid_set_per_second)
	    
        ### if you want to stat the exceptional function belong to the exceptional pid from the very beginning, you may use the code below
        if restat_from_begin==True:
            restat_result = restat_bypid(pid_frequency_set,columns_pid,columns_R_time,columns_C_time,columns_runtime)
            pid_count = 0
            for pid in pid_frequency_set:
                plotshow(restat_result[pid_count][0],restat_result[pid_count][1],restat_result[pid_count][2],int(restat_result[pid_count][4]/1E9)*1E9)
    	        pid_count+=1

    
###################################################################################################################
    if exception_type=='mean':
        plotshow_one(mean,int(columns_R_time[0]/1E9)*1E9,'mean')
        ###location of the max mean 
        loc_max_mean = mean.index(max(mean))
    	#print 'location of the max mean:',loc_max_mean
   	###the set of pid which result in the mean exception
    	pid_mean_set = list(set(columns_pid[location[loc_max_mean][0]:location[loc_max_mean][1]]))
        restat_runtime=[[] for i in range(len(pid_mean_set))]
        pid_count=0
        for pid in pid_mean_set:
            for i in range(location[loc_max_mean][0],location[loc_max_mean][1]):
                if columns_pid[i]==pid:
                    restat_runtime[pid_count].append(columns_runtime[i])
            pid_count+=1

	dlistid_set_per_second=[]
	for loc in range(0,len(mean)):
	    dlistid_set_per_second.append(get_dlistid_pid_set(loc,columns_pid,location,columns_dlist_id))
	generateLink("mean",dlistid_set_per_second)
	
        if restat_from_begin==True:
            restat_result = restat_bypid(pid_mean_set,columns_pid,columns_R_time,columns_C_time,columns_runtime)
            pid_count = 0
            for pid in pid_mean_set:
                plotshow(restat_result[pid_count][0],restat_result[pid_count][1],restat_result[pid_count][2],int(restat_result[pid_count][4]/1E9)*1E9)
                pid_count+=1
        

###################################################################################################################
    if exception_type=='std':
        plotshow_one(std,int(columns_R_time[0]/1E9)*1E9,'std')
        ###location of the max std
    	loc_max_std = std.index(max(std))
    	###the set of pid which result in the std exception
    	pid_std_set = list(set(columns_pid[location[loc_max_std][0]:location[loc_max_std][1]]))
        restat_runtime=[[] for i in range(len(pid_std_set))]
        pid_count=0
        for pid in pid_std_set:
            for i in range(location[loc_max_std][0],location[loc_max_std][1]):
                if columns_pid[i]==pid:
                    restat_runtime[pid_count].append(columns_runtime[i])
            pid_count+=1
	
	dlistid_set_per_second=[]
	for loc in range(0,len(std)):
	    dlistid_set_per_second.append(get_dlistid_pid_set(loc,columns_pid,location,columns_dlist_id))
	generateLink("std",dlistid_set_per_second)
        
	if restat_from_begin==True:
            restat_result = restat_bypid(pid_std_set,columns_pid,columns_R_time,columns_C_time,columns_runtime)
            pid_count = 0
            for pid in pid_mean_set:
                plotshow(restat_result[pid_count][0],restat_result[pid_count][1],restat_result[pid_count][2],int(restat_result[pid_count][4]/1E9)*1E9)
                pid_count+=1
    
###################################################################################################################
###run main()
start = time.time()
main(sys.argv[1],sys.argv[2],False)
###print the time consuming
end = time.time()
print  'take %f s' %(end-start)
