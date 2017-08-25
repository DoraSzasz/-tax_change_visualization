# importing some libraries
#importing some libraries
import pandas as pd
from os import path

#importing Bokeh libraries
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bkcharts import Line, Bar
from bkcharts.attributes import cat, ColorAttr, color
from bkcharts.operations import blend
from bokeh.layouts import column
from bokeh.io import output_file, show
from bokeh.models import FuncTickFormatter
from bokeh.embed import components
from bokeh.resources import CDN


# load data as DataFrame
df = pd.read_csv("/Users/rcc/Documents/Projects/Rick/Demo_Django/mysite/bokehapp/static/dataset_tax_change.csv", decimal=",", encoding='utf-8-sig')

# extract the columns that we are interested in
df_data = df[['Unnamed: 0', 'Tax Units with Tax Cut', 'Tax Units with Tax Increase', 'Average Tax Change']]

# drop the first and the last row (first row contains units and last one source)
# we may have to skip this step when working with data coming from server
df_dropped = df_data.drop(df.index[[0, len(df_data['Tax Units with Tax Cut']) - 1]])

# change the format of the data to be float
# and make the tax-cut data to be negative
df_dropped['Tax Units with Tax Cut'] = [x.replace(',', '.') for x in df_dropped['Tax Units with Tax Cut']]
df_dropped['Tax Units with Tax Cut'] = (-1) * df_dropped['Tax Units with Tax Cut'].astype(float)
df_dropped['Tax Units with Tax Increase'] = [x.replace(',', '.') for x in df_dropped['Tax Units with Tax Increase']]
df_dropped['Tax Units with Tax Increase'] = df_dropped['Tax Units with Tax Increase'].astype(float)

# assign the name "Intervals" to the first column
names = df_dropped.columns.tolist()
names[names.index('Unnamed: 0')] = 'Intervals'
df_dropped.columns = names

# transform ColumnDataFrame to ColumnDataSource
tax_increase = ColumnDataSource(pd.DataFrame(df_dropped["Tax Units with Tax Increase"]))
tax_cut = ColumnDataSource(pd.DataFrame(df_dropped["Tax Units with Tax Cut"]))
cds_df_dropped = ColumnDataSource(df_dropped)

# the plots with the bars
p = Bar(df_dropped,
        label=cat(columns='Intervals', sort=False),
        values=blend('Tax Units with Tax Increase', 'Tax Units with Tax Cut', name='values', labels_name='vars'),
        tooltips=[('Value', '@values')], ylabel="Tax units with tax cut             Tax units with tax increase",
        stack=cat(columns='values', sort=False),
        color=color(columns='vars',
                    palette=['silver', 'orange'],
                    sort=True),
        bar_width=0.4, tools="pan,box_zoom, reset, save", plot_width=600, plot_height=450,
        toolbar_sticky=False, legend=False)
p.xaxis.axis_label = 'Income [$ thousands]'
p.toolbar.logo = None

values = blend('Tax Units with Tax Increase', 'Tax Units with Tax Cut', name='values', labels_name='vars')

# the line plot for avrage tax change
s1 = figure(plot_width=600, plot_height=200, title='Average Tax Change', tools="box_zoom, reset, save")
s1.toolbar.logo = None
s1.toolbar_sticky = False
s1.title.text_color = '#0569CE'
s1.xaxis.axis_label = 'Income [$ thousands]'

avg_tax_change = df_dropped['Average Tax Change']
line_x = [i for i in range(len(df_dropped['Intervals']))]

s1.line(line_x, avg_tax_change, line_color='#0569CE', line_width=2)
s1.circle(line_x, avg_tax_change, fill_color="white", size=8)

# keep the original label names
label_dict = {}
for i, s in enumerate(df_dropped['Intervals']):
    label_dict[i] = s

s1.xaxis.formatter = FuncTickFormatter(code="""
    var labels = %s;
    return labels[tick];
""" % label_dict)

# create output fileoutput_file("bar.html")
output_file("bar.html")
p_l = column(s1, p)
#show(p_l)

js,div=components(p_l)
cdn_js=CDN.js_files[0]
cdn_css=CDN.css_files[0]
