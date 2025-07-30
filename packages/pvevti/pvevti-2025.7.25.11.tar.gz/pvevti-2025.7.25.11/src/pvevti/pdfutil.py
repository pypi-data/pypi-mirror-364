"""
A library of PDF utilities to interface with matplotlib's PDF engine.
For help, explore the readme and the docs markdown files in the package source.
"""

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import pandas as pd
import os
from pvevti import genutil as gu

plt.rcParams['text.usetex'] = False

cols = [
    "#00677F",
    "#303030",
    "#7CBCCA",
    "#1B6527",
    "#B4B4B4",
    "#651B26"
]

default_config = {
    "docTitle": "Document Title", "docSubTitle": "Document Subtitle",
    "pages": [
        {
            "pageName": "Conditions",
            "plots": [
                {
                    "plotTitle": "Altitude",
                    "plotType" : "dualline",
                    "xData"    : "cumulative distance",
                    "yData"    : ["gps_z", "gps_speed"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "Ambient Conditions",
                    "plotType" : "dualline",
                    "xData"    : "cumulative distance",
                    "yData"    : ["amb_t", "amb_p"],
                    "filterLength": 120
                }
            ]
        },
        {
            "pageName": "Basic Analytics",
            "plots": [
                {
                    "plotTitle": "Speed and Time",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["GPS_speed_mph"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "CAC and Condensor Package",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["amb_t", "cac_2_2_air_ti", "cond_2_2_air_ti"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "Turbocharger and CAC Pressure Performance (Compressor)",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["AMB_P", "ICPI", "ICPO"],
                    "filterLength": 180
                },
                {
                    "plotTitle": "Turbocharger and CAC Pressure Performance (Turbine)",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["amb_p", "expo", "ats_pi", "ats_po"],
                    "filterLength": 180
                }
            ]
        },
        {
            "pageName": "Engine Performance",
            "plots": [
                {
                    "plotTitle": "Engine Speeds",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["EngSpd_Cval_PT", "FanSpd_Cval_PT", "OutShaftSpd_Cval_PT"],
                    "filterLength": 20
                },
                {
                    "plotTitle": "Engine Torque",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["ebm_eng_act_trq", "tbf_trq_friction", "can_trq_dem"],
                    "filterLength": 20
                },
                {
                    "plotTitle": "Fuel Rail",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["rpg_p_rail_act", "rpg_p_rail_des"],
                    "filterLength": 20
                },
                {
                    "plotTitle": "Mass Flow",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["sp_intake_mass", "sp_air_mass", "sp_egr_mass", "spe_des_air_mass"]
                }
            ]
        },
        {
            "pageName": "Primary Thermal Analysis",
            "plots": [
                {
                    "plotTitle": "ACM",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["ACM_FRT_ST", "acm_bck_st", "acm_hrn_brk_zt_st"],
                    "filterLength": 20
                },
                {
                    "plotTitle": "Aftertreatment System",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["ATS_DPS_ST", "ATS_HRN_AFT_ZT_ST", "ATS_HRN_COND_ST", "ATS_HRN_ELBOW_ST", "ATS_HRN_ZT_TOP_ST"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "Ambient and Intake",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["amb_T", "cti", "icto"],
                    "filterLength": 360
                },
                {
                    "plotTitle": "Radiator Package",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["rad_2_2_air_ti", "rad_2_2_air_to", "rad_4_2_air_ti", "rad_4_2_air_to"],
                    "filterLength": 360
                }
            ]
        },
        {
            "pageName": "Continued Thermal Analysis",
            "plots": [
                {
                    "plotTitle": "SCU Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["soot_scu_st", "soot_scu_air_t", "soot_scu_conn_st"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "NOX Raw Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["nox_raw_hex_st", "nox_raw_ecu_st", "nox_raw_conn_st"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "NOX Mid Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["nox_out_hex_st", "nox_out_ecu_st", "nox_out_conn_st"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "NOX Out Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["nox_out_hex_st", "nox_out_ecu_st", "nox_out_conn_st"],
                    "filterLength": 40
                },
                {
                    "plotTitle": "HVAC",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["HVAC_SetTemp_Stat", "cab_breath_l_air_t", "cab_breath_r_air_t"],
                    "filterLength": 40
                }
            ]
        },
        {
            "pageName": "Pre-SCR Overview",
            "plots": [
                {
                    "plotTitle": "Pre-SCR Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["PRE_SCR_ST_1", "PRE_SCR_ST_10", 
                                  "PRE_SCR_ST_2", "PRE_SCR_ST_3", 
                                  "PRE_SCR_ST_4", "PRE_SCR_ST_5", 
                                  "PRE_SCR_ST_6", "PRE_SCR_ST_7", 
                                  "PRE_SCR_ST_8", "PRE_SCR_ST_9"],
                    "filterLength": 160
                }
            ]
        },
        {
            "pageName": "Status",
            "plots": [
                {
                    "plotTitle": "TMC Status",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["tmc_status"]
                },
                {
                    "plotTitle": "AM OPC Status",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["am_opc_status"]
                },
                {
                    "plotTitle": "Fan Status",
                    "plotType" : "dualline",
                    "xData"    : "t",
                    "yData"    : ["fan_status_mcm", "clto"]
                }
            ]
        },
        {
            "pageName": "Extras",
            "plots": [
                {
                    "plotTitle": "Air Compressor and Dryer Performance",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["air_comp_ti", "air_comp_to", "air_dryer_ti", "air_dryer_to"],
                    "filterLength": 3
                },
                {
                    "plotTitle": "Air Compressor Status",
                    "plotType" : "line",
                    "xData"    : "t",
                    "yData"    : ["air_on"]
                },
                {
                    "plotTitle": "Power-Speed Plot",
                    "plotType" : "scatter",
                    "xData"    : "EngRPM_Cval_CPC3",
                    "yData"    : ["HP_CALCULATED"]
                },
                {
                    "plotTitle": "Torque-Speed Plot",
                    "plotType" : "scatter",
                    "xData"    : "EngRPM_Cval_CPC3",
                    "yData"    : ["isp_trq_current"]
                }
            ]
        }
    ]
}

def getCol(i, colList=cols):
    """
    For Color parsing; returns the hex color for any provided integer.
    Cycles through available colors as defined in the pvevti.pdfutil.cols list.
    """
    return colList[((i+1) % len(colList)-1)]

class PDFdoc:
    def __init__(self, name="Unnamed PDF"):
        """
        Create an empty PDF document object with a name attribute. Name may but does not need to include '.pdf'.
        """
        self.pages = []
        if ".pdf" not in name:
            self.name = name + ".pdf"
        else:
            self.name = name

    def add_page(self, page):
        """
        Attach a Page object to the PDF document object.
        """
        self.pages.append(page)

    def save(self, location="."):
        """
        Saves the PDF document object as a PDF file on the system. 
        """
        path = location+self.name
        print("Save {}".format(path))
        with PdfPages(path) as pdf:
            for page in self.pages:
                page.save_to(pdf)

class Page:
    def __init__(self, title="Unnamed Page"):
        """
        Create an empty Page object with a title attribute.
        """
        self.items = []
        self.title = title

    def set_title(self, title):
        """
        Override plot title. No return
        """
        self.title = title

    def add_plot(self, item):
        """
        Add a plot object to the page. No return
        """
        self.items.append(item)

    def save_to(self, pdfObj):
        """
        Save page to PDF object. No return
        """
        fig, ax_hidden = plt.subplots(figsize=(8.5, 11))
        ax_hidden.axis('tight')
        ax_hidden.axis('off')
        gs = GridSpec(len(self.items), 1, hspace=0.1+max(0.2, len(self.items)*0.2-0.3))
        subax = []
        fig.suptitle(self.title)
        print(" Save Page {}".format(self.title))
        for (i, item) in enumerate(self.items):
            subax.append(fig.add_subplot(gs[i]))
            item.render()
        pdfObj.savefig(fig)
        plt.close(fig)

class Plot:
    def __init__(self, type="line", data=[], legend = [], xlabel = "", ylabel = "", columns = [], infer_names = False, title="Unnamed Plot", filterLength=0):
        """
        Create a Plot object with type, data, legend, xlabel, ylabel, columns, and infer_names properties. 
          type: str in ["line", "scatter"]
          data: nested list with column-wise data
          legend: list of str to override the legend display
          xlabel, ylabel: str to override respective axis label
          columns: raw column data from a pd df to infer axis and legend names
          infer_names: bool to permit axis and legend name inference
        
        Changing values post-init should be done with the respective methods.
        """
        self.type = type.lower().strip()
        self.data = data
        self.legend = legend
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.columns = list(columns)
        self.grid = 'x'
        self.title= title
        self.filterLength = filterLength
        if infer_names:
            self.infer_names()
    
    def __str__(self):
        return("Plot item\n  (type: {}, legend: {}, \n   xlabel: {}, ylabel: {},\n   grid: {})".format(self.type, self.legend, self.xlabel, self.ylabel, self.grid))

    def infer_names(self):
        """
        Passive method to infer names for signals and axis based on a provided columnset. 
        The plot should have a defined list of column names, *including* the x-axis (usually "t[s]")
        No return
        """
        if self.columns != []:
            names = []
            units = []
            for column in self.columns:
                if "[" in column:
                    names.append(column.split("[")[0])
                    units.append(column.split("[")[1].split("]")[0])
                else:
                    names.append(column)
                    units.append("")
        if len(names) > 2:
            self.legend = names[1:]
            self.xlabel = names[0] + "  [" + units[0] + "]"
            self.ylabel = units[1]
        elif len(names) == 2:
            self.legend = []
            self.xlabel = names[0] + "  [" + units[0] + "]"
            self.ylabel = names[1] + "  [" + units[1] + "]"
        else:
            self.legend = []
            self.xlabel = ""
            self.ylabel = ""
        if self.filterLength != 0:
            self.title = self.title + " [EMA{}]".format(self.filterLength)

    def no_legend(self):
        """
        Clears the legend from the plot
        """
        self.legend = []

    def set_legend(self, legend: list):
        """
        Sets the legend of the plot. Legend must be a list of strings.
        """
        self.legend = legend
    
    def no_xlabel(self):
        """
        Clears the xlabel from the plot.
        """
        self.xlabel = ""
    
    def set_xlabel(self, label: str):
        """
        Sets the xlabel of the plot. Label must be a string.
        """
        self.xlabel = label

    def no_ylabel(self):
        """
        Clears the ylabel from the plot.
        """
        self.ylabel = ""
    
    def set_ylabel(self, label: str):
        """
        Sets the ylabel of the plot. Label must be a string.
        """
        self.ylabel = label

    def set_grid(self, grid):
        """
        Set the plot's grid style to the provided; may be 'x', 'y', 'both', or 'none'.
        """
        if grid in ['none', 'both', 'x', 'y']:
            self.grid = grid
        else:
            self.grid = 'none'

    def no_grid(self):
        """
        Clears the grid from the plot.
        """
        self.grid = 'none'

    def render(self):
        """
        Renders the plot with the provided settings. 
        Change all plot settings prior to calling Plot.render().
        """
        #print("  Render Plot")

        # Render plot based on type
        match self.type:

            # Line plot
            case "line" | "lineplot":
                if len(self.data) > 1:
                    for i in range(1, len(self.data)):
                        if i <= len(cols):
                            plt.plot(self.data[0], self.data[i], color=getCol(i-1)+"D0")
                        else:
                            plt.plot(self.data[0], self.data[i], color=getCol(i-1), linestyle='--')
                else:
                    plt.plot(self.data[0], self.data[1], color=getCol(0))

            # Scatter plot
            case "scatter" | "scatterplot":
                for i in range(1, len(self.data)):
                    if i <= len(cols):
                        if len(self.data[0]) > 16000:
                            app = "28"
                        elif len(self.data[0]) > 8000:
                            app = "50"
                        elif len(self.data[0]) > 4000:
                            app = "8c"
                        else:
                            app = "af"
                        plt.scatter(self.data[0], self.data[i], color=getCol(i-1)+app, s=3)
                    else:
                        plt.scatter(self.data[0], self.data[i], color=getCol(i-1), s=3)
                pass
            case "dual" | "dualline":
                ax1 = plt.gca()
                ax2 = ax1.twinx()
                pos = ax2.get_position()
                ax2.set_position([pos.x0, pos.y0, pos.width * 0.95, pos.height])
                ax1.plot(self.data[0], self.data[1], color=getCol(0))
                for i in range(2, len(self.data)):
                    ax2.plot(self.data[0], self.data[i], color=getCol(i-1))
                ax1.set_ylabel(self.columns[1], color=getCol(0))
                ax2.set_ylabel(self.columns[2], color=getCol(1))
                ax1.tick_params(axis="y", colors=getCol(0), labelcolor=getCol(0))
                ax2.tick_params(axis="y", colors=getCol(1), labelcolor=getCol(1))
                ax1.grid(True, 'major', 'y', color=getCol(0))
                ax2.grid(True, 'major', 'y', color=getCol(1), linestyle="--")
                ax1.set_xlabel(self.xlabel)
                # ax1.set_xticks(range(int(min(self.data[0])), int(max(self.data[0])), int((max(self.data[0])-min(self.data[0]))/8)))
        
        plt.title(self.title)
        if self.type not in ['dual', 'dualline']:
            if self.legend != [] and len(self.data) > 2:
                plt.legend(self.legend, loc="upper left", fontsize=8)
            if self.xlabel != "":
                plt.xlabel(self.xlabel)
            if self.ylabel != "":
                plt.ylabel(self.ylabel)
            if self.grid != 'none':
                plt.grid(visible=True, axis=self.grid, which='major')
            else:
                plt.grid(visible=False)
                

def fixConfig(config_old: dict):
    config = config_old.copy()
    if "docTitle" not in config:
        config["docTitle"] = "UNNAMED DOCUMENT TITLE"
    if "docSubTitle" not in config:
        config["docSubTitle"] = "UNNAMED DOCUMENT SUBTITLE"
    if "pages" not in config:
        config["pages"] = []
    for page in config["pages"]:
        if "pageName" not in page:
            page["pageName"] = "UNNAMED PAGE NAME"
        if "plots" not in page:
            page["plots"] = []
        for plot in page["plots"]:
            if "plotTitle" not in plot:
                plot["plotTitle"] = "UNNAMED PLOT"
            if "plotType" not in plot:
                plot["plotType"] = ""
            if "xData" not in plot:
                plot["xData"] = ""
            if "yData" not in plot:
                plot["yData"] = [""]
            elif not isinstance(plot["yData"], list):
                plot["yData"] = [plot["yData"]]
            if "filterLength" not in plot or plot["filterLength"] == False:
                plot["filterLength"] = 0
            elif plot["filterLength"] == True:
                plot["filterLength"] = 30
            else:
                plot["filterLength"] = int(plot["filterLength"])
    return config


def createDocument(data: pd.DataFrame, config: dict, save_path: str=os.path.expanduser("~")+"\\"):
    """
    Creates, manages, and saves a document given a dataset and configuration file.
    Check documentation for information on config structure. 
    If no save path is specified, defaults to the user's home directory (C:\\Users\\USERNAME\\)
    """
    cfg = fixConfig(config)
    # print("\n-- Metadata --\n\n Document Title: {}\n Document Subtitle: {}".format(cfg['docTitle'], cfg['docSubTitle']))
    # print("\n\n-- Pages --")
    cd_document = PDFdoc(cfg['docTitle'])

    for (i, page) in enumerate(cfg['pages']):
        # print("\n- Page "+str(i+1))
        # print("  Name: {}\n  Number of plots: {}".format(page['pageName'], len(page['plots'])))
        cd_page = Page("[{}] ".format(cfg['docSubTitle'])+page['pageName'])

        for (x, plot) in enumerate(page['plots']):
            # print("\n--  Plot "+str(x+1))
            # print("    Title: {}\n    Type: {}".format(plot['plotTitle'], plot['plotType']))
            # print("    x data: '{}'\n    y data: {}\n    Filter Length: {}".format(plot['xData'], 
            # plot['yData'], plot['filterLength']))
            toPlot = gu.formatData(data, signal_x=plot['xData'], signals_y=plot['yData'])
            if plot['filterLength'] > 0:
                toPlot = gu.applyFilter(toPlot, span=plot['filterLength'])
            cd_plot = Plot(type=plot["plotType"], data=toPlot, 
                           columns=(gu.parseNames(data.columns, plot['xData'])+gu.parseNames(data.columns, plot['yData'])), 
                           title=plot['plotTitle'], filterLength=plot['filterLength'])
            cd_plot.infer_names()
            cd_plot.set_grid('y')
            cd_page.add_plot(cd_plot)
            del cd_plot
        
        cd_document.add_page(cd_page)
        del cd_page

    cd_document.save(save_path)
    print("")

