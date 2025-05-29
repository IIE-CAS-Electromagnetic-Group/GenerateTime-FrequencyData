from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from pathlib import Path
import os
import numpy as np

def plot_greyscale_for_singledf(df,image_name='gray_image_default.png'):
    '''
    为一个单独的csv频谱数据绘制灰度图
    '''
    print("绘制灰度图......")
    width = df.shape[1]#列数对应图片的宽
    height = df.shape[0]#行数对应图片的高
    print("width:"+str(width))
    print("height:" + str(height))

    #确定底噪
    all_values=df.values.flatten()
    background_noise=pd.Series(all_values).median()

    signal_max=pd.Series(all_values).max()

    powerwidth=signal_max-background_noise

    '''# 设置每个像素的颜色，这里以一个简单的渐变为例
    for i in range(width):
        for j in range(height):
            # 计算灰度值
            if(df.iloc[j,i]<background_noise):
                df.iloc[j, i]=background_noise
            gray_value = int(((df.iloc[j,i]-background_noise)/powerwidth) * 255)
            # 设置像素的RGB值，灰度图所以R=G=B
            pixels[i, j] = (gray_value, gray_value, gray_value)


    # 保存图片
    img.save(image_name)
    print('图片已保存为:'+str(image_name))
    return img  # 返回img,画gif图用的'''

    # 使用 Pandas 的向量化操作来设置底噪
    df_clipped = df.clip(lower=background_noise,upper=signal_max)

    # 计算灰度值并转换为 8 位整数
    gray_values = ((df_clipped - background_noise) / powerwidth * 255).astype(np.uint8)

    # 将 DataFrame 转换为 NumPy 数组
    gray_array = gray_values.values

    # 转换为图像
    img = Image.fromarray(gray_array, 'L')  # 'L' 表示灰度图

    # 保存图片
    img.save(image_name)
    print(f'图片已保存为: {image_name}')
    return img


def background_noise_normalization(df):
    '''噪底归一化'''
    # 确定底噪
    all_values = df.values.flatten()
    background_noise = pd.Series(all_values).median()
    df=df.clip(lower=background_noise)
    return df



def plot_greyscale_for_singledf_with_anthor(df,anchors_list,image_name='gray_image_anchor.png',saveimg=True):
    '''
    为一个单独的csv频谱数据绘制灰度图
    同时也会把锚框绘制上去
    '''
    print("绘制锚框灰度图......")
    width = df.shape[1]#列数对应图片的宽
    height = df.shape[0]#行数对应图片的高
    print("width:"+str(width))
    print("height:" + str(height))
    img = Image.new('RGB', (width, height), color='black')
    pixels = img.load()  # 创建像素映射


    #确定底噪
    all_values=df.values.flatten()
    background_noise=pd.Series(all_values).median()


    signal_max = df.values.max()


    powerwidth=signal_max-background_noise
    df=background_noise_normalization(df)
    # 设置每个像素的颜色，这里以一个简单的渐变为例
    for i in range(width):
        for j in range(height):
            # 计算灰度值
            '''if(df.iloc[j,i]<background_noise):
                df.iloc[j, i]=background_noise'''
            gray_value = int(((df.iloc[j,i]-background_noise)/powerwidth) * 255)
            # 设置像素的RGB值，灰度图所以R=G=B
            pixels[i, j] = (gray_value, gray_value, gray_value)
    for anthor in anchors_list:
        anthor=list(map(int, anthor))
        if anthor[2]>anthor[0] or anthor[2]>df.shape[1]-anthor[0]:
            print("anchor width illegal")
        if anthor[3]>anthor[1] or anthor[3]>df.shape[0]-anthor[1]:
            print("anchor height illegal")
        '''w=min(anthor[2],anthor[0],df.shape[1]-anthor[0])
        h=min(anthor[3], anthor[1], df.shape[0] - anthor[1])
        anthor=[anthor[0],anthor[1],w,h]
        print("anthor_box:"+str(anthor))'''
        for i in range(anthor[2]):
            pixels[anthor[0]-int(anthor[2]/2)+i,anthor[1]-int(anthor[3]/2)]=(255,0,0)
            pixels[anthor[0] - int(anthor[2] / 2) + i,anthor[1] + int(anthor[3] / 2) ] = (255,0,0)
        for i in range(anthor[3]):
            pixels[anthor[0]-int(anthor[2]/2),anthor[1]-int(anthor[3]/2)+i]=(255,0,0)
            pixels[anthor[0] + int(anthor[2]/2),anthor[1]-int(anthor[3] / 2)+i ] = (255,0,0)
    if saveimg:
        # 保存图片
        img.save(image_name)
    print('图片已保存为:'+image_name)
    return img#返回img,画gif图用的

