import MySQLdb
import numpy 
import matplotlib.pyplot as plt 
import time

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
    ax1 = fig.add_subplot(311)
    ax1.plot(xData, frequency,'r',label="frequency")
    ax1.plot(xData, frequency,'b*')
    ax1.set_ylabel('frequency')
    ax1.set_xlabel('start_time: '+str(start_time)+'ns')
    
    ax2 = fig.add_subplot(312)
    ax2.plot(xData,mean,'g',label="mean")
    ax2.plot(xData,mean,'r*')
    ax2.set_ylabel('mean')
    ax2.set_xlabel('start_time: '+str(start_time)+'ns')
    
    ax3 = fig.add_subplot(313)
    ax3.plot(xData,std,'b',label="std")
    ax3.plot(xData,std,'r*')
    ax3.set_ylabel('std')
    ax3.set_xlabel('start_time: '+str(start_time)+'ns')
    plt.show()

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
    
def main():
    
    ###function start,set some parameter
    ###calculate time 
    start = time.time()
    stat_interval_time = 1E9 
    f_id =28489
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
    ###start time is the first time the function return minus 1E9
#    plotshow(frequency,mean,std,int(columns_R_time[0]/1E9)*1E9)
    ###location of the max frequency
    loc_max_frequency = frequency.index(max(frequency))
    print 'location of the max frequency:',loc_max_frequency
    ###the set of pid which result in the frequency exception
    pid_frequency_set = list(set(columns_pid[location[loc_max_frequency][0]:location[loc_max_frequency][1]]))
    print 'the set of pid:',pid_frequency_set
    
    ###location of the max mean 
    loc_max_mean = mean.index(max(mean))
    print 'location of the max mean:',loc_max_mean
    ###the set of pid which result in the mean exception
    pid_mean_set = list(set(columns_pid[location[loc_max_mean][0]:location[loc_max_mean][1]]))
    print 'the set of pid:',pid_mean_set
    
    ###location of the max std
    loc_max_std = std.index(max(std))
    print 'location of the max std:',loc_max_std
    ###the set of pid which result in the std exception
    pid_std_set = list(set(columns_pid[location[loc_max_std][0]:location[loc_max_std][1]]))
    print 'the set of pid:',pid_std_set
    
    ###print the time consuming
    end = time.time()
    print  'take %f s' %(end-start)
    
    ################################################################################################################
    ###find exception by pid set,time is limited in the exception time
#    restat_runtime=[[] for i in range(len(pid_frequency_set))]
#    pid_count=0
#    for pid in pid_frequency_set:
#        for i in range(location[loc_max_frequency][0],location[loc_max_frequency][1]):
#            if columns_pid[i]==pid:
#                restat_runtime[pid_count].append(columns_runtime[i])
#		print columns_dlist_id[i]
#	print 'frequency exception function  excute runtime of: '+str(pid)
#	print restat_runtime[pid_count]
#	print 'frequency exception function  mean and std of: '+str(pid)
#	print cal_mean_std(restat_runtime[pid_count])
#        pid_count+=1



    restat_runtime=[[] for i in range(len(pid_mean_set))]
    pid_count=0
    for pid in pid_mean_set:
        for i in range(location[loc_max_mean][0],location[loc_max_mean][1]):
            if columns_pid[i]==pid:
                restat_runtime[pid_count].append(columns_runtime[i])
		print columns_dlist_id[i]
	print 'mean exception function excute runtime of: '+str(pid)
	print restat_runtime[pid_count]
	print 'mean exception function mean and std of: '+str(pid)
	print cal_mean_std(restat_runtime[pid_count])
        pid_count+=1
        
#    restat_runtime=[[] for i in range(len(pid_std_set))]
#    pid_count=0
#    for pid in pid_std_set:
#        for i in range(location[loc_max_std][0],location[loc_max_std][1]):
#            if columns_pid[i]==pid:
#                restat_runtime[pid_count].append(columns_runtime[i])
#	print 'std exception function excute runtime of: '+str(pid)
##	print restat_runtime[pid_count]
#	print 'std exception function mean and std of: '+str(pid)
#	print cal_mean_std(restat_runtime[pid_count])
#        pid_count+=1

#################################################################################################################
### if you want to stat the exceptional function belong to the exceptional pid from the very beginning, you may use the code below
    
    ###when exception occured in frequency 
#    restat_result = restat_bypid(pid_frequency_set,columns_pid,columns_R_time,columns_C_time,columns_runtime)
#    pid_count = 0
#    for pid in pid_frequency_set:
#	plotshow(restat_result[pid_count][0],restat_result[pid_count][1],restat_result[pid_count][2],int(restat_result[pid_count][4]/1E9)*1E9)
#	pid_count+=1
#     
#    ###when exception occured in mean
#    restat_result = restat_bypid(pid_mean_set,columns_pid,columns_R_time,columns_C_time,columns_runtime)
#    pid_count = 0
#    for pid in pid_mean_set:
#        plotshow(restat_result[pid_count][0],restat_result[pid_count][1],restat_result[pid_count][2],int(restat_result[pid_count][4]/1E9)*1E9)
#        pid_count+=1
#    
#    ####when exception occured in std 
#    restat_result = restat_bypid(pid_std_set,columns_pid,columns_R_time,columns_C_time,columns_runtime)
#    pid_count = 0
#    for pid in pid_mean_set:
#        plotshow(restat_result[pid_count][0],restat_result[pid_count][1],restat_result[pid_count][2],int(restat_result[pid_count][4]/1E9)*1E9)
#        pid_count+=1

#################################################################################################################
###run main()
main()
