'''目的还是为了便捷地看一下某些.csv频谱到底长啥样'''
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt

def plot_trace_heatmap(csv_file_path, html_save_path="default.html"):
    """
    从CSV文件读取数据并绘制热图。

    csv_file_path (str): CSV文件的路径。
    html_save_path (str): 生成的HTML文件的保存路径。
    """
    # 读取CSV文件
    df = pd.read_csv(csv_file_path)

    # 获取频率（x轴），即第一行的列名（除了第一列时间）
    frequencies = df.columns[1:].astype(str).tolist()

    # 获取时间（y轴），即第一列的数据
    times = df.iloc[:, 0].astype(str).tolist()

    # 获取能量值（z轴），即除去第一列后的数据矩阵
    z_values = df.iloc[:, 1:].values

    # 创建热图
    heatmap = go.Heatmap(
        z=z_values,
        x=frequencies,
        y=times,
        colorscale='jet',
        showscale=True,
        hoverongaps=True,
        hoverinfo='z'
    )

    # 创建布局，隐藏坐标轴，并使图表填满整个画布
    layout = go.Layout(
        xaxis=dict(
            title='频率',
            nticks=20,
            showgrid=False,
            zeroline=False,
            visible=True
        ),
        yaxis=dict(
            title='时间',
            showgrid=False,
            zeroline=False,
            visible=True,
            autorange='reversed'
        ),
        margin=dict(l=50, r=50, t=50, b=50),
        autosize=True
    )

    # 创建图表
    fig = go.Figure(data=[heatmap], layout=layout)

    fig.show()
    # 保存为HTML文件
    '''fig.write_html(html_save_path)

    print(f"热图已保存到: {html_save_path}")'''
    return fig




if __name__=="__main__":
    print("start")
    #plot_trace_heatmap(csv_file_path="D:/0-30MHz电梯/信息工程研究所/0_30MHz原始信号数据/20240925111821_20240925171821_0.009_30.0.csv")
    fig=plot_trace_heatmap(csv_file_path="E:\\24L01预处理\\2485_2495MHz原始信号数据\\20250328151803_20250328152303_2485.0_2495.0.csv")
    fig.write_html("24L01.html")