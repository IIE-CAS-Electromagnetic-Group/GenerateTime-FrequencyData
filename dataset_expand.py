'''原来的数据集太少了，这里需要复制增加一下'''
from datetime import datetime
from time import strftime

import pandas as pd
from datetime import timedelta
from pandas import DataFrame, to_datetime
import os
from data_clean import fill_missing_data_in_csv

def merge_all_csvfile_from_a_dir(dir_path):
    '''读取指定目录下的所有.csv原始文件，并合并为一个巨大的df'''
    df_total=DataFrame()
    for file in os.listdir(dir_path):
        if file.endswith(".csv"):
            print("Reading "+file)
            df_tmp=pd.read_csv(os.path.join(dir_path,file))
            df_total=pd.concat([df_total, df_tmp], ignore_index=True)
    #print(df)
    return df_total



'''df=merge_all_csvfile_from_a_dir("D:\iie\Python_Workspace\Time-Series-Library-main\数据集\葛洲坝\\raw_data\\test_raw_data")
print(df)
df['date'] = df['date'].str.replace('/', '-', regex=False)
df['date'] = pd.to_datetime(df['date'])
# 将 datetime 对象格式化为指定的字符串格式
df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
print(df)



df.to_csv("0.csv",index=False)
print(df)'''
df=pd.read_csv("0.csv")
df['date'] = pd.to_datetime(df['date'])

for i in range(1,20):
    # 初始化一个空列表来存储行数据
    data_list = []
    for index,row in df.iterrows():
        # 将每一行数据添加到列表中
        row[0]=row[0]+timedelta(days=i)
        row[0]=row[0].strftime("%Y-%m-%d %H:%M:%S")
        data_list.append(row)
    df_new = pd.DataFrame(data_list, columns=df.columns)
    filename_starttime=pd.to_datetime(df_new.iloc[0,0]).strftime("%Y%m%d%H%M%S")
    filename_endtime=pd.to_datetime(df_new.iloc[-1,0]).strftime("%Y%m%d%H%M%S")
    df_new.to_csv(f"{filename_starttime}_{filename_endtime}.csv",index=False)