def save_as_gif(img_list, duration=500, gif_name="default.gif"):
    '''
    将图像列表保存为 GIF 动画
    :param img_list: 图像对象列表
    :param duration: 每帧的持续时间（毫秒）
    :param gif_name: 保存的 GIF 文件名
    '''
    print("保存 GIF 动画......")
    # 保存为 GIF 动画
    add_start_text=True
    if add_start_text and len(img_list) > 0:
        # 在第一个图像中央添加“start”文字
        img = img_list[0].copy()  # 复制第一个图像
        draw = ImageDraw.Draw(img)

        # 设置字体和大小
        try:
            font = ImageFont.truetype("arial.ttf", 20)  # 使用 Arial 字体，大小为 20
        except IOError:
            font = ImageFont.load_default()  # 如果字体文件不存在，使用默认字体

        # 获取文字尺寸
        text = "start"

        # 计算文字位置（中央）
        '''img_width, img_height = img.size
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2'''

        # 文字位置（左上）
        x = 0
        y = 0

        # 添加文字
        draw.text((x, y), text, fill=(255, 0, 0), font=font)  # 红色文字
        img_list[0] = img  # 替换第一个图像

        #接下来给每一个图像添加一个编号
        for i in range(1,len(img_list)):
            img = img_list[i].copy()
            draw = ImageDraw.Draw(img)
            # 设置字体和大小
            try:
                font = ImageFont.truetype("arial.ttf", 20)  # 使用 Arial 字体，大小为 20
            except IOError:
                font = ImageFont.load_default()  # 如果字体文件不存在，使用默认字体
            text=str(i)
            x = 0
            y = 0

            # 添加文字
            draw.text((x, y), text, fill=(0, 255, 0), font=font)  # 红色文字
            img_list[i] = img

    img_list[0].save(
        gif_name,
        save_all=True,
        append_images=img_list[1:],
        duration=duration,
        loop=0  # 无限循环
    )
    print(f"GIF 动画已保存为: {gif_name}")


def plot_greyscale_for_singledf_sigmoid(df,image_name='gray_image_default.png'):
    '''
    为一个单独的csv频谱数据绘制灰度图
    '''
    print("绘制灰度图......")
    width = df.shape[1]#列数对应图片的宽
    height = df.shape[0]#行数对应图片的高
    print("width:"+str(width))
    print("height:" + str(height))
    img = Image.new('RGB', (width, height), color='black')
    pixels = img.load()  # 创建像素映射
    #确定底噪
    all_values=df.values.flatten()
    background_noise=pd.Series(all_values).median()
    print("底噪")
    print(background_noise)


    signal_max=pd.Series(all_values).max()
    print("极大值")
    print(signal_max)




    powerwidth=signal_max-background_noise

    # 使用 Pandas 的向量化操作来设置底噪
    df_clipped = df.clip(lower=background_noise,upper=signal_max)

    def grey_sigmoid(df_clipped,background_noise,signal_refer):
        '''非线性映射'''
        powerwidth=signal_refer-background_noise
        mid_power=(signal_refer+background_noise)/2
        return ((1 / (1 + np.exp(-5*(df_clipped-mid_power)/(powerwidth/2))))*255).astype(np.uint8)
    # 计算灰度值并转换为 8 位整数

    signal_refer=signal_max if signal_max<background_noise+30 else background_noise+30
    gray_values = grey_sigmoid(df_clipped,background_noise,signal_refer)

    # 将 DataFrame 转换为 NumPy 数组
    gray_array = gray_values.values

    # 转换为图像
    img = Image.fromarray(gray_array, 'L')  # 'L' 表示灰度图

    # 保存图片
    img.save(image_name)
    print(f'图片已保存为: {image_name}')
    return img




if __name__=="__main__":
    root_dir =Path("D:\信工所电梯0.5-4\\0.5_4MHz原始信号")

    output_dir =Path("D:\信工所电梯0.5-4灰度图1")

    for dirpath, _, filenames in os.walk(root_dir):
        dirpath = Path(dirpath)
        for filename in filenames:
            if filename.endswith('.csv'):
                print(f"开始处理{filename}")
                csv_path = dirpath / filename

                # 构造输出基础路径，保持目录结构
                relative = csv_path.relative_to(root_dir)
                out_base = (output_dir / relative).with_suffix('.png')
                out_base.parent.mkdir(parents=True, exist_ok=True)

                df=pd.read_csv(csv_path)
                df=df.iloc[:,1:]

                #plot_greyscale_for_singledf(df,image_name=out_base)
                plot_greyscale_for_singledf_sigmoid(df,image_name=out_base)


