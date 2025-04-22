'''数据清洗'''
import os
import pandas as pd
from datetime import datetime, timedelta


def fill_missing_data_in_csv(directory="/path/to/your/directory"):
    """
    遍历目录下的所有频谱文件
    如果时间步中有缺失，则用前一行的数据来填充缺失行，并覆盖原文件。
    """
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)

            try:
                df = pd.read_csv(file_path, delimiter=',')

                if df.shape[1] >= 1:
                    # 将第一列转换为datetime类型
                    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format='%Y-%m-%d %H:%M:%S', errors='coerce')

                    start_date = df.iloc[0, 0]
                    end_date = df.iloc[-1, 0]

                    # 检查是否有缺失的时间步
                    date_range = pd.date_range(start=start_date, end=end_date, freq='1s')

                    if len(date_range) > len(df):
                        complete_df = pd.DataFrame(index=date_range)

                        df.set_index(df.iloc[:, 0], inplace=True)
                        df.drop(df.columns[0], axis=1, inplace=True)

                        complete_df = complete_df.join(df)
                        complete_df.ffill(inplace=True)

                        complete_df.reset_index(inplace=True)
                        complete_df.rename(columns={'index': df.columns[0]}, inplace=True)
                        complete_df.iloc[:, 0] = complete_df.iloc[:, 0].dt.strftime('%Y/%m/%d %H:%M:%S')

                        # 保存回原文件
                        complete_df.to_csv(file_path, index=False)
                        print(f"Processed {filename}: filled {len(date_range) - len(df)} missing rows")
                    else:
                        print(f"No missing data in {filename}")
                else:
                    print(f"File {filename} does not have enough columns")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")


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


if __name__=="__main__":
    fill_missing_data_in_csv("D:\iie\Python_Workspace\Time-Series-Library-main\数据集\电梯信号\\raw_data\\test_raw_data")