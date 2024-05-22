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
        prog="python polEmissivity_vs_latitude.py",
        description="Plot dual-polarized microwave emissivity as a function of latitude",
    )
    parser.add_argument("Hfile", type=str, help="GPKG file containing H-polarized Magellan emissivity data")
    parser.add_argument("Vfile", type=str, help="GPKG file containing V-polarized Magellan emissivity data")
    
    parser.add_argument(
        "-emisField",
        type=str,
        default="SURFACE_EMISSIVITY",
        help="Surface emissivity field name",
    )
    parser.add_argument(
        "-latField",
        type=str,
        default="RAD_FOOTPRINT_LATITUDE",
        help="Latitude field name",
    )
    parser.add_argument(
        "-incField",
        type=str,
        default="INCIDENCE_ANGLE",
        help="Incidence angle field name",
    )
    parser.add_argument(
        "-binSize",
        type=float,
        default=0.1,
        help="Size of latitude bins",
    )
    parser.add_argument(
        "-figFile",
        type=str,
        default="pol_emissivity.pdf",
        help="Filename for output PDF",
    )
    parser.add_argument(
        "-xaxis_min",
        type=float,
        default=-10.0,
        help="Leftmost value for the x axis",
    )
    parser.add_argument(
        "-xaxis_max",
        type=float,
        default=4.5,
        help="Rightmost value for the x axis",
    )
    parser.add_argument(
        "-yaxis_min",
        type=float,
        default=0.25,
        help="Bottommost value for the x axis",
    )
    parser.add_argument(
        "-yaxis_max",
        type=float,
        default=1.05,
        help="Topmost value for the x axis",
    )

    
    return parser.parse_args()


def main():
    args = cli()

    
    # Read data from gpkg and store in geodataframe
    Hlayer = fiona.listlayers(args.Hfile)[0]
    Vlayer = fiona.listlayers(args.Vfile)[0]
    ovda_v = gpd.read_file(args.Vfile, layer = Vlayer)
    ovda_h = gpd.read_file(args.Hfile, layer = Vlayer)

    # sort geodf by latitude
    dfh = pd.DataFrame(data = ovda_h).sort_values(args.latField)
    dfv = pd.DataFrame(data = ovda_v).sort_values(args.latField)

    # get min and max latitude and divide into bins
    min_thi = dfh[args.incField].min()
    max_thi = dfh[args.incField].max()
    bins = np.arange(min_thi, max_thi+0.05, args.binSize)
    dfv = dfv[(dfv[args.incField] >= min_thi) & (dfv[args.incField] <= max_thi)]


    # compute mean and standard deviation emissivity values binned by latitude
    dfh["BIN"] = pd.cut(dfh[args.incField], bins, right=True)
    dfh["MEAN_SURFACE_EMISSIVITY"] = dfh.groupby("BIN")[args.emisField].transform("mean") 
    dfh["STD_SURFACE_EMISSIVITY"] = dfh.groupby("BIN")[args.emisField].transform("std") 
    dfh["MEAN_INCIDENCE_ANGLE"] = dfh.groupby("BIN")[args.incField].transform("mean") 
    dfh["MEAN_RAD_FOOTPRINT_LATITUDE"] = dfh.groupby("BIN")[args.latField].transform("mean") 

    dfv["BIN"] = pd.cut(dfv[args.incField], bins, right=True)
    dfv["MEAN_SURFACE_EMISSIVITY"] = dfv.groupby("BIN")[args.emisField].transform("mean") 
    dfv["STD_SURFACE_EMISSIVITY"] = dfv.groupby("BIN")[args.emisField].transform("std") 
    dfv["MEAN_INCIDENCE_ANGLE"] = dfv.groupby("BIN")[args.incField].transform("mean") 
    dfv["MEAN_RAD_FOOTPRINT_LATITUDE"] = dfv.groupby("BIN")[args.latField].transform("mean")
    
    # plot the data
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(16, 8)


    matplotlib.rcParams['font.sans-serif'] = "Arial"
    matplotlib.rcParams['font.family'] = "sans-serif"

    hcolor = "#ae76a3"
    vcolor = "#90c987"
    hcoloravg = "#882e72"
    vcoloravg = "#4eb27f"

    dfh.plot.scatter(args.latField, args.emisField, ax=ax, s = 10, color = "white", edgecolor = hcolor)
    dfv.plot.scatter(args.latField, args.emisField, ax=ax, s = 10, color = "white", edgecolor = vcolor)

    ax.fill_between(dfh['MEAN_RAD_FOOTPRINT_LATITUDE'], dfh['MEAN_SURFACE_EMISSIVITY'] - dfh['STD_SURFACE_EMISSIVITY'], dfh['MEAN_SURFACE_EMISSIVITY'] + dfh['STD_SURFACE_EMISSIVITY'], color = hcolor, alpha = 0.5)
    ax.fill_between(dfv['MEAN_RAD_FOOTPRINT_LATITUDE'], dfv['MEAN_SURFACE_EMISSIVITY'] - dfv['STD_SURFACE_EMISSIVITY'], dfv['MEAN_SURFACE_EMISSIVITY'] + dfv['STD_SURFACE_EMISSIVITY'], color = vcolor, alpha = 0.5)

    dfv.plot.scatter('MEAN_RAD_FOOTPRINT_LATITUDE', 'MEAN_SURFACE_EMISSIVITY', ax=ax, s = 15, label="V-polarized",  marker = "x", color = vcoloravg)
    dfh.plot.scatter('MEAN_RAD_FOOTPRINT_LATITUDE', 'MEAN_SURFACE_EMISSIVITY', ax=ax, s = 15, label="H-polarized",  marker = "x", color = hcoloravg)



    ax.set_xlabel("Footprint center latitude", fontsize = 10)
    ax.set_ylabel("Polarized emissivity", fontsize = 10)
    ax.set_xlim(args.xaxis_min, args.xaxis_max)
    ax.set_ylim(args.yaxis_min, args.yaxis_max)
    ax.tick_params(axis="both", which="major", labelsize=10)
    ax.xaxis.set_major_formatter(StrMethodFormatter(u"{x:.0f} °"))
    ax.xaxis.labelpad = 8
    ax.yaxis.labelpad = 8
    ax.legend(fontsize = 10, loc = 2)

    plt.grid(visible=True, which='major', axis='both', linewidth=0.5)

    plt.savefig(args.figFile, bbox_inches='tight')
    plt.show()
    
    
main()