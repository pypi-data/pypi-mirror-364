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
    def __init__(self, type, data, legend=[]):
        self.type = type.lower().strip()
        self.data = data
        self.legend = legend

    def set_legend(self, legend):
        self.legend = legend
    
    def render(self, ax):
        print("  Render Plot")
        match self.type:
            case "line" | "lineplot":
                if len(self.data) > 1:
                    for i in range(1, len(self.data)):
                        plt.plot(self.data[0], self.data[i], color=getCol(i-1))
                        plt.legend(self.legend)
                else:
                    plt.plot(self.data[0])
            case "scatter" | "scatterplot":
                # Do scatter plot drawing here
                pass
