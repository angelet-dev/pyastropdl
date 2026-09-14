from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


def set_dark_theme():

    BASE_DIR = Path(__file__).resolve().parent


    FONTS_DIR = BASE_DIR / "fonts" 


    GEIST_FONT_PATH = FONTS_DIR / "Geist" / "static"/ "Geist-Bold.ttf"
    IBM_MONO_FONT_PATH = FONTS_DIR /"IBM_Plex_Mono"/ "IBMPlexMono-Bold.ttf"

    geist_path = str(GEIST_FONT_PATH)
    ibm_mono_path = str(IBM_MONO_FONT_PATH)

    fm.fontManager.addfont(geist_path)
    fm.fontManager.addfont(ibm_mono_path)

    geist_prop = fm.FontProperties(fname=geist_path)
    ibm_mono_prop = fm.FontProperties(fname=ibm_mono_path)

    plt.rcParams['font.sans-serif'] = geist_prop.get_name()
    plt.rcParams['font.monospace'] = ibm_mono_prop.get_name()
    plt.rcParams['axes.titlesize'] = 16       
    plt.rcParams['axes.titlepad'] = 15


    plt.rcParams.update({
        'figure.facecolor': "#1f1e1e",  
        'axes.facecolor': "#232222",    
        'axes.edgecolor': "#414141",    
        'axes.labelcolor': '#c4c4c4',   
        'xtick.color': "#c4c4c4",     
        'ytick.color': "#c4c4c4",      
        'text.color': '#c4c4c4',        
        'grid.color': "#414141",      
        'grid.linestyle': '-',       
        'grid.alpha': 1,                     
        "text.usetex": False,
        "axes.labelsize": 12,
        "font.size": 12,
        "font.family": 'sans-serif',
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })


def set_plot_costomitation(ax):

    ax.tick_params(
        axis='both',         
        which='both',        
        direction='out',     
        length=6,             
        width=1.2,             
        labelsize=10,         
        pad=5                 
    )

    ax.spines['left'].set_color("#9f9f9f")
    ax.spines['left'].set_position(('axes',-0.03))
    ax.spines['bottom'].set_color("#9f9f9f")
    ax.spines['bottom'].set_position(('axes',-0.03))
    ax.spines['right'].set_visible(False)
    ax.spines['right'].set_position(('axes',1.08))
    ax.spines['top'].set_visible(False)

    interval = ax.xaxis.get_data_interval()
    x_min, x_max = interval[0] * 1.03, interval[1]*0.9 
    ax.set_xlim(x_min, x_max)
    num_ticks = 10
    ticks = np.linspace(x_min, x_max, num_ticks)

    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))

    interval_y = ax.yaxis.get_data_interval()
    y_min, y_max = interval_y[0] -100 , interval_y[1]*1.03
    ax.set_ylim(y_min, y_max)
    num_ticks = 10
    ticks = np.linspace(y_min, y_max, num_ticks)

    ax.set_yticks(ticks)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))

    ax.grid(True)
    ax.legend()
    ax.title.set(fontfamily='monospace')