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
            "pageName": "Page One",
            "plots": [
                {
                    "plotTitle": "Example Plot",
                    "plotType" : "line",
                    "xData"    : "x_axis_data",
                    "yData"    : ["signal_name_1","signal_name_2", "signal_name_3"],
                    "filterLength": 60
                },
                {
                    "plotTitle": "Example Plot 2",
                    "plotType" : "line",
                    "xData"    : "x_axis_data",
                    "yData"    : ["signal_name_4", "signal_name_5"],
                    "filterLength": 300
                }
            ]
        },
        {
            "pageName": "Page Two",
            "plots": [
                {
                    "plotTitle": "Example Plot 3",
                    "plotType" : "scatter",
                    "xData"    : "t",
                    "yData"    : ["signal_name_6", "signal_name_7", "signal_name_8", "signal_name_9"]
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
        gs = GridSpec(len(self.items), 1, hspace=0.1+max(0.2, len(self.items)*0.15-0.3))
        subax = []
        fig.suptitle(self.title)
        print(" Save Page {}".format(self.title))
        for (i, item) in enumerate(self.items):
            subax.append(fig.add_subplot(gs[i]))
            item.render()
        pdfObj.savefig(fig)
        plt.close(fig)

class Plot:
    def __init__(self, type="line", data=[], legend = [], xlabel = "", ylabel = "", columns = [], infer_names = False):
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
        print("  Render Plot")
        match self.type:
            case "line" | "lineplot":
                if len(self.data) > 1:
                    for i in range(1, len(self.data)):
                        plt.plot(self.data[0], self.data[i], color=getCol(i-1))
                        if self.legend != []:
                            plt.legend(self.legend, loc="upper left")
                        if self.xlabel != "":
                            plt.xlabel(self.xlabel)
                        if self.ylabel != "":
                            plt.ylabel(self.ylabel)
                        if self.grid != 'none':
                            plt.grid(axis=self.grid, which='major')
                        else:
                            plt.grid(visible=False)
                else:
                    plt.plot(self.data[0])
            case "scatter" | "scatterplot":
                # Do scatter plot drawing here
                pass

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
    print("\n-- Metadata --\n\n Document Title: {}\n Document Subtitle: {}".format(cfg['docTitle'], cfg['docSubTitle']))
    print("\n\n-- Pages --")
    cd_document = PDFdoc(cfg['docTitle'])

    for (i, page) in enumerate(cfg['pages']):
        print("\n- Page "+str(i+1))
        print("  Name: {}\n  Number of plots: {}".format(page['pageName'], len(page['plots'])))
        cd_page = Page("[{}] ".format(cfg['docSubTitle'])+page['pageName'])

        for (x, plot) in enumerate(page['plots']):
            print("\n--  Plot "+str(x+1))
            print("    Title: {}\n    Type: {}".format(plot['plotTitle'], plot['plotType']))
            print("    x data: '{}'\n    y data: {}\n    Filter Length: {}".format(plot['xData'], plot['yData'], plot['filterLength']))
            toPlot = gu.formatData(data, signal_x=plot['xData'], signals_y=plot['yData'])
            if plot['filterLength'] > 0:
                toPlot = gu.applyFilter(toPlot, span=plot['filterLength'])
            cd_plot = Plot(type=plot["plotType"], data=toPlot, columns=([plot["xData"]]+gu.parseNames(data.columns, plot['yData'])))
            cd_plot.infer_names()
            cd_page.add_plot(cd_plot)
            del cd_plot
        
        cd_document.add_page(cd_page)
        del cd_page

    cd_document.save(save_path)
    print("")
