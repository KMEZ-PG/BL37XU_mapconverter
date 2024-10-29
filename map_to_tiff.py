# この .py ファイルを 生データと同じ階層 に配置
import os
import re
import gc
import pandas as pd
import numpy as np
from PIL import Image

# setting global params
files = os.listdir()
files.remove('map_to_tiff.py')

# 生データファイルがあるディレクトリに格納されるはず
for file in files:
    lines = []
    with open(file, 'r', encoding = 'UTF-8') as paramset:
        line_num = 0
        while line_num < 10:
            line_num += 1
            txt = paramset.readline()
            lines.append(txt)
# 正規表現の練習がてら
    x_start = re.findall(r'\D\d+\.\d+', lines[4])
    x_end = re.findall(r'\D\d+\.\d+', lines[5])
    x_step = re.findall(r'\D\d+\.\d+', lines[6])
    z_start = re.findall(r'\D\d+\.\d+', lines[7])
    z_end = re.findall(r'\D\d+\.\d+', lines[8])
    z_step = re.findall(r'\D\d+\.\d+', lines[9])

    scan_width = int((float(x_end[0]) - float(x_start[0]))/float(x_step[0])) # スキャンの幅
    scan_hight = int((float(z_end[0]) - float(z_start[0]))/float(z_step[0])) # スキャンの高さ
    
    del lines, line_num, txt, x_start, x_end, x_step, z_start, z_end, z_step
    gc.collect()

# スキャン方向判別
# 初動の座標値変化をみる
    df = pd.read_csv(file, header = 12, sep = '\t')
    ch_num = 7 # しばらくCh数は変わんないと思う
    roi_num = int((df.shape[1] - 4)/ch_num -1)
    if abs(df['x/um'][1]-df['x/um'][0]) > abs(df['z/um'][1]-df['z/um'][0]):
        on_the_fly = 0
    else:
        on_the_fly = 1
    for m in range(roi_num):
        os.makedirs('processed/' + file, exist_ok=True)
    
    print(file)
    for i in range(roi_num):
        im_2d = np.zeros((scan_hight, scan_width))
        if on_the_fly == 0:
            for j in range(scan_hight):
                for k in range(scan_width):
                    for l in range(ch_num):
                        im_2d[j][k] += df['ROI'+str(i + 1)+'_Ch'+ str(l + 1)][k + scan_width*j]
                    im_2d[j][k] = im_2d[j][k] / df['ch1(I0)'][k + scan_width*j]
            img = Image.fromarray(im_2d)
            img.save('processed/' + file + '/roi_' + str(i + 1)+'.tif')
        else:
            for j in range(scan_width):
                for k in range(scan_hight):
                    for l in range(ch_num):
                        im_2d[k][j] += df['ROI'+str(i + 1)+'_Ch'+ str(l + 1)][k + scan_hight*j]
                    im_2d[k][j] = im_2d[k][j] / df['ch1(I0)'][k + scan_hight*j]
            img = Image.fromarray(im_2d)
            img.save('processed/' + file + '/roi_' + str(i + 1)+'.tif')
