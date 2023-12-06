# wrfoutから簡易的に流跡線解析を行うためのスクリプト
# それぞれの時刻における空気塊の移動を風の空間内挿を用いて行う
# 結果はcsv形式にしてあるのでawkなりpandasあたりで読み取って下さい

# 標準ライブラリ
import datetime
import sys
import math
import multiprocessing

# 外部ライブラリ
import numpy as np
from netCDF4 import Dataset
import wrf
import geocat.f2py

# 設定ファイルの読み込み
from config import s_tmp,e_tmp,path,output,s_lat,s_lon,s_height,ana_varis,time_delta,backward,core_num
"""
# config===================================================
# 基本的にconfigファイルから読み込む
s_tmp = datetime.datetime(2017,7,4,12,00)
e_tmp = datetime.datetime(2017,7,5,00,00)
path = f"./wrfout_d01_2017-07-04_06:00:00"
output = f"back.csv"
s_lat = np.arange(32, 33, 0.05)
s_lon = np.arange(128, 129, 0.05)
s_height = 2000 #(m) 
ana_varis = {"QVAPOR":None}
time_delta = 60 # second(秒単位)
backward = True #後方流跡線解析にする場合はTrue
# 後方流跡線解析の場合でもs_tmp<e_tmpで設定する
core_num = 10 #実行コア数
# ==========================================================
"""

class Point:
    def __init__(self, lat, lon, height, time) -> None:
        self.lat = lat
        self.lon = lon
        self.hei = height
        self.tmp = time
    
    def post_lat(self):
        return self.lat
    
    def post_lon(self):
        return self.lon
    
    def post_height(self):
        return self.hei

    def post_time(self):
        return self.tmp

    def move(self, u, v, w, dt):
        # backwardの時はdtが負の値になる
        self.lat += v*dt*(90/10000/1000) 
        self.lon += u*dt*(90/10000/1000) / math.cos(math.radians(float(self.lat)))
        self.hei += w*dt
        self.tmp += datetime.timedelta(0,dt)


def calc_wrf_tstep(nc):
    wrf_datetime = []
    times = nc.variables["Times"]
    t_len = nc.dimensions["Time"].size
    for j in range(t_len):
        _tmp = ""
        for i in times[j]:
            _tmp += i.decode()
        wrf_datetime.append(datetime.datetime.strptime(_tmp, '%Y-%m-%d_%H:%M:%S'))

    time_step = wrf_datetime[1] - wrf_datetime[0]
    print(f"time step of wrfout is {time_step}")
    return time_step, wrf_datetime

