from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['text.usetex'] = False

cols = [
    "#00677F",
    "#303030",
    "#1C4048",
    "#B4B4B4",
    "#7CBCCA"
]

def getCol(i):
    return cols[((i+1) % len(cols)-1)]

class PDFdoc:
    def __init__(self, name):
        self.pages = []
        if ".pdf" not in name:
            self.name = name + ".pdf"
        else:
            self.name = name

    def add_page(self, page):
        self.pages.append(page)

    def save(self, location="."):
        path = location+self.name
        print("Save {}".format(path))
        with PdfPages(path) as pdf:
            for page in self.pages:
                page.save_to(pdf)

class Page:
    def __init__(self, title=""):
        self.items = []
        self.title = title

    def set_title(self, title):
        self.title = title

    def add_plot(self, item):
        self.items.append(item)

    def save_to(self, pdfObj):
        fig, ax_hidden = plt.subplots(figsize=(8.5, 11))
        ax_hidden.axis('tight')
        ax_hidden.axis('off')
        gs = GridSpec(len(self.items), 1)
        subax = []
        fig.suptitle("REPORT: " + self.title)
        print(" Save Page {}".format(self.title))
        for (i, item) in enumerate(self.items):
            subax.append(fig.add_subplot(gs[i]))
            item.render(subax[i])
        pdfObj.savefig(fig)
        plt.close(fig)
        pass

class Plot:
    def __init__(self, type, data, legend = [], xlabel = "", ylabel = "", columns = [], infer_names = False):
        self.type = type.lower().strip()
        self.data = data
        self.legend = legend
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.columns = list(columns)
        self.grid = 'x'
        if infer_names:
            self.infer_names()

    def infer_names(self):
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
        if grid:
            self.grid = grid
        else:
            self.grid = 'none'

    def no_grid(self):
        self.grid = 'none'

    
    def render(self, ax):
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
