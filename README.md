#dcg-analyser

### 功能

在lxr平台上集成函数频度分析图，步骤：

1. 用户在lxr页面上填入平台、内核版本、时间范围、函数名等参数
2. 提交请求后，后台根据函数名查找函数定义的表FLIST，得到指定函数的id
3. 根据该id查询动态函数调用数据库FDLIST，并对该时间内的函数以指定时间段进行统计频度
4. 利用matploitlib绘制svg图
5. 在svg图上添加处理的函数，以便于点击网页上的图上点时，可以有相应的响应操作
6. 将svg图嵌入到网页中展示

### 细节

* statistics.py,generateLink.py由python编写
* dcgAnalyser由perl脚本编写
* statistics.py函数的执行入口为main函数，在main函数里面可以进行相关参数的设置，例如函数id，统计时间间

