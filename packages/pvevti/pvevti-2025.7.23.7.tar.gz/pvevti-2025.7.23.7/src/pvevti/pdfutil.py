from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

plt.rcParams['text.usetex'] = False

cols = [
    "#00677F",
    "#303030",
    "#7CBCCA",
    "#1B6527",
    "#B4B4B4",
    "#651B26"
]

def getCol(i):
    """
    For Color parsing; returns the hex color for any provided integer.
    Cycles through available colors as defined in the pvevti.pdfutil.cols list.
    """
    return cols[((i+1) % len(cols)-1)]

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
        gs = GridSpec(len(self.items), 1, max(0, len(self.items)*0.15-0.45))
        subax = []
        fig.suptitle("REPORT: " + self.title)
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
