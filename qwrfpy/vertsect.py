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

from WRFdraw import TKSample
class Vertsect(TKSample):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("WRF DRAW VertSect")
        self.root.geometry("750x550")
        self.root.resizable(width = False, height = False)
        self.font = tkinter.font.Font(family="MS ゴシック", size=12, weight="normal")

        # accept Only 4D variables
        self.combobox08 = ttk.Combobox(self.root, justify="left", values=["SET","Prog4D","Diag4D"], state="readonly", width=10)
        self.combobox08.current(0)
        self.var_kind = "OFF"
        self.combobox08.bind('<<ComboboxSelected>>', self.getvarkind)
        self.combobox08.place(x=100, y=75)
        

        # vertical cross-section
        base_y = 475
        Button04 = tkinter.Button(text='Vert-DRAW', font=self.font)
        Button04.bind("<Button-1>",self.Vert_draw)
        Button04.place(x=10, y=base_y)
        tkinter.Label(self.root, text='A(lat,lon):', font=self.font).place(x=100, y=base_y)  
        self.Vert_alat = tkinter.Entry(self.root, width=6, font=self.font)
        self.Vert_alon = tkinter.Entry(self.root, width=6, font=self.font)
        self.Vert_alat.place(x=180, y=base_y)  
        self.Vert_alon.place(x=260, y=base_y)  
        tkinter.Label(self.root, text='B(lat,lon):', font=self.font).place(x=320, y=base_y)  
        self.Vert_blat = tkinter.Entry(self.root, width=6, font=self.font)
        self.Vert_blon = tkinter.Entry(self.root, width=6, font=self.font)
        self.Vert_blat.place(x=400, y=base_y)  
        self.Vert_blon.place(x=480, y=base_y)  
    
    def getpath_getpath(self):
        super().getpath_getpath()
        self.Vert_alat.insert(0, format(float(self.xlat[0, 0, self.x_len//2]),'.2f').rstrip('0')) 
        self.Vert_alon.insert(0, format(float(self.xlon[0, 0, 0]),'.2f').rstrip('0')) 
        self.Vert_blat.insert(0, format(float(self.xlat[0, -1, -1]),'.2f').rstrip('0'))
        self.Vert_blon.insert(0, format(float(self.xlon[0, 0, -1]),'.2f').rstrip('0'))
        # self.getvarkind
        # self.combobox01 = ttk.Combobox(self.root, justify="left", values=self.nc_vars[self.var_kind], state="readonly")
        # self.combobox01.place(x=200, y=75)
    
    def draw_line(self, ax):
        self.csr_lon = [float(self.Vert_alon.get()), float(self.Vert_blon.get())]
        self.csr_lat = [float(self.Vert_alat.get()), float(self.Vert_blat.get())]
        ax.plot(self.csr_lon, self.csr_lat, color="red", transform = proj, linewidth = 2)

    def draw_ter(self ,ax2):
        ter = wrf.getvar(self.nc, "ter", timeidx=self.t_idx)
        self.ter_line = wrf.interpline(
                        ter, 
                        wrfin = self.nc, 
                        start_point = self.cross_s, 
                        end_point = self.cross_e
                        )
        # print(wrf.to_np(self.ter_line))
        # print((wrf.to_np(self.cross_array)).shape)
        ax2.fill_between(self.csr_x, 0, wrf.to_np(self.ter_line)/100,  facecolor="saddlebrown", zorder = 0)

    def Vert_draw(self, event):
        print("Ploting...")
        self.get_plt_extent()
        self.get_plt_coordinate()

        fig = plt.figure(figsize=(16,8))
        fig.tight_layout()
        fig.subplots_adjust(wspace=0.5, bottom=0.2)
        ax = fig.add_subplot(1, 2, 1, projection=proj)
        self.set_ax(ax)
        
        if self.var_flag:
            self.draw_shade(ax)

        if self.var_c_flag:
            self.draw_contour(ax)

        if self.flag_wind == "ON":
            self.draw_wind(ax)

        if self.flag_up == "ON":
            self.draw_up(ax)
        
        self.draw_line(ax)
        self.set_title(ax)

        # 鉛直断面図を2つ目の図として描く
        if not self.var_flag:
            # 鉛直断面を描くために陰影の情報は必須とする
            print("Set variables in shade.")
            return
        if  not self.var_kind in ["Prog4D", "Diag4D"]: 
            print("Set 4D variables in shade.")
            return

        ax2 = fig.add_subplot(1, 2, 2)
        self.draw_csr_shade(ax2)
        self.draw_ter(ax2)

        self.set_title2(ax2)
        
        plt.show()

def Vertdraw():
    app = Vertsect(tkinter.Tk())
    app.mainloop()

if __name__ == '__main__':
    print("Running...")
    Vertdraw()
