# import internal library
import os
import datetime
import tkinter
import tkinter.font
import tkinter.filedialog
import tkinter.ttk as ttk

# import external library
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker  
import matplotlib.cm
import matplotlib.path
import matplotlib.offsetbox
import cartopy.crs

# import recommendation library
try:
    import wrf
    wrflib = True
except:
    wrflib = False

# set constant
proj = cartopy.crs.PlateCarree()

class TKSample(tkinter.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("WRF DRAW")
        self.root.geometry("750x500")
        # self.root.attributes('-zoomed', True)
        self.root.resizable(width = False, height = False)
        self.font = tkinter.font.Font(family="MS ゴシック", size=12, weight="normal")
    
        # Init
        # Button00 = tkinter.Button(text='Init')
        # Button00.bind("<Button-1>",self.__init__)
        # Button00.place(x=10, y=0)

        # Set path
        self.status  = False
        tkinter.Label(self.root, text='PATH', font=self.font).place(x=10, y=25)

        self.EditBox01 = tkinter.Entry(self.root, width=58, font=self.font)
        # self.EditBox01 = tkinter.Entry(self.root, width=75, font=self.font)
        # self.EditBox01.bind("<Button-1>",self.getpath)
        self.EditBox01.place(x=50, y=25)

        # """
        def filedialog_clicked(event):
            iFilePath = tkinter.filedialog.askopenfilename()
            self.EditBox01.delete(0, tkinter.END)   
            self.EditBox01.insert(0,iFilePath)
            self.getpath_getpath()
        Button00 = tkinter.Button(text='Ref')
        Button00.bind("<Button-1>",filedialog_clicked)
        Button00.place(x=600, y=25)
        # """

        Button01 = tkinter.Button(text='Set path')
        Button01.bind("<Button-1>",self.getpath)
        Button01.place(x=530, y=25)

        # set variables for contourf
        self.var_flag = False
        tkinter.Label(self.root, text='Shade', font=self.font).place(x=10, y=75)
        # self.nc_vars = []

        self.nc_vars = { 
            "OFF":[],
            "Prog3D":[],
            "Prog4D":[],
            "Addi3D":[
                    # "LANDUSEF"
                    #   ,"CAPE","CIN","LCL","LFC",                    
                      ],
            # "Addi4D":[],
            }

        # see https://wrf-python.readthedocs.io/en/latest/diagnostics.html#diagnostic-table
        if wrflib:
            self.nc_vars["Diag3D"] = ["ctt",
                      "mdbz","helicity","pw","rh2","slp",
                      "ter","td2","td","updraft_helicity",
                      ],
            self.nc_vars["Diag4D"] = ["avo","theta_e",
                    # "cape_3d",
                    # "cloudfrac",
                    "dbz","geopt","omega","pressure","pvo","rh",
                    "td","tc","theta","temp","tk","tv","height",
                      ],
        
        self.combobox08 = ttk.Combobox(self.root, justify="left", values=["OFF","Prog3D","Prog4D","Diag3D","Diag4D","Addi3D"], state="readonly", width=10)
        self.combobox08.current(0)
        self.var_kind = "OFF"
        self.combobox08.bind('<<ComboboxSelected>>', self.getvarkind)
        self.combobox08.place(x=100, y=75)
        self.combobox01 = ttk.Combobox(self.root, justify="left", values=self.nc_vars[self.var_kind], state="readonly")
        self.combobox01.place(x=200, y=75)

        # set variables for contour
        self.var_c_flag = False
        tkinter.Label(self.root, text='Contour', font=self.font).place(x=10, y=100)
        self.combobox09 = ttk.Combobox(self.root, justify="left", values=["OFF","Prog3D","Prog4D","Diag3D","Diag4D","Addi3D"], state="readonly", width=10)
        self.combobox09.current(0)
        self.var_kind_c = "OFF"
        self.combobox09.bind('<<ComboboxSelected>>', self.getvarkind_c)
        self.combobox09.place(x=100, y=100)
        self.combobox05 = ttk.Combobox(self.root, justify="left", values=self.nc_vars[self.var_kind_c], state="readonly")
        self.combobox05.place(x=200, y=100)

        # set on/off of wind vector
        tkinter.Label(self.root, text='Wind', font=self.font).place(x=10, y=125)
        self.combobox06 = ttk.Combobox(self.root, justify="left", values=["OFF","ON"], state="readonly")
        self.combobox06.current(0)
        self.flag_wind = "OFF"
        self.combobox06.bind('<<ComboboxSelected>>', self.wind_on)
        self.combobox06.place(x=100, y=125)

        # set on/off of upward
        tkinter.Label(self.root, text='upward', font=self.font).place(x=10, y=150)
        self.combobox07 = ttk.Combobox(self.root, justify="left", values=["OFF","ON"], state="readonly")
        self.combobox07.current(0)
        self.flag_up = "OFF"
        self.combobox07.bind('<<ComboboxSelected>>', self.upward_on)
        self.combobox07.place(x=100, y=150)

        # set time
        tkinter.Label(self.root, text='Time', font=self.font).place(x=10, y=175)
        self.combobox02 = ttk.Combobox(self.root, justify="left", values=[], state="readonly")
        self.t_idx = 0
        self.combobox02.bind('<<ComboboxSelected>>', self.Tselect)
        self.combobox02.place(x=100, y=175)

        # set T-mode and e_time
        tkinter.Label(self.root, text='T-mode', font=self.font).place(x=10, y=200)
        self.combobox10 = ttk.Combobox(self.root, justify="left", values=["Snapshot","Difference","Average"], state="readonly", width=10)
        self.combobox10.current(0)
        self.T_mode = "Snapshot"
        self.combobox10.bind('<<ComboboxSelected>>', self.T_mode_select)
        self.combobox10.place(x=100, y=200)
        self.combobox11 = ttk.Combobox(self.root, justify="left", values=[], state="readonly")
        self.end_t_idx = 1
        self.combobox11.bind('<<ComboboxSelected>>', self.EndTselect)
        self.combobox11.place(x=200, y=200)

        # set height
        tkinter.Label(self.root, text='Coord', font=self.font).place(x=10, y=225)
        self.combobox03 = ttk.Combobox(self.root, justify="left", values=["Z(km)","P(hPa)"], state="readonly", width=10)
        self.combobox03.current(0)
        self.coord = "Z(km)"
        self.combobox03.bind('<<ComboboxSelected>>', self.get_coordinate)
        self.combobox03.place(x=100, y=225)

        tkinter.Label(self.root, text='Height', font=self.font).place(x=200, y=225)
        self.combobox04 = ttk.Combobox(self.root, justify="left", values=list( np.arange(0.5, 18.5, 0.5) ), state="readonly", width=10)
        self.height = 10
        self.combobox04.bind('<<ComboboxSelected>>', self.get_height)
        self.combobox04.place(x=250, y=225)

        # 東西南北
        base_y = 250
        tkinter.Label(self.root, text='N:', font=self.font).place(x=70, y=base_y)  
        self.N = tkinter.Entry(self.root, width=6, font=self.font)
        self.N.place(x=100, y=base_y)
        tkinter.Label(self.root, text='W:', font=self.font).place(x=20, y=base_y+25)  
        self.W = tkinter.Entry(self.root, width=6, font=self.font)
        self.W.place(x=50, y=base_y+25)  
        tkinter.Label(self.root, text='E:', font=self.font).place(x=120, y=base_y+25)  
        self.E = tkinter.Entry(self.root, width=6, font=self.font) 
        self.E.place(x=150, y=base_y+25) 
        tkinter.Label(self.root, text='S:', font=self.font).place(x=70, y=base_y+50)  
        self.S = tkinter.Entry(self.root, width=6, font=self.font) 
        self.S.place(x=100, y=base_y+50)  
        # 領域のクリア
        Button03 = tkinter.Button(text='Clear Region', font=self.font)
        Button03.bind("<Button-1>",self.C_region)
        Button03.place(x=180, y=base_y+50)


        Button02 = tkinter.Button(text='DRAW', font=self.font)
        Button02.bind("<Button-1>",self.draw)
        Button02.place(x=10, y=350)

        # Optional
        base_y = 400
        tkinter.Label(self.root, text='Optional', font=self.font).place(x=10, y=base_y)  
        tkinter.Label(self.root, text='Shade Level', font=self.font).place(x=10, y=base_y+25) 
        tkinter.Label(self.root, text='Min:', font=self.font).place(x=100, y=base_y+25) 
        self.shade_lev_min = tkinter.Entry(self.root, width=6, font=self.font) 
        self.shade_lev_min.place(x=130, y=base_y+25)  
        tkinter.Label(self.root, text='Max:', font=self.font).place(x=200, y=base_y+25) 
        self.shade_lev_max = tkinter.Entry(self.root, width=6, font=self.font) 
        self.shade_lev_max.place(x=230, y=base_y+25)  
        # Set Extend
        tkinter.Label(self.root, text='Extend', font=self.font).place(x=300, y=base_y+25) 
        self.combobox12 = ttk.Combobox(self.root, justify="left", values=['neither', 'both', 'min', 'max'], state="readonly", width=10)
        self.combobox12.current(1)
        self.shade_extend = "both"
        self.combobox12.bind('<<ComboboxSelected>>', self.set_shade_extend)
        self.combobox12.place(x=350, y=base_y+25)
        # Set Cmap
        tkinter.Label(self.root, text='Cmap', font=self.font).place(x=450, y=base_y+25) 
        self.combobox13 = ttk.Combobox(self.root, justify="left", values=['jet','rainbow','ocean','gist_earth','terrain','turbo'], state="readonly", width=10)
        self.combobox13.current(0)
        self.combobox13.place(x=500, y=base_y+25)

    def C_region(self, event):
        self.N.delete(0, tkinter.END)
        self.W.delete(0, tkinter.END)
        self.E.delete(0, tkinter.END)
        self.S.delete(0, tkinter.END)
    
    def set_shade_extend(self, event):
        self.shade_extend = self.combobox12.get()

    def getpath(self, event):
        self.getpath_getpath()

    def getpath_getpath(self):
        self.path = self.EditBox01.get()
        self.status = os.path.isfile(self.path)
        tkinter.Label(self.root, text=f"path:{self.status}", font=self.font).place(x=10, y=50)
        print(f"{self.path}:{self.status}")
        if "wrfinput" in self.path:
            self.nc_vars["Addi3D"].append("LANDUSEF")

        self.getnc_vars()

        # Read dimension
        self.t_len = self.nc.dimensions["Time"].size
        self.x_len = self.nc.dimensions["west_east"].size
        self.y_len = self.nc.dimensions["south_north"].size
        self.z_len = self.nc.dimensions["bottom_top"].size
        tkinter.Label(self.root, text=f"T:{self.t_len} Z:{self.z_len} Y:{self.y_len} X:{self.x_len}", font=self.font).place(x=300, y=50)

        # Read essential variables
        self.times = np.ma.getdata( self.nc.variables["Times"] )
        self.get_time()
        self.xlat  = np.ma.getdata( self.nc.variables["XLAT"]  )
        self.xlon  = np.ma.getdata( self.nc.variables["XLONG"] )
        self.N.insert(0,format(np.max(self.xlat), '.2f').rstrip('0'))
        self.W.insert(0,format(np.min(self.xlon), '.2f').rstrip('0'))
        self.E.insert(0,format(np.max(self.xlon), '.2f').rstrip('0'))
        self.S.insert(0,format(np.min(self.xlat), '.2f').rstrip('0'))

        self.combobox02 = ttk.Combobox(self.root, justify="left", values=list(np.arange(self.t_len)), state="readonly")
        self.combobox02.current(0)
        self.combobox02.bind('<<ComboboxSelected>>', self.Tselect)
        self.combobox02.place(x=100, y=175)

    def getnc_vars(self):
        if self.status:
            try:
                self.nc = netCDF4.Dataset(self.path)
                tkinter.Label(self.root, text=f"Open netCDF file", font=self.font).place(x=150, y=50)
                print(f"open {self.path}")

            except:
                tkinter.Label(self.root, text=f"file is not netCDF", font=self.font).place(x=150, y=50)
                self.status = False
                print(f"canot open {self.path}")
                return
                        
            self.nc_vars_all = list( self.nc.variables.keys() )
            # lat,lonの広がりを持つ変数だけにする
            for _vv in self.nc_vars_all:
                dim = self.nc.variables[_vv].dimensions
                if dim == ('Time', 'bottom_top', 'south_north', 'west_east'):
                    self.nc_vars["Prog4D"].append(_vv)
                elif dim == ('Time', 'south_north', 'west_east'):
                    self.nc_vars["Prog3D"].append(_vv)

    def getvarkind(self, event):
        self.var_kind = self.combobox08.get()
        self.combobox01 = ttk.Combobox(self.root, justify="left", values=self.nc_vars[self.var_kind], state="readonly")
        self.combobox01.bind('<<ComboboxSelected>>', self.getvariables)
        self.combobox01.place(x=200, y=75)
        if self.var_kind == "OFF":
            self.var_flag = False
            tkinter.Label(self.root, text=f"OFF", font=self.font, width=20).place(x=370, y=75)

    def getvarkind_c(self, event):
        self.var_kind_c = self.combobox09.get()
        self.combobox05 = ttk.Combobox(self.root, justify="left", values=self.nc_vars[self.var_kind_c], state="readonly")
        self.combobox05.bind('<<ComboboxSelected>>', self.getvariables_c)
        self.combobox05.place(x=200, y=100)
        if self.var_kind_c == "OFF":
            self.var_c_flag = False
            tkinter.Label(self.root, text=f"OFF", font=self.font, width=20).place(x=370, y=100)

    def T_mode_select(self, event):
        self.T_mode = self.combobox10.get()
        print(self.T_mode)
        if self.T_mode == "Snapshot":
            self.combobox11 = ttk.Combobox(self.root, justify="left", values=None, state="readonly")
        else:
            self.combobox11 = ttk.Combobox(self.root, justify="left", values=list(np.arange(self.t_len)[1:]), state="readonly")
            self.combobox11.bind('<<ComboboxSelected>>', self.EndTselect)
            self.combobox11.current(0)
        self.combobox11.place(x=200, y=200)

    def getvariables(self, event):
        self.var_name = self.combobox01.get()
        self.var_flag = True
        tkinter.Label(self.root, text=f"{self.var_kind}:{self.var_name}", font=self.font, width=20).place(x=370, y=75)

    def getvariables_c(self, event):
        self.var_c_name = self.combobox05.get()
        self.var_c_flag = True
        tkinter.Label(self.root, text=f"{self.var_kind_c}:{self.var_c_name}", font=self.font, width=20).place(x=370, y=100)

    def wind_on(self, event):
        self.flag_wind = self.combobox06.get()
        tkinter.Label(self.root, text=f"{self.flag_wind}", font=self.font, width=20).place(x=370, y=125)

    def upward_on(self, event):
        self.flag_up = self.combobox07.get()
        tkinter.Label(self.root, text=f"{self.flag_up}", font=self.font, width=20).place(x=370, y=150)
    
    def Tselect(self, event):
        self.t_idx = int( self.combobox02.get() )
        self.get_time()

    def EndTselect(self, event):
        self.end_t_idx = int( self.combobox11.get() )
        self.get_end_time()

    def get_time(self):
        self.tmp=""
        for i in self.times[self.t_idx]:self.tmp += i.decode()
        self.tmp=datetime.datetime.strptime(self.tmp, '%Y-%m-%d_%H:%M:%S')
        print(self.tmp)
        tkinter.Label(self.root, text=f"{self.tmp}(UTC)", font=self.font).place(x=370, y=175)

    def get_end_time(self):
        self.end_tmp=""
        for i in self.times[self.end_t_idx]:self.end_tmp += i.decode()
        self.end_tmp=datetime.datetime.strptime(self.end_tmp, '%Y-%m-%d_%H:%M:%S')
        print(self.end_tmp)
        tkinter.Label(self.root, text=f"{self.end_tmp}(UTC)", font=self.font).place(x=370, y=200)

    def get_coordinate(self, event):
        self.coord = self.combobox03.get()
        if self.coord == "P(hPa)":
            self.combobox04 = ttk.Combobox(self.root, justify="left", values=list( np.arange(1000, 200, -50) ), state="readonly", width=10)
            self.combobox04.bind('<<ComboboxSelected>>', self.get_height)
            self.combobox04.place(x=250, y=225)            

    def get_height(self, event):
        self.height = self.combobox04.get()
        print(f"{self.coord}:{self.height}")
        tkinter.Label(self.root, text=f"{self.coord}:{self.height}", font=self.font).place(x=370, y=225)

    # これより下は図を描くための関数##########################################################################
    def set_ax(self,ax):
        try:
            angle = int( max( abs(self.extent[0]-self.extent[1])/5, abs(self.extent[2]-self.extent[3])/5  ) )
        except:# ゼロ割回避のため
            angle = 1
        if angle<1:
            angle=0.2
        xticks = np.arange(0, 360.1, angle)
        yticks = np.arange(-90, 90.1, angle)
        ax.set_xticks(xticks, crs=proj)
        ax.set_yticks(yticks, crs=proj)
        ax.tick_params(direction='out', length=3, width=0.7, colors='k',grid_color='k', grid_alpha=0.5)
        ax.tick_params(which='minor', axis='x', length=2, color='k')
        ax.tick_params(which='minor', axis='y', length=2, color='k')
        gl = ax.gridlines(crs=proj, draw_labels=False, linewidth=0.5, linestyle='--', color='gray', alpha=0.5)
        gl.xlocator = matplotlib.ticker.FixedLocator(xticks) # 経度線を描く値
        gl.ylocator = matplotlib.ticker.FixedLocator(yticks) # 緯度線を描く値
        ax.coastlines(linewidths = 1, zorder = 1, resolution='10m',) 
        ax.set_extent(self.extent, crs=proj)

    def getvar_multi(self, hoge_name, units=None):
        # 平均や差分を取る場合も含めてこの関数で値の取得を行う
        if units==None:
            array = wrf.getvar(self.nc, hoge_name, timeidx=self.t_idx)
        else:
            array = wrf.getvar(self.nc, hoge_name, units=units, timeidx=self.t_idx)
        var_name = array.name
        var_units= array.units
        if self.T_mode == "Difference":
            if units==None:
                array_after = wrf.getvar(self.nc, hoge_name, timeidx=self.end_t_idx)
            else:
                array_after = wrf.getvar(self.nc, hoge_name, units=units, timeidx=self.end_t_idx)
            array = array_after - array
        elif self.T_mode == "Average":
            for hoge_t in range(self.t_idx+1,self.end_t_idx+1):
                if self.end_t_idx == self.t_idx:
                    print("Please set different time index.")
                else:
                    if units==None:
                        array += wrf.getvar(self.nc, hoge_name, timeidx=hoge_t)
                    else:
                        array += wrf.getvar(self.nc, hoge_name, units=units, timeidx=hoge_t)
                    # array += wrf.getvar(self.nc, hoge_name, timeidx=hoge_t, units=units)
                    array = array / (self.end_t_idx - self.t_idx + 1 )
        else: 
            pass #これはスナップショットの場合
        return array, var_name, var_units

    def get_plt_extent(self):
        try:
            self.extent = [float(self.W.get()), float(self.E.get()), float(self.S.get()), float(self.N.get())]
        except:
            self.extent = [np.min(self.xlon), np.max(self.xlon), np.min(self.xlat), np.max(self.xlat)]
    
    def get_plt_coordinate(self):
        if self.coord == "P(hPa)":
            self.P = self.getvar_multi("pressure")[0]
        else:
            self.Z = self.getvar_multi("z", units="km")[0]
    
    def draw_landuse(self, ax):
        # 本当は21種類あるけど色が20色しか用意出来なかったから、保留
        temp_array = np.zeros([self.var_shade.shape[-2],self.var_shade.shape[-1]])
        for _i in range(20):
            temp_array += self.var_shade[_i,:,:] * _i 
        self.var_shade = temp_array
        _lon = (self.xlon[self.t_idx, self.y_len//2 ,1:] + self.xlon[self.t_idx, self.y_len//2 ,:-1])/2
        _lat = (self.xlat[self.t_idx, 1:, self.x_len//2] + self.xlat[self.t_idx, :-1, self.x_len//2])/2
        shade_plot = ax.pcolormesh(
                        _lon,
                        _lat,
                        self.var_shade[1:-1,1:-1],
                        cmap = plt.get_cmap("tab20"),
                        vmin = -0.5,
                        vmax = 19.5,
                        alpha = 0.8,
                        )
        cax = ax.inset_axes([1.04, 0.1, 0.03, 0.8], transform=ax.transAxes)#cbarの座標
        plt.colorbar(shade_plot, cax = cax, orientation='vertical',extendfrac = 'auto', ticks = np.arange(0, 20, 1) ,label="LANDUSEF")

    def draw_shade(self, ax):
        print("shade")
        self.var_shade,var_name,var_units = self.getvar_multi(self.var_name)
        self.var_dis = f"{var_name}[{var_units}]"
        if self.var_kind == "Addi3D":
            if self.var_name == "LANDUSEF":
                self.draw_landuse(ax)
                return
        elif self.var_shade.ndim == 3:
            if self.coord == "P(hPa)":
                self.var_shade = wrf.interplevel(self.var_shade, self.P, float(self.height))
            else:
                self.var_shade = wrf.interplevel(self.var_shade, self.Z, float(self.height))

        vmin = np.nanmin(self.var_shade)
        vmax = np.nanmax(self.var_shade)
        try:
            vmin_g = float(self.shade_lev_min.get())
            vmax_g = float(self.shade_lev_max.get())
            if vmin_g < vmax and vmax_g > vmin:
                vmin, vmax = vmin_g, vmax_g
        except:
            pass
        if abs(vmin)>3 and abs(vmax)>3:
            vmin = int(vmin)
            vmax = int(vmax)
        self.shade_lev_min.delete(0, tkinter.END)  
        self.shade_lev_max.delete(0, tkinter.END)  
        self.shade_lev_min.insert(0,vmin)
        self.shade_lev_max.insert(0,vmax)

        try:step =  (vmax-vmin)/10
        except:step = 1e-6
        self.shade_range = np.arange(vmin, vmax+1e-6, step )

        shade_plot = ax.contourf(
                    self.xlon[self.t_idx,:,:],
                    self.xlat[self.t_idx,:,:],
                    self.var_shade,
                    transform = proj,
                    levels = self.shade_range,
                    cmap = matplotlib.colormaps[self.combobox13.get()],
                    extend = self.shade_extend,
                    zorder = 0,
                    )
        cax = ax.inset_axes([1.04, 0.1, 0.03, 0.8], transform=ax.transAxes)#cbarの座標
        plt.colorbar(shade_plot, cax = cax, orientation='vertical',extendfrac = 'auto', ticks = self.shade_range)
        text = matplotlib.offsetbox.AnchoredText(f"shade:{self.var_dis}", loc='lower right', prop=dict(size=13), pad=0.3, borderpad=0., frameon=True, bbox_to_anchor=(1., 0.), bbox_transform=ax.transAxes)
        ax.add_artist(text)

    def draw_contour(self, ax):
        print("contour")
        self.var_c,var_name,var_units = self.getvar_multi(self.var_c_name)
        self.var_cdis = f"{var_name}[{var_units}]"
        if self.var_c.ndim == 3:
            if self.coord == "P(hPa)":
                self.var_c = wrf.interplevel(self.var_c, self.P, float(self.height))
            else:
                self.var_c = wrf.interplevel(self.var_c, self.Z, float(self.height))

        contour=ax.contour(
            self.xlon[self.t_idx,:,:],
            self.xlat[self.t_idx,:,:],
            self.var_c,
            transform = proj,
            # levels=lev,
            colors="black",
            extend = 'both',
            zorder = 0,
            )
        ax.clabel(contour) 
        text = matplotlib.offsetbox.AnchoredText(f"contour:{self.var_cdis}", loc='upper left', prop=dict(size=13), pad=0.3, borderpad=0., frameon=True, bbox_to_anchor=(0., 1.), bbox_transform=ax.transAxes)
        ax.add_artist(text)

    def draw_wind(self, ax):
        print("wind")
        self.ua = np.ma.getdata( self.getvar_multi("ua", units="m s-1")[0] )
        self.va = np.ma.getdata( self.getvar_multi("va", units="m s-1")[0] )
        if self.coord == "P(hPa)":
            self.ua = wrf.interplevel(self.ua, self.P, float(self.height))
            self.va = wrf.interplevel(self.va, self.P, float(self.height))
        else:
            self.ua = wrf.interplevel(self.ua, self.Z, float(self.height))
            self.va = wrf.interplevel(self.va, self.Z, float(self.height))
        wind_plot = ax.quiver(self.xlon[self.t_idx,::15,::15],self.xlat[self.t_idx,::15,::15],self.ua[::15,::15], self.va[::15,::15], units='xy', transform=proj)
        try:
            ref_length = int( abs(np.nanmean(self.ua)) + abs(np.nanmean(self.va)) ) * 2
            ax.quiverkey(wind_plot, 0.92, -0.065, ref_length, str(ref_length)+r'$\left[ \frac{m}{s} \right]$', labelpos='N',color='red',labelsep=0.05, transform=proj, labelcolor="red")
        except:
            pass

    def draw_up(self, ax):
        print("up")
        self.wa = np.ma.getdata( self.getvar_multi("wa", units="m s-1")[0] )
        if self.coord == "P(hPa)":
            self.wa = wrf.interplevel(self.wa, self.P, float(self.height))
        else:
            self.wa = wrf.interplevel(self.wa, self.Z, float(self.height))
        lev=np.arange(1, 3, 1)*0.05
        ax.contourf(
                    self.xlon[self.t_idx,:,:],
                    self.xlat[self.t_idx,:,:],
                    self.wa,
                    transform = proj,
                    levels=lev,
                    cmap = "gray", 
                    extend = 'max',
                    zorder = 0,
                    alpha = 0.5,
                    )
            
    def draw_csr_shade(self, ax2):
        # 鉛直断面は
        # m単位のみ
        # また、単一時間のみを想定
        self.cross_s = wrf.CoordPair(lat = self.csr_lat[0], lon = self.csr_lon[0])
        self.cross_e = wrf.CoordPair(lat = self.csr_lat[1], lon = self.csr_lon[1])
        self.csr_var_shade = wrf.getvar(self.nc, self.var_name, timeidx=self.t_idx)
        
        vmin = np.nanmin(self.csr_var_shade)
        vmax = np.nanmax(self.csr_var_shade)
        if abs(vmin)>3 and abs(vmax)>3:
            vmin = int(vmin)
            vmax = int(vmax)
        try:step =  (vmax-vmin)/10
        except:step = 1e-6
        self.csr_shade_range = np.arange(vmin, vmax+1e-6, step )
        
        self.ht =  wrf.getvar(self.nc, "z", timeidx=self.t_idx)
        self.cross_array = wrf.vertcross(
                                self.csr_var_shade, 
                                self.ht, 
                                wrfin = self.nc,
                                start_point = self.cross_s,
                                end_point   = self.cross_e,
                                latlon = True, 
                                meta = True
                                )
        self.csr_x = np.arange(0, self.cross_array.shape[-1], 1)
        self.csr_y = wrf.to_np(self.cross_array.coords["vertical"])
        csr_shade_plt = ax2.contourf( 
                                    # self.csr_x,
                                    # self.csr_y,
                                    wrf.to_np(self.cross_array), 
                                    cmap = matplotlib.colormaps[self.combobox13.get()],
                                    extend = self.shade_extend,
                                    zorder = 0,
                                    levels = self.csr_shade_range,
                                    )
        cax2 = ax2.inset_axes([1.04, 0.1, 0.03, 0.8], transform=ax2.transAxes)#cbarの座標
        plt.colorbar(csr_shade_plt, cax = cax2, orientation='vertical',extendfrac = 'auto', ticks = self.csr_shade_range)

        # Set the x-ticks to use latitude and longitude labels.
        coord_pairs = wrf.to_np(self.cross_array.coords["xy_loc"])
        csr_x_ticks = np.arange(coord_pairs.shape[0])
        x_labels = [pair.latlon_str(fmt="{:.2f}, {:.2f}") for pair in wrf.to_np(coord_pairs)]
        ax2.set_xticks(csr_x_ticks[::20])
        ax2.set_xticklabels(x_labels[::20], rotation=45)

        # Set the y-ticks to be height.
        vert_vals = wrf.to_np(self.cross_array.coords["vertical"])
        v_ticks = np.arange(vert_vals.shape[0])
        ax2.set_yticks(v_ticks[::20])
        ax2.set_yticklabels(vert_vals[::20])

        ax2.set_xlabel("Latitude, Longitude")
        if self.coord == "P(hPa)":
            ax2.set_ylabel("Pressure (hPa)")
        else:
            ax2.set_ylabel("Height (m)")


        text = matplotlib.offsetbox.AnchoredText(f"shade:{self.var_dis}", loc='upper right', prop=dict(size=13), pad=0.3, borderpad=0., frameon=True, bbox_to_anchor=(1., 0.), bbox_transform=ax2.transAxes)
        ax2.add_artist(text)

    def set_title(self, ax):
        if self.T_mode=="Difference":
            ax.set_title(f"Dif({self.end_tmp})-({self.tmp})(UTC)[{self.coord}:{self.height}]")
        elif self.T_mode=="Average":
            ax.set_title(f"Ave({self.tmp})-({self.end_tmp})(UTC)[{self.coord}:{self.height}]")
        else:
            ax.set_title(f"{self.tmp}(UTC)[{self.coord}:{self.height}]")

    def set_title2(self, ax2):
        ax2.set_title(f"{self.tmp}(UTC)")
        # if self.T_mode=="Difference":
        #     ax2.set_title(f"Dif({self.end_tmp})-({self.tmp})(UTC)")
        # elif self.T_mode=="Average":
        #     ax2.set_title(f"Ave({self.tmp})-({self.end_tmp})(UTC)")
        # else:
        #     ax2.set_title(f"{self.tmp}(UTC)")


    # メインの関数
    def draw(self, event):
        if not self.status:
            print("Please set nc file and variables")
            return
        print("Ploting...")
        self.get_plt_extent()
        self.get_plt_coordinate()

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection=proj)
        self.set_ax(ax)
        
        if self.var_flag:
            self.draw_shade(ax)

        if self.var_c_flag:
            self.draw_contour(ax)

        if self.flag_wind == "ON":
            self.draw_wind(ax)

        if self.flag_up == "ON":
            self.draw_up(ax)
        
        self.set_title(ax)

        plt.show()

    
def WRFdraw():
    app = TKSample(tkinter.Tk())
    app.mainloop()

if __name__ == '__main__':
    print("Running...")
    WRFdraw()