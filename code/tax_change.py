# import some libraries
import pandas as pd
from os import path

# import Bokeh libraries
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Select
from bokeh.charts import Line, Bar
from bokeh.charts.attributes import cat, ColorAttr, color
from bokeh.charts.operations import blend
from bokeh.layouts import column
from bokeh.io import output_file, show
from bokeh.models import BoxZoomTool, ResetTool, ResetTool, SaveTool
from bokeh.models import FuncTickFormatter
from bokeh.models import CustomJS, Slider

# load data as DataFrame
df = pd.read_csv("resources/dataset_tax_change.csv", decimal=",", encoding='utf-8-sig')

# extract the columns of interest
df_data = df[['""','Tax Units with Tax Cut', 'Tax Units with Tax Increase', 'Average Tax Change']]

# remove first and last rows
df_dropped=df_data.drop(df.index[[0,len(df_data['Tax Units with Tax Cut'])-1]])






