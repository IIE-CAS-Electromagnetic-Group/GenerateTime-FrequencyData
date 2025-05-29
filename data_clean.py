'''数据清洗'''
import os
import pandas as pd
from datetime import datetime, timedelta

from bokeh.core.property.datetime import TimeDelta
from sympy.physics.units import minutes


def fill_missing_data_in_csv(directory="/path/to/your/directory",min_time_minutes=None):
    """
    遍历目录下的所有频谱文件。
    如果时间步中有缺失，则用前一行的数据来填充缺失行，并覆盖原文件。
    """
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)

            # 读取CSV文件时明确指定列名
            df = pd.read_csv(file_path, delimiter=',')

            if df.shape[1] >= 1:
                # 保存原始列名
                original_col_name = df.columns[0]

                # 将第一列转换为datetime类型
                df[original_col_name] = pd.to_datetime(df[original_col_name])
                print(df[original_col_name])
                start_date = df.iloc[0][original_col_name]
                end_date = df.iloc[-1][original_col_name]

                if not min_time_minutes==None:
                    end_date=(start_date+timedelta(minutes=min_time_minutes)).strftime('%Y-%m-%d %H:%M:%S')


                # 检查是否有缺失的时间步
                date_range = pd.date_range(start=start_date, end=end_date, freq='1s')

                complete_df = pd.DataFrame(index=date_range)

                # 设置索引并保留列名
                df.set_index(original_col_name, inplace=True)

                complete_df = complete_df.join(df)
                complete_df.ffill(inplace=True)

                # 重置索引并恢复原始列名
                complete_df.reset_index(inplace=True)
                complete_df.rename(columns={'index': original_col_name}, inplace=True)

                # 格式化日期列
                complete_df[original_col_name] = complete_df[original_col_name].dt.strftime('%Y/%m/%d %H:%M:%S')

                # 保存回原文件
                complete_df.to_csv(file_path, index=False)
                print(f"Processed {filename}: filled {len(date_range) - len(df)} missing rows")
            else:
                print(f"File {filename} does not have enough columns")



def check_time_order_in_csv(directory):
    '''检查csv里的时间顺序是否出现奇奇怪怪的乱序'''
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)

            try:
                df = pd.read_csv(file_path, delimiter=',')
                if df.shape[1] >= 1:
                    # 将第一列转换为datetime类型
                    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format='%Y-%m-%d %H:%M:%S', errors='coerce')

                    # 检查时间是否严格递增
                    if not df.iloc[:, 0].is_monotonic_increasing:
                        print(f"警告: {filename} 中的时间列不是严格递增的")
                else:
                    print(f"文件 {filename} 没有足够的列来检查时间顺序")
            except Exception as e:
                print(f"处理 {filename} 时出错: {str(e)}")


def del_short_signal_record(csv_file):
    df=pd.read_csv(csv_file)
    df["start_time"]=pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])
    mask = df["start_time"] != df["end_time"]
    df=df[mask]
    df.to_csv(csv_file,index=False)


if __name__=="__main__":
    fill_missing_data_in_csv("D:\信工所电梯0.5-4\\0.5_4MHz原始信号")
    #del_short_signal_record("D:\iie\Python_Workspace\Time-Series-Library-main\数据集\葛洲坝\\raw_data\signal_record_and_feature\\train_signal_record_and_feature.csv")
    #fill_missing_data_in_csv(".")