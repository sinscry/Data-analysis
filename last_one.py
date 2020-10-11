import pandas as pd
import os
import sys
import math
from matplotlib import pyplot as plt

'''
对数据分天处理分品牌处理
'''



# 归一化程序
def Normalization(data):
    return (data-data.min())/(data.max()-data.min())



# 按时间做平均处理
def attribute_follow_lvl(attribute):
    global exp_data,con_data,shift_hour
    exp_avg = con_avg = [0,0,0,0]
    exp_c = con_c =  [0,0,0,0]
    # 以 4334做平均,根据小时算
    for hour in range(9,23+shift_hour):
        if hour<13+shift_hour:
            q=0
        elif hour<16+shift_hour:
            q=1
        elif hour<19+shift_hour:
            q=2
        else:
            q=3

        # 实验组
        if len(exp_data.loc[exp_data.hour==hour, attribute]):
            exp_avg[q]=exp_avg[q]+float(exp_data.loc[exp_data.hour==hour,attribute])
            exp_c[q]=exp_c[q]+1

        # 对照组
        if len(con_data.loc[con_data.hour==hour, attribute]):
            con_avg[q]=con_avg[q]+float(con_data.loc[con_data.hour==hour,attribute])
            con_c[q]=con_c[q]+1

        
    # 平均值反赋值给对应的数
    for hour in range(9,23+shift_hour):
        if hour<13+shift_hour:
            q=0
        elif hour<16+shift_hour:
            q=1
        elif hour<19+shift_hour:
            q=2
        else:
            q=3
        # 实验组
        if len(exp_data.loc[exp_data.hour==hour,attribute]):
            exp_data.loc[exp_data.hour==hour,attribute]=exp_avg[q]/exp_c[q]
        # 对照组
        if len(con_data.loc[con_data.hour==hour,attribute]):
            con_data.loc[con_data.hour==hour,attribute]=con_avg[q]/con_c[q]


# 画图设定
def save_plot(brand_name,day,exp_data,con_data,attributes):
    plt.figure(figsize=(10,10), dpi=100)
    # 共有4对
    ax=[[] for i in range(2*len(attributes))] # 共8张图，每张图有两个数据

    for i in range(len(ax)):
        if i%2==0:
            group='实验组'
            lvl=Normalization(exp_data['lvl'])
            tmp_data=exp_data
        else:
            group='对照组'
            lvl=Normalization(con_data['lvl'])
            tmp_data=con_data

        ax[i].append(plt.subplot(421+i))
        ax[i][0].plot(lvl)
        ax[i][0].legend(["lvl"],loc=2)
        x = range(0,len(tmp_data),1)
        plt.xticks(x, tmp_data['hour'])
        ax[i][0].set_xlabel(r"hour")
        plt.yticks(lvl,tmp_data['lvl'])
        ax[i][0].set_ylabel(r"lvl")
        ax[i][0].grid()
        

        # ax[i].append(ax[i][0].twin())

        # plt.title(brand_name+group+str(421+i))
        




    plt.subplots_adjust(wspace =0.1, hspace =1)#调整子图间距
    plt.show()
    sys.exit(0)


def Mission(day,brand_name):
    global exp_data,con_data,ax

    # print(day,brand_name)
    # 实验组原始数据
    exp_origin_data=df[(df.brand_store_name==brand_name)&(df.dt==day)&(df.result_user_tag=='实验组')]
    # 对照组原始数据
    con_origin_data=df[(df.brand_store_name==brand_name)&(df.dt==day)&(df.result_user_tag=='对照组')]

    # 按照小时排序并重标索引号
    exp_data=exp_origin_data.sort_values(['hour'],ascending=True).reset_index(drop=True)
    exp_data['lvl']=exp_data['lvl'].shift(shift_hour)  # 做等级平移处理
    exp_data=exp_data[(exp_data.lvl!='(NULL)')&(pd.isnull(exp_data.lvl)!=True)].reset_index(drop=True) # 去除等级为空的数
    
    con_data=con_origin_data.sort_values(['hour'],ascending=True).reset_index(drop=True)
    con_data['lvl']=con_data['lvl'].shift(shift_hour)  # 做等级平移处理
    con_data=con_data[(con_data.lvl!='(NULL)')&(pd.isnull(con_data.lvl)!=True)].reset_index(drop=True) # 去除等级为空的数
    
    # 品牌在档期流uv/部类档期流uv,  品牌在档期流uv/档期流uv(APP),  部类里的排序,  实验品牌里的排序
    attributes=['dangqiliu_bulei_ratio','dangqiliu_app_ratio','all_rank','test_rank']
    for att in attributes:
        attribute_follow_lvl(att)  # 对相关属性按时间进行平均
    save_plot(brand_name,day,exp_data,con_data,attributes)






    

# 前期设置数据
def Setting():
    global df,dt,brand_name_list,corrs,shift_hour
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei'] # 让matplotlib中文显示不出错
    shift_hour = 0 # 对等级延后小时设置
    df = pd.read_excel('0813.xlsx',sheet_name='Sheet1')  # 设定调用excel文件名和sheet
    # print(df.head()) # 观测数据前5行
    dt = list(df['dt'].astype('int').unique()) # 获取数据的天数，用标签列属性获取
    dt.sort()  # 对日期进行排序
    brand_name_list = df['brand_store_name'].unique() # 获取品牌数目
    corrs = ['-1_-0.6','-0.6_0','0_0.6','0.6_1'] # 相关系数文件夹名



def main():
    # 调用设定函数进行数据设定
    Setting()
    # 注意通过更改dt能限制判断的天数,如dt=[20200809,20200810]
    for day in dt:
        # 按天创建文件夹,相关系数
        try:
            os.mkdir(str(day))
        except:
            pass
        for corr in corrs:
            try:    
                os.mkdir('./'+str(day)+'/'+corr)
            except:
                pass
        for brand_name in brand_name_list:
            Mission(day,brand_name)
            # sys.exit(0) 


if __name__ == '__main__':
    # 启动主函数
    main() 