# Plot polarized emissivity as shown in Figure 8
import argparse
import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter, StrMethodFormatter
from mpl_toolkits.mplot3d import Axes3D

import pandas as pd
import geopandas as gpd
import fiona

def cli():
    parser = argparse.ArgumentParser(
        prog="python emissivity_vs_elevation.py",
        description="Plot Magellan microwave emissivity as a function of planetary radius",
    )
    parser.add_argument("file", type=str, help="GPKG file containing Magellan emissivity data")
    
    parser.add_argument(
        "-emisField",
        type=str,
        default="SURFACE_EMISSIVITY",
        help="Surface emissivity field name",
    )
    parser.add_argument(
        "-prField",
        type=str,
        default="AVERAGE_PLANETARY_RADIUS",
        help="Planetary radius field name",
    )
   
    parser.add_argument(
        "-figFile",
        type=str,
        default="emissivity_vs_pr.pdf",
        help="Filename for output PDF",
    )
    parser.add_argument(
        "-xaxis_min",
        type=float,
        default=0.15,
        help="Leftmost value for the x axis",
    )
    parser.add_argument(
        "-xaxis_max",
        type=float,
        default=0.9,
        help="Rightmost value for the x axis",
    )
    parser.add_argument(
        "-yaxis_min",
        type=float,
        default=6051,
        help="Bottommost value for the x axis",
    )
    parser.add_argument(
        "-yaxis_max",
        type=float,
        default=6058.0,
        help="Topmost value for the x axis",
    )
    parser.add_argument(
        "-color",
        type=str,
        default="k",
        help="Plot color",
    )

    
    return parser.parse_args()


def main():
    args = cli()

    
    # Read data from gpkg and store in geodataframe
    layer = fiona.listlayers(args.file)[0]
    data = gpd.read_file(args.file, layer = layer)
    
    # plot the data
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(3.5,3.5)

    matplotlib.rcParams['font.sans-serif'] = "Arial"
    matplotlib.rcParams['font.family'] = "sans-serif"

    ax.scatter(data[args.emisField], data[args.prField], color = args.color, s = 5, alpha=0.7)

    ax.set_xlabel("Emissivity", fontsize = 10)
    ax.set_ylabel("Surface elevation (km)", fontsize = 10)
    ax.set_xlim(args.xaxis_min, args.xaxis_max)
    ax.set_ylim(args.yaxis_min, args.yaxis_max)
    ax.tick_params(axis="both", which="major", labelsize=10)
    ax.xaxis.labelpad = 15
    ax.yaxis.labelpad = 15


    lg = ax.legend(fontsize = 10)
    for lh in lg.legendHandles: 
        lh.set_alpha(1)

    plt.grid(visible=True, which='major', axis='both', linewidth=0.5)
    plt.savefig(args.figFile, format="pdf", bbox_inches='tight')
    plt.show()
    
    
main()