def each(item, wrfout_step, wrf_datetime, wrf_lat, wrf_lon, U, V, W, Z, ana_varis,):
    now_tmp = item.post_time()
    while (s_tmp <= now_tmp) and (now_tmp <= e_tmp):
        now_tmp = item.post_time()
        z = float(item.post_height())
        
        # 欠損値の場合はその空気界の追跡を終了する
        if math.isnan(z):break

        ref_t_idx = 0
        while now_tmp >= wrf_datetime[ref_t_idx]:ref_t_idx+=1
        ratio = abs(wrf_datetime[ref_t_idx-1]-now_tmp) / wrfout_step

        u3d = U[ref_t_idx-1]*ratio + U[ref_t_idx]*(1-ratio)
        v3d = V[ref_t_idx-1]*ratio + V[ref_t_idx]*(1-ratio)
        w3d = W[ref_t_idx-1]*ratio + W[ref_t_idx]*(1-ratio)
        z3d = Z[ref_t_idx-1]*ratio + Z[ref_t_idx]*(1-ratio)

        ana_varis3d = {}
        for var in ana_varis:
            ana_varis3d[var] = ana_varis[var][ref_t_idx-1]*ratio + ana_varis[var][ref_t_idx]*(1-ratio)

        p_lat = np.array([item.post_lat()])
        p_lon = np.array([item.post_lon()])
        # 水平内挿を行う
        u1d = np.array( geocat.f2py.rcm2points(wrf_lat, wrf_lon, u3d, p_lat, p_lon) )
        v1d = np.array( geocat.f2py.rcm2points(wrf_lat, wrf_lon, v3d, p_lat, p_lon) )
        w1d = np.array( geocat.f2py.rcm2points(wrf_lat, wrf_lon, w3d, p_lat, p_lon) )
        z1d = np.array( geocat.f2py.rcm2points(wrf_lat, wrf_lon, z3d, p_lat, p_lon) )
        ana_varis1d = {}
        for var in ana_varis:
            ana_varis1d[var] = np.array( geocat.f2py.rcm2points(wrf_lat, wrf_lon, ana_varis3d[var], p_lat, p_lon) )

        # 鉛直内挿を行う
        u = wrf.interplevel( u1d.reshape([1,1,-1]), z1d.reshape([1,1,-1]), z )
        v = wrf.interplevel( v1d.reshape([1,1,-1]), z1d.reshape([1,1,-1]), z )
        w = wrf.interplevel( w1d.reshape([1,1,-1]), z1d.reshape([1,1,-1]), z )
        add_var = {}
        for var in ana_varis:
            add_var[var] = wrf.interplevel( ana_varis1d[var].reshape([1,1,-1]), z1d.reshape([1,1,-1]), z )

        if backward:
            item.move(u,v,w,-time_delta)
        else:
            item.move(u,v,w,time_delta)

        # 結果の出力
        log=open(output, 'a+')
        log.write(f'{float(item.post_lat())}, {float(item.post_lon())}, {float(item.post_height())*0.001}, {item.post_time()}, ')
        for var in ana_varis:
            log.write(f"{float(add_var[var])}, ")
        log.write(f"\n")
        log.close()
    return 0

def main():
    # set initial point and time
    s_points = []
    for i in s_lat:
        for j in s_lon:
            if backward:
                tmp_p = Point(i,j,s_height,e_tmp)
            else:
                tmp_p = Point(i,j,s_height,s_tmp)
            s_points.append(tmp_p)

    nc = Dataset(path, "r")
    wrfout_step, wrf_datetime = calc_wrf_tstep(nc)

    # 計算に必要な変数
    wrf_lat = np.ma.getdata( nc.variables["XLAT"][0,:,:] )
    wrf_lon = np.ma.getdata( nc.variables["XLONG"][0,:,:])
    U = wrf.getvar(nc, "ua", timeidx = wrf.ALL_TIMES)
    V = wrf.getvar(nc, "va", timeidx = wrf.ALL_TIMES)
    W = wrf.getvar(nc, "wa", timeidx = wrf.ALL_TIMES)
    Z = wrf.getvar(nc, "z", units="m", timeidx = wrf.ALL_TIMES)

    # 解析変数
    for var in ana_varis:
        if not var in nc.variables.keys():
            print(f"{var} is not in wrfout")
            sys.exit()   
        ana_varis[var] = np.ma.getdata(nc.variables[var])

    # 出力ファイルを作成する
    log=open(output, 'w')
    log.write(f'lat,lon,height,time,')
    for var in ana_varis:
        log.write(f"{var},")
    log.write(f"\n")
    log.close()

    done = 0
    point_num = len(s_points)
    while done<point_num:
        print(done)
        # for id, item in enumerate(s_points):
        for _ in range(core_num):
            done+=1
            if done>=point_num:continue
            process = multiprocessing.Process(
            target = each,
                kwargs = {
                    'item':s_points[done],
                    "wrfout_step":wrfout_step,
                    "wrf_datetime":wrf_datetime,
                    "wrf_lat":wrf_lat,
                    "wrf_lon":wrf_lon,
                    'U':U,
                    'V':V,
                    'W':W,
                    'Z':Z,
                    'ana_varis':ana_varis,
                    })
            process.start()
        process.join()



if __name__ == "__main__":
    print(datetime.datetime.now().replace(microsecond = 0),"START",__file__)
    main()
    print(datetime.datetime.now().replace(microsecond = 0),"END",__file__)