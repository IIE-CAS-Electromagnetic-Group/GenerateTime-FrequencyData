import json
import numpy as np
from scipy import signal
import os
from pathlib import Path
import math

def sigmf_to_csv(meta_path, data_path, csv_path,
                 num_freq_bins=None, time_step=None,
                 nfft=None, noverlap=None,
                 max_rows_per_file=2000, max_files=999,
                 target_time_samples=1000,
                 min_time_step=None):
    """
    将 单个的SigMF meta 和 data 文件转换为频谱格式并保存为 CSV，
    并在行数过多时拆分为多个文件。

    meta_path: SigMF metadata (.sigmf-meta) 文件路径
    data_path: SigMF raw data (.sigmf-data) 文件路径
    csv_path: 输出 CSV 文件路径（不带索引后缀）
    num_freq_bins: 指定生成的频率采样点数量（nfft=2*(num_freq_bins-1)）
    time_step: 指定生成的时间步长（秒）
    nfft: FFT 点数（如果未指定 num_freq_bins，传入此参数）
    noverlap: 相邻窗口重叠点数（如果未指定 time_step，传入此参数）
    max_rows_per_file: 每个 CSV 最多包含的时间行数，超出则截断成下一个文件
    max_files: 每个SigMF-data文件最多生成的 CSV 文件数

    target_time_samples: 目标时间采样点数（自动计算参数时的参考值）
    min_time_step=None:最小时间步长（秒），防止时间步长过小


    关于默认设置：有的时候我们可能不知道要把time_step设置为多少，
    比如有些sigmf数据仅仅包含了几秒的时间，所以需要把time_step设得比较小，
    有的sigmf数据可能跨度几小时，所以需要让time_step=1(秒)甚至几秒，
    但是不可能一个一个指定这个数据集里的每个文件的time_step和num_freq_bins

    这个时候就把time_step和noverlap都设为None，传入target_time_samples参数
    target_time_samples 参数的作用是帮助函数自动计算一个合适的时间步长 (time_step)
    默认设置为 1000，函数会尝试让生成的频谱数据时间轴上有大约 1000 个采样点。
    但这也带来了一个新的问题：
    当 target_time_samples 设置得过大时，对于较短的数据（例如几秒钟），会导致计算出的时间步长（time_step）过小，
    从而生成的频谱数据时间轴采样点过于密集。这可能会导致生成的 CSV 文件过于细长，包含大量行，
    比如较短的数据只有几秒钟，一般认为0.001s的时间步就比较合适了，
    但是我把target_time_samples设置成了10000000,导致这个几秒的数据生成的时间步也过于小了
    因此这里还要再设置min_time_step，在计算时间步长时增加一个最小时间步长限制，以防止生成过于密集的时间采样点。

    输出文件：
    如果 csv_path 为 "A.csv"：
      输出A_0.csv, A_1.csv, ...
    """
    # 读取 metadata
    meta_path = Path(meta_path)
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    sample_rate = meta['global']['core:sample_rate']
    datatype = meta['global']['core:datatype']
    center_freq = meta['captures'][0]['core:frequency']

    # 确定 FFT 点数
    if num_freq_bins is not None:
        nfft = 2 * (num_freq_bins - 1)
    if nfft is None:
        raise ValueError("必须指定 num_freq_bins 或 nfft")

    # 如果 time_step 和 noverlap 均未指定，自动计算
    if time_step is None and noverlap is None:
        # 读取原始 I/Q 数据计算总时长
        raw = np.fromfile(data_path, dtype=np.int16)
        total_samples = len(raw) // 2  # 每个样本占 2 个字节（I 和 Q）
        total_duration = total_samples / sample_rate

        # 计算期望的总时间步数
        target_total_steps = min(target_time_samples, max_files * max_rows_per_file)
        time_step = total_duration / target_total_steps

        # 限制最大时间步长
        if min_time_step is not None:
            time_step = max(time_step, min_time_step)
        print(f"自动计算 time_step: {time_step:.6f} s")

    # 确定重叠或时间步长
    if time_step is not None:
        hop = int(round(time_step * sample_rate))
        if hop <= 0:
            raise ValueError("time_step 太小，hop 转换后为 0")
        noverlap = nfft - hop
    elif noverlap is None:
        noverlap = nfft // 2
    hop = nfft - noverlap

    # 打印时间步长信息
    min_time_step = hop / sample_rate
    print(f"Minimal time step (实际步长): {min_time_step:.6f} s，采样参数：nfft={nfft}, noverlap={noverlap}")
    if time_step is not None:
        print(f"Requested time_step: {time_step} s")
    print(f"Frequency bins: {num_freq_bins or int(nfft/2+1)}")

    # 读取原始 I/Q 数据
    raw = np.fromfile(data_path, dtype=np.int16)

    # 确保数据长度是偶数
    if len(raw) % 2 != 0:
        raw = raw[:-1]  # 如果长度不是偶数，截断最后一个元素

    i = raw[0::2].astype(np.float32)
    q = raw[1::2].astype(np.float32)
    iq = i + 1j * q

    # STFT 计算瀑布图
    freqs, times, Sxx = signal.spectrogram(
        iq,
        fs=sample_rate,
        nperseg=nfft,
        noverlap=noverlap,
        mode='complex'
    )

    # 计算功率谱 (dBFS)
    power = 10 * np.log10(np.abs(Sxx)**2 + 1e-12)

    # 频率轴（中心频率 + 偏移）
    freq_axis = center_freq + freqs

    # 准备输出路径与基础文件名
    csv_path = Path(csv_path)
    output_dir = csv_path.parent
    base_name = csv_path.stem


    # 限制总行数与拆分
    total_rows = len(times)
    max_total_rows = max_rows_per_file * max_files
    rows_to_write = min(total_rows, max_total_rows)
    num_files = math.ceil(rows_to_write / max_rows_per_file)

    header = 'time(s),' + ','.join(f"{f:.0f}" for f in freq_axis)

    for idx in range(num_files):
        start = idx * max_rows_per_file
        end = min(start + max_rows_per_file, rows_to_write)
        out_file = output_dir / f"{base_name}_{idx}.csv"
        with open(out_file, 'w') as out:
            out.write(header + '\n')
            for ti, row in zip(times[start:end], power[:, start:end].T):
                line = f"{ti:.6f}," + ','.join(f"{p:.3f}" for p in row)
                out.write(line + '\n')
        print(f"Saved CSV part {idx+1}/{num_files}: {out_file} (rows {start} to {end-1})")


