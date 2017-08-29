# importing some libraries
#importing some libraries
import pandas as pd
from os import path

#importing Bokeh libraries
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS, Slider, Text
from bkcharts import Line, Bar
from bkcharts.attributes import cat, ColorAttr, color
from bkcharts.operations import blend
from bokeh.layouts import column, layout
from bokeh.io import output_file, show
from bokeh.models import FuncTickFormatter
from bokeh.embed import components
from bokeh.resources import CDN


# define the years of interested
#years of interest
years=[2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

# load data as DataFrame and process data in an appropriate format
sources = {}
sources_df = {}

#load data as DataFrame
#prepare data

for year in years:
    sources = pd.DataFrame(pd.read_csv("bokehapp/static/14814_"+str(year)+"_difference_combined_bins.csv", decimal=",", encoding='utf-8-sig', header=1))
    sources=sources.rename(columns={'Unnamed: 0':'Intervals'})
    # drop the first and the last row (first row contains units and last one source)
    sources_dropped=sources.drop(sources.index[[0,len(sources['Tax Units with Tax Cut'])-1]])
    # extract the columns that we are interested in
    df_data = sources_dropped[['Intervals','Tax Units with Tax Cut', 'Tax Units with Tax Increase', 'Average Tax Change']]
    # assign the name "Intervals" to the first column
    intervals = df_data['Intervals']
    # change the format of the data to be float
    # and make the tax-cut data to be negative
    df_data['Tax Units with Tax Cut']= [x.replace(',', '.') for x in df_data['Tax Units with Tax Cut']]
    df_data['Tax Units with Tax Cut']=(-1)*df_data['Tax Units with Tax Cut'].astype(float)
    df_data['Tax Units with Tax Increase']= [x.replace(',', '.') for x in df_data['Tax Units with Tax Increase']]
    df_data['Tax Units with Tax Increase']=df_data['Tax Units with Tax Increase'].astype(float)
    # transform ColumnDataFrame to ColumnDataSource and assign the year
    sources_df['_' + str(year)] = ColumnDataSource(df_data)

# we can also create a corresponding dictionary_of_sources object, where the keys are integers and the values are the references to our ColumnDataSources from above:
dictionary_of_sources = dict(zip([x for x in years], ['_%s' % x for x in years]))

js_source_array = str(dictionary_of_sources).replace("'", "")

# we start from the first year of data, which is our source that drives the Bar (the other sources will be used later).
renderer_source = sources_df['_%s' % years[0]]

# add the year as text plot
text_source = ColumnDataSource({'year': ['%s' % years[0]]})
text = Text(x=0.8, y=600, text='year', text_font_size='20pt', text_color='#0569CE', text_alpha=1)

#add the Bar graph
p = Bar(renderer_source.data,
       label=cat(columns='Intervals', sort=False),
       values=blend('Tax Units with Tax Increase', 'Tax Units with Tax Cut', name='values', labels_name='vars'),
       tooltips=[('Value', '@values')], ylabel="Tax units with tax cut             Tax units with tax increase", stack=cat(columns='values', sort=False),
       color=color(columns='vars',
                      palette=['silver', 'orange'],
                      sort=True),
       bar_width=0.4, tools="pan,box_zoom, reset, save", plot_width=600, plot_height=500, logo=None,
       toolbar_sticky=False, legend=False)
p.xaxis.axis_label = 'Income [$ thousands]'
#add the text as a glyph
p.add_glyph(text_source, text)

# Create the "Average tax" figure
s1 = figure(plot_width=600, plot_height=200, title='Average Tax Change', tools="box_zoom, reset, save")
s1.toolbar.logo = None
s1.toolbar_sticky = False
s1.title.text_color = '#0569CE'
s1.xaxis.axis_label = 'Income [$ thousands]'

#take the data corresponding with the first year
avg_tax_change=renderer_source.data['Average Tax Change']

# form the line
line_x=[i for i in range(len(renderer_source.data['Intervals']))]

s1.line(line_x, avg_tax_change, line_color='#0569CE', line_width=2)
s1.circle(line_x, avg_tax_change, fill_color="white", size=8)

# Add the slider
code = """
    var year = slider.get('value'),
        sources = %s,
        new_source_data = sources[year].get('data');
    renderer_source.set('data', new_source_data);
    text_source.set('data', {'year': [String(year)]});
""" % js_source_array

callback = CustomJS(args=sources_df, code=code)
slider = Slider(start=years[0], end=years[-1], value=1, step=1, title="Year", callback=callback)
callback.args["renderer_source"] = renderer_source
callback.args["slider"] = slider
callback.args["text_source"] = text_source

# create output fileoutput_file("bar.html")
output_file("bar.html")
p_l = column(s1, p)
lay_out=layout([[p_l],[slider]])
#show(p_l)

js,div=components(lay_out)
cdn_js=CDN.js_files[0]
cdn_css=CDN.css_files[0]
