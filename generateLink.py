def generate_url(dlist_id):
    url = 'http://os.cs.tsinghua.edu.cn:280/lxr/systrace-perl?v=linux-3.5.4&amp;\
f=&amp;a=x86_32&amp;path0=' + str(dlist_id-250)+'&amp;path1='+str(dlist_id+250)
    return url
#####
def generateLink(svg_name,dlistid_set_per_second):
    txtpath=r"link.xml"
    fp=open(txtpath)
    i=0;
    line=["","","","","","",""]
    for lines in fp.readlines():
        line[i]=lines
        i=i+1
    fp.close()
    js_fp= open("click.js",'r')
    js_lines=js_fp.readlines()
    
    fp=open(svg_name+'.svg','r')
    newfp = open('result_'+svg_name+'.svg','wt')
    list_of_all_the_lines = fp.readlines()
    tag = 1###is not <use>
    id_index = 0
    lines_write=[]
    for row in list_of_all_the_lines:
        if tag==1:
            if '<use' in row:
    	    	tag=0
            else:
     	    	newfp.write(row)
    	        if '<svg' in row:
    		    newfp.writelines(js_lines)
        if tag==0:
            if '<use' not in row:
    	    	tag=2
    	    	newfp.writelines(lines_write)
    	    	newfp.write(row)
    	    else:
    	        x_index= row.find('x=')
    	        for i in range(x_index+3,x_index+20):  ###max length of position x is less than 20
    		    if row[i]=='"':
    		        pos_x = row[x_index+3:i]
    		        break
    	        y_index= row.find('y=')
    	    	for i in range(y_index+3,y_index+20):  ###max length of position x is less than 20
    		    if row[i]=='"':
    		    	pos_y = row[y_index+3:i]
    		    	break
    	    	#x=float(pos_x)+20
		x=float(pos_x)
    	    	y=float(pos_y)
    #######################
	    	dlistid_num_per_pid = len(dlistid_set_per_second[id_index])
		###find the pid set which belongs to the same time(1s)
		if dlistid_num_per_pid:
		    pid_list = []
	    	    for i in range(0,dlistid_num_per_pid):
		        if dlistid_set_per_second[id_index][i][1] not in pid_list:
			    pid_list.append(dlistid_set_per_second[id_index][i][1])
		
		    len_pid_list = len(pid_list)
		##### we need to calculate postion of the list,for solve the screeen overflow
		    num_in_pid_list = [0 for i in range(0,len_pid_list)]
			
		    for i in range(0,dlistid_num_per_pid):
			temp_index = pid_list.index(dlistid_set_per_second[id_index][i][1])
			num_in_pid_list[temp_index] = num_in_pid_list[temp_index] + 1
		    
		    y0 = y
		    x0 = x + 10				
		    xn = 1220###accurate value is 1228
		    yn = 640###accurate value is 648
		    m = len_pid_list
		    n = max(num_in_pid_list)
		    n_max = int(yn/14)
		    if n > yn/14:
			y = 0
			### set the max number of dlist is int(yn/14)
		    else:
			if n >(yn-y)/14-1:
			    y = yn-14*(n+1)
		    if m<=(xn-x-10)/60:
			x = x+10
		    else:
			x = (x-60*m-10)
		########################################################
			
    	    	    line0 = line[0].replace('@id',str(id_index))
    	    	    lines_write.append(line0)
		    for i in range(0,len_pid_list):
    	    	        line1 = line[1].replace('@x',str(x+(i*60)))
    	    	        line1 = line1.replace('@color','#EFE9CE')
    	    	        line1 = line1.replace('@y',str(y))
    	    	        lines_write.append(line1)
    	    	        line2 = line[2].replace('@x',str(x+(i*60)))
    	    	        line2 = line2.replace('@y',str(y+10))
	    	        line2 = line2.replace('@pid',pid_list[i])
		        line2 = line2.replace('<a xlink:show="new" xlink:href="@href">','')
		        line2 = line2.replace('</a>','')
    	    	        lines_write.append(line2)
			j_count=0
	    	    	for j in range(0,dlistid_num_per_pid):
			    if dlistid_set_per_second[id_index][j][1]==pid_list[i]:
    	                        line3=line[1].replace('@x',str(x+(i*60)))
    	                        line3=line3.replace('@color','#AAD5EF')
    	                        line3 = line3.replace('@y',str(y+(j_count+1)*14))
    	                        lines_write.append(line3)
    	                        line4 =line[2].replace('@x',str(x+(i*60)))
    	                        line4 = line4.replace('@y',str(y+(j_count+2)*14-4))
    	                        line4 = line4.replace('@pid',str(dlistid_set_per_second[id_index][j][0]))
			        line4 = line4.replace('@href',generate_url(dlistid_set_per_second[id_index][j][0]));
    	                        lines_write.append(line4)
				j_count = j_count+1 
				if j_count >=n_max:### there are too many function call to display on the screen,we just display n_max
				    break;
    	            lines_write.append(line[3])
    ######################
    	            temp = line[4].replace('@id1',str(id_index)+'g')###d is stand for the blue dot ,which will become green when we click it	
    	            newfp.write(line[4].replace('@id2',str(id_index)))
    	            temp = line[5].replace('@id',str(id_index)+'t')
    	            temp = temp.replace('@x',str(x0-14))
    	            newfp.write(temp.replace('@y',str(y0+2)))
    	            newfp.write(line[6])

    	        id_index=id_index+1
    	    continue;
        if tag==2:
    	    newfp.write(row)
    fp.close()
    newfp.close()
    