def batch_processing_sigmf_to_csv(root_dir, output_dir,
                                  num_freq_bins=None, time_step=None,
                                  nfft=None, noverlap=None,
                                  max_rows_per_file=2000, max_files=5,
                                  target_time_samples=None,
                                  min_time_step=None):
    """
    批量处理指定目录下的 .sigmf-data 和对应的 .sigmf-meta 文件，转换为拆分后的 CSV。

    root_dir: 输入的根目录，遍历根目录下及所有子目录的.sigmf-data 和 .sigmf-meta 文件
    output_dir: 输出的根目录，转换后的 CSV 文件将保存在此目录下，保持原有的目录结构
    num_freq_bins: 指定生成的频率采样点数量（nfft=2*(num_freq_bins-1)）
    time_step: 指定生成的时间步长（秒）
    nfft: FFT 点数（如果未指定 num_freq_bins，可传入此参数）
    noverlap: 相邻窗口重叠点数（可与 time_step 二选一）
    max_rows_per_file: 每个 CSV 最多包含的时间行数
    max_files: 最多生成的 CSV 文件数
    """
    root_dir = Path(root_dir)
    output_dir = Path(output_dir)

    for dirpath, _, filenames in os.walk(root_dir):
        dirpath = Path(dirpath)
        for filename in filenames:
            if filename.endswith('.sigmf-data'):
                data_path = dirpath / filename
                meta_path = dirpath / (filename.replace('.sigmf-data', '.sigmf-meta'))
                if not meta_path.exists():
                    print(f"对应的 meta 文件不存在: {meta_path}")
                    continue

                # 构造输出基础路径，保持目录结构
                relative = data_path.relative_to(root_dir)
                out_base = (output_dir / relative).with_suffix('.csv')
                out_base.parent.mkdir(parents=True, exist_ok=True)

                # 调用转换函数
                sigmf_to_csv(meta_path, data_path, out_base,
                             num_freq_bins=num_freq_bins,
                             time_step=time_step,
                             nfft=nfft,
                             noverlap=noverlap,
                             max_rows_per_file=max_rows_per_file,
                             max_files=max_files,
                             target_time_samples=target_time_samples,
                             min_time_step=min_time_step)

if __name__ == "__main__":
    batch_processing_sigmf_to_csv(
        root_dir="E:\\电磁频谱数据集",
        output_dir="E:\\电磁PSD数据集1",
        num_freq_bins=800,
        #time_step=None,
        max_rows_per_file=10000,
        target_time_samples=50000,
        min_time_step=0.000001
    )
