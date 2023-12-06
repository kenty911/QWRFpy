

# 標準ライブラリ
import datetime
import os
# import csv
# import sys

# 外部ライブラリ
from netCDF4 import Dataset
import wrf
import numpy as np
import pandas as pd
import matplotlib.colors
import matplotlib.cm

# 設定ファイルの読み込み
import config
path = config.path
csv_f = config.output
output = f"{csv_f[:-3]}txt"


def main():
    lev=np.arange(0,4.1,0.1) #描写の高度を指定する(最小値は地表面を描くために0にすべし)
    z_times=1 #高度方向のデフォルメ

    nc = Dataset(path)

    lat = nc.variables["XLAT"][0,:,:]
    lon = nc.variables["XLONG"][0,:,:]
    x_len = nc.dimensions["west_east"].size
    y_len = nc.dimensions["south_north"].size
    # t_len = nc.dimensions["Time"].size
    # z_len = nc.dimensions["bottom_top"].size
    idx_z = len(lev)

    ter = np.ma.getdata( wrf.getvar(nc, "ter", units="km", timeidx=0) )#モデル高度の取得
    ter = ter[np.newaxis,:,:]+np.zeros([idx_z,y_len,x_len])
    ter_3d=np.where(ter>lev[:,np.newaxis,np.newaxis],1,0)#土地がある場所は1無い場所は2にしている


    #ファイルを開く
    f = open(output, 'w')

    for i_z, z in enumerate(lev):
        for i_lat in range(y_len):
            for i_lon in range(x_len):
                if ter_3d[i_z,i_lat,i_lon]==1:
                    f.write(f"{float(lon[i_lat,i_lon])} {float(lat[i_lat,i_lon])} {str(z*z_times)} 140 120 0\n")


    
    df = pd.read_csv(csv_f)

    cmap_d = matplotlib.cm.jet(np.arange(matplotlib.cm.jet.N))
    cmap_d[:,:3] = cmap_d[:,:3]*255
    #0~25.5(g/kg)でスケール
    for i in range(len(df.lat)):
        color = int(min(255, max(float(df.QVAPOR[i])*10000, 0)))
        f.write(f"{float(df.lon[i])} {float(df.lat[i])} {float(df.height[i]*z_times)} {cmap_d[color,0]} {cmap_d[color,1]} {cmap_d[color,2]}\n")
    f.close()

if __name__ == "__main__":
    print(datetime.datetime.now().replace(microsecond = 0),"START",__file__)
    main()
    print(datetime.datetime.now().replace(microsecond = 0),"END",__file__)