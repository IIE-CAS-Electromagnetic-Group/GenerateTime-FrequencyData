from fontTools.misc.plistlib import end_false

from methods.read_and_sample_method import *
from methods.convert_windows_and_linux_path import convert_paths
from methods.process_one_bin_file import generate_one_data_from_center_list, generate_one_data


def generate_trace_data_center(bin_file_dir = "G:/Work/Workspace/Data/原始数据/信息工程研究所/410_420MHz",
                               start_date = "2024-09-25 00:00",
                               stop_date = "2024-10-17 00:00",
                               center_freq_list=[416.086],
                               bandwidth=0.2,
                               resample_time = 1,
                               minute_of_picture = '1D',
                               prefix_path= "G:/Work/Workspace/Data/预处理数据"):
    '''
    按照频点中心生成迹线数据
    :param bin_file_dir:
    :param start_date:
    :param stop_date:
    :param center_freq_list:
    :param bandwidth:
    :param prefix_path:
    :return:
    '''
    # 从长时设备采集的原始bin文件中读取特点频段（根据中心频点进行选择），特点时间段内的数据，并进行频点下采样，采样时间下采样，目的是精简数据，便宜处理和观察
    # 参数bin_file_dir为存储bin文件的文件夹TraceRecord，一般其中含有子文件夹“2024-05-23，2024-05-24，....”
    # 频段选择select_start_freq ，select_stop_freq
    # 数据时间段选择日期 start_date ，stop_date
    # picture_num将指定频段，指定时间段内的数据分几部分存
    # minute_of_picture一个文件包括多长时间段的数据
    # resample_time在时间上进行下采样
    # resample_freq_num在频点上进行下采样，选取的频点列不超过该值


    bin_file_dir=convert_paths(bin_file_dir)

    picture_num = 1
    #minute_of_picture = '10T'
    #resample_time = 1


    file_massages = bin_file_dir.split("/")
    location = file_massages[-2]

    other_message=''
    for center_freq in center_freq_list:
        other_message=other_message+str(center_freq)+"_"
    other_message =other_message+str(bandwidth)
    output_dir = os.path.join(prefix_path, location,other_message +"MHz原始信号数据")
    output_dir = convert_paths(output_dir)


    date_list = produce_date_intervals(bin_file_dir, start_date, stop_date, minute_of_picture)


    for (intervals_start_date, intervals_stop_date) in date_list:

        print(f"generrating the picture of frequency between , date from {intervals_start_date} to {intervals_stop_date}")

        generate_one_data_from_center_list(bin_file_dir, center_freq_list, bandwidth, intervals_start_date,
                                           intervals_stop_date, resample_time, output_dir)

    pass

def generate_trace_data(bin_file_dir = "G:/Work/Workspace/Data/原始数据/信息工程研究所/0_30MHz",
                        select_start_freq = 0,
                        select_stop_freq = 10,
                        start_date = "2024-07-05 00:00",
                        stop_date = "2024-07-06 00:00",
                        picture_num = 1,
                        minute_of_picture = '6H',
                        resample_time = 1,
                        resample_freq_num=1000,
                        prefix_path="E:/预处理2"
                        ):
    # 从长时设备采集的原始bin文件中读取特点频段，特点时间段内的数据，并进行频点下采样，采样时间下采样，目的是精简数据，便宜处理和观察
    # 参数bin_file_dir为存储bin文件的文件夹TraceRecord，一般其中含有子文件夹“2024-05-23，2024-05-24，....”
    # 频段选择select_start_freq ，select_stop_freq
    # 数据时间段选择日期 start_date ，stop_date
    # picture_num将指定频段，指定时间段内的数据分几部分存
    # minute_of_picture一个文件包括多长时间段的数据
    # resample_time在时间上进行下采样
    # resample_freq_num在频点上进行下采样，选取的频点列数不超过该值

    # bin_file_dir = "G:/Work/Workspace/Data/原始数据/信息工程研究所/125_135MHz"
    # bin_file_dir = "G:/Work/Workspace/Data/原始数据/信息工程研究所/2400_2500MHz"
    # bin_file_dir = "F:/频谱迹线采集/410_420MHz"
    #bin_file_dir = "G:/Work/Workspace/Data/原始数据/信息工程研究所/0_30MHz"
    # bin_file_dir = "G:/Work/Workspace/Data/原始数据/信息工程研究所/410_420MHz"

    #bin_file_dir = "D:/iie/Data/原始数据/信息工程研究所/0_30MHz"
    #bin_file_dir="E:/葛洲坝/TraceRecord"


    bin_file_dir=convert_paths(bin_file_dir)

    #select_start_freq = 0
    #select_stop_freq = 10

    #start_date = "2024-07-05 00:00"
    #stop_date = "2024-07-06 00:00"
    # point_num_of_picture = 50000

    #picture_num = 1
    #minute_of_picture = '6H'
    # minute_of_picture = '30T'
    #resample_time = 1
    #resample_freq_num=1000

    file_massages = bin_file_dir.split("/")
    location = file_massages[-2]
    print("file_massages:"+str(file_massages))

    #prefix_path= "G:/Work/Workspace/Data/预处理数据"
    #prefix_path="E:/预处理2"
    output_dir = os.path.join(prefix_path, location,str(select_start_freq)+"_"+str(select_stop_freq)+"MHz原始信号数据")
    output_dir = convert_paths(output_dir)

    # 生成日期区间和频率区间列表
    date_list = produce_date_intervals(bin_file_dir, start_date, stop_date, minute_of_picture,select_start_freq,select_stop_freq)
    intervals_list = produce_freq_intervals_with_picturenum(bin_file_dir, select_start_freq, select_stop_freq, picture_num)
    print("日期区间:"+str(date_list))
    print("频率区间:"+str(intervals_list))

    # 遍历日期和频率区间，生成数据
    print("遍历日期和频率区间，生成数据")

    for (intervals_start_date, intervals_stop_date) in date_list:
        print("intervals_start_date:"+str(intervals_start_date))
        print("intervals_stop_date:"+str(intervals_stop_date))
        for (intervals_start_freq, intervals_stop_freq) in intervals_list:
            print("--intervals_start_freq:"+str(intervals_start_freq))
            print("--intervals_stop_freq:"+str(intervals_stop_freq))
            print(f"generrating the picture of frequency between {intervals_start_freq} and {intervals_stop_freq} , date from {intervals_start_date} to {intervals_stop_date}")
            print("*bin_file_dir:"+str(bin_file_dir))
            generate_one_data(bin_file_dir, intervals_start_freq, intervals_stop_freq, intervals_start_date,
                                 intervals_stop_date, resample_time,resample_freq_num,output_dir)
    pass



if __name__ == "__main__":

    '''generate_trace_data_center(bin_file_dir = "E:/111/TraceRecord",
                               start_date = "2024-03-10 00:00",
                               stop_date = "2024-03-15 00:00",
                               center_freq_list=[7.5],
                               bandwidth=0.1,
                               prefix_path= "E:/20250310迹线预处理")'''
    generate_trace_data(bin_file_dir="D:/iie/Data/原始数据/信息工程研究所/0_30MHz",
                        select_start_freq=0.5,
                        select_stop_freq=4,
                        start_date="2024-09-26 00:00",
                        stop_date="2024-10-16 00:00",
                        picture_num=1,
                        minute_of_picture='10T',
                        resample_time=1,
                        resample_freq_num=100,
                        prefix_path="D:/信工所电梯0.5-4"
                        )
