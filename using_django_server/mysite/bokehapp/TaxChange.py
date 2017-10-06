# importing some libraries
import pandas as pd
from os import path
from math import pi

# importing Bokeh libraries
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS, Slider, LabelSet
# from bkcharts import Line, Bar
# from bkcharts.attributes import cat, ColorAttr, color
# from bkcharts.operations import blend
from bokeh.layouts import column, layout
from bokeh.io import output_file, show
from bokeh.models import FuncTickFormatter, FactorRange
from bokeh.embed import components
from bokeh.resources import CDN
pd.options.mode.chained_assignment = None


# define the years of interested
# years of interest
years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

# load data as DataFrame and process data in an appropriate format
sources = {}
sources_df = {}

# load data as DataFrame
# prepare data

for year in years:
    sources = pd.DataFrame(pd.read_csv("bokehapp/static/14814_"+str(year)+"_difference_combined_bins.csv", decimal=",", encoding='utf-8-sig', header=1))
    sources = sources.rename(columns={'Unnamed: 0': 'Intervals'})
    # drop the first and the last row (first row contains units and last one source)
    sources_dropped = sources.drop(sources.index[[0,len(sources['Tax Units with Tax Cut'])-1]])
    # extract the columns that we are interested in
    df_data = sources_dropped[['Intervals','Tax Units with Tax Cut', 'Tax Units with Tax Increase', 'Average Tax Change']]
    # assign the name "Intervals" to the first column
    intervals = df_data['Intervals']
    # change the format of the data to be float
    # and make the tax-cut data to be negative
    df_data['Tax Units with Tax Cut'] = [x.replace(',', '.') for x in df_data['Tax Units with Tax Cut']]
    df_data['Tax Units with Tax Cut'] = (-1)*df_data['Tax Units with Tax Cut'].astype(float)
    df_data['Tax Units with Tax Increase'] = [x.replace(',', '.') for x in df_data['Tax Units with Tax Increase']]
    df_data['Tax Units with Tax Increase'] = df_data['Tax Units with Tax Increase'].astype(float)
    # transform ColumnDataFrame to ColumnDataSource and assign the year
    sources_df['_' + str(year)] = ColumnDataSource(df_data)

# we can also create a corresponding dictionary_of_sources object, where the
# keys are integers and the values are the references to our ColumnDataSources from above:
dictionary_of_sources = dict(zip([x for x in years], ['_%s' % x for x in years]))

js_source_array = str(dictionary_of_sources).replace("'", "")

# we start from the first year of data, which is our source that drives the Bar
# (the other sources will be used later).
renderer_source = sources_df['_%s' % years[0]]

# add the year as text plot
# text_source = ColumnDataSource({'year': ['%s' % years[0]]})
# text = Text(x=0.8, y=600, text='year', text_font_size='20pt',
#             text_color='#0569CE', text_alpha=1)
# label_source = ColumnDataSource({'year': ['%s' % years[0]]})
# label = Label(x=70, y=70, text='year', border_line_alpha=1, x_units='screen',
#               y_units='screen', render_mode='css')
# label = LabelSet(x=60, y=370, x_units='screen', y_units='screen',
#                  text='%s' % years[0], render_mode='css',
#                  border_line_color='black', border_line_alpha=0.0,
#                  background_fill_color='white', background_fill_alpha=1.0)

label_source = ColumnDataSource({'text': [str(years[0])]})
label = LabelSet(x=0.5, y=600, text='text', level='glyph', source=label_source,
                 render_mode='canvas', text_font_size='50pt', text_color='#0569CE')

# add the Bar graph
p = figure(plot_width=600, plot_height=500, y_range=[-1000, 1000],
           x_range=FactorRange(*renderer_source.data['Intervals']),
           tools="box_zoom, reset, save")
p.toolbar.logo = None

# import pdb; pdb.set_trace()

p.vbar(top='Tax Units with Tax Increase', x='Intervals', width=0.4,
       color='orange', source=renderer_source)
p.vbar(top='Tax Units with Tax Cut', x='Intervals', width=0.4, color='silver',
       source=renderer_source)
p.xaxis.axis_label = 'Income [$ thousands]'
p.xaxis.major_label_orientation = pi/4
p.yaxis.axis_label = 'Tax Units with Tax Cut            Tax Units with Tax Increase'
p.yaxis.major_label_orientation = "vertical"

# add the text as a glyph
p.add_layout(label)

# Create the "Average tax" figure
s1 = figure(plot_width=600, plot_height=200, title='Average Tax Change',
            tools="box_zoom, reset, save")
s1.toolbar.logo = None
s1.title.text_color = '#0569CE'
s1.xaxis.axis_label = 'Income [$ thousands]'

# take the data corresponding with the first year
avg_tax_change = renderer_source.data['Average Tax Change']

# form the line
line_x = [i for i in range(len(renderer_source.data['Intervals']))]

s1.line(line_x, avg_tax_change, line_color='#0569CE', line_width=2)
s1.circle(line_x, avg_tax_change, fill_color="white", size=8)

# Add the slider
code = """
    var sources = %s;
    debugger;
    var year = slider.value;
    var new_source_data = sources[year].data;
    var data = renderer_source.data;

    for (i = 0; i < renderer_source.data['index'].length; i++){
        data['Average Tax Change'][i] = new_source_data['Average Tax Change'][i];
        data['Intervals'][i] = new_source_data['Intervals'][i];
        data['Tax Units with Tax Cut'][i] = new_source_data['Tax Units with Tax Cut'][i];
        data['Tax Units with Tax Increase'][i] = new_source_data['Tax Units with Tax Increase'][i];
    }

    label_source.data['year'] = String(year);

    label_source.change.emit();
    renderer_source.change.emit();

    debugger;
""" % js_source_array

callback = CustomJS(args=sources_df, code=code)
slider = Slider(start=years[0], end=years[-1], value=years[0], step=1,
                title="Year", callback=callback)
callback.args["renderer_source"] = renderer_source
callback.args["slider"] = slider
callback.args["label_source"] = label_source

# create output fileoutput_file("bar.html")
output_file("bar.html")
p_l = column(s1, p)
lay_out = layout([[p_l], [slider]])

js, div = components(lay_out)
cdn_js = CDN.js_files[0]
cdn_css = CDN.css_files[0]
widget_js = CDN.js_files[1]
widget_css = CDN.css_files[1]



# # define the years of interested
# # years of interest
# years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
#
# # load data as DataFrame and process data in an appropriate format
# sources = {}
# sources_df = {}
#
# # load data as DataFrame
# # prepare data
#
# for year in years:
#     sources = pd.DataFrame(pd.read_csv("bokehapp/static/14814_"+str(year)+"_difference_combined_bins.csv", decimal=",", encoding='utf-8-sig', header=1))
#     sources = sources.rename(columns={'Unnamed: 0': 'Intervals'})
#     # drop the first and the last row (first row contains units and last one source)
#     sources_dropped = sources.drop(sources.index[[0,len(sources['Tax Units with Tax Cut'])-1]])
#     # extract the columns that we are interested in
#     df_data = sources_dropped[['Intervals','Tax Units with Tax Cut', 'Tax Units with Tax Increase', 'Average Tax Change']]
#     # assign the name "Intervals" to the first column
#     intervals = df_data['Intervals']
#     # change the format of the data to be float
#     # and make the tax-cut data to be negative
#     df_data['Tax Units with Tax Cut'] = [x.replace(',', '.') for x in df_data['Tax Units with Tax Cut']]
#     df_data['Tax Units with Tax Cut'] = (-1)*df_data['Tax Units with Tax Cut'].astype(float)
#     df_data['Tax Units with Tax Increase'] = [x.replace(',', '.') for x in df_data['Tax Units with Tax Increase']]
#     df_data['Tax Units with Tax Increase'] = df_data['Tax Units with Tax Increase'].astype(float)
#     # transform ColumnDataFrame to ColumnDataSource and assign the year
#     sources_df['_' + str(year)] = ColumnDataSource(df_data)
#
# # we can also create a corresponding dictionary_of_sources object, where the
# # keys are integers and the values are the references to our ColumnDataSources from above:
# dictionary_of_sources = dict(zip([x for x in years], ['_%s' % x for x in years]))
#
# js_source_array = str(dictionary_of_sources).replace("'", "")
#
# # we start from the first year of data, which is our source that drives the Bar
# # (the other sources will be used later).
# renderer_source = sources_df['_%s' % years[0]]
#
# # add the year as text plot
# text_source = ColumnDataSource({'year': ['%s' % years[0]]})
# text = Text(x=0.8, y=600, text='year', text_font_size='20pt',
#             text_color='#0569CE', text_alpha=1)
#
# # add the Bar graph
# p = figure(plot_width=600, plot_height=500)
# p.vbar(label=cat(columns='Intervals', sort=False),
#        values=blend('Tax Units with Tax Increase', 'Tax Units with Tax Cut',
#                     name='values', labels_name='vars'),
#        tooltips=[('Value', '@values')],
#        ylabel="Tax units with tax cut             Tax units with tax increase",
#        stack=cat(columns='values', sort=False),
#        color=color(columns='vars',
#                    palette=['silver', 'orange'],
#                    sort=True),
#        bar_width=0.4, tools="pan, box_zoom, reset, save",
#        logo=None, toolbar_sticky=False, legend=False,
#        source=renderer_source)
# p.xaxis.axis_label = 'Income [$ thousands]'
# # add the text as a glyph
# p.add_glyph(text_source, text)
#
# # Create the "Average tax" figure
# s1 = figure(plot_width=600, plot_height=200, title='Average Tax Change',
#             tools="box_zoom, reset, save")
# s1.toolbar.logo = None
# s1.toolbar_sticky = False
# s1.title.text_color = '#0569CE'
# s1.xaxis.axis_label = 'Income [$ thousands]'
#
# # take the data corresponding with the first year
# avg_tax_change = renderer_source.data['Average Tax Change']
#
# # form the line
# line_x = [i for i in range(len(renderer_source.data['Intervals']))]
#
# s1.line(line_x, avg_tax_change, line_color='#0569CE', line_width=2)
# s1.circle(line_x, avg_tax_change, fill_color="white", size=8)
#
# # Add the slider
# code = """
#     var year = slider.value;
#     var sources = %s;
#     var new_source_data = sources[year].data;
#     var data = renderer_source.data;
#
#     debugger
#
#         for (i = 0; i < renderer_source.data['index'].length; i++){
#             data['Average Tax Change'][i] = new_source_data['Average Tax Change'][i];
#             data['Intervals'][i] = new_source_data['Intervals'][i];
#             data['Tax Units with Tax Cut'][i] = new_source_data['Tax Units with Tax Cut'][i];
#             data['Tax Units with Tax Increase'][i] = new_source_data['Tax Units with Tax Increase'][i];
#         }
#
#     text_source.data['year'] = String(year);
#
#     text_source.change.emit();
#     renderer_source.change.emit();
#
#     debugger;
# """ % js_source_array
#
# callback = CustomJS(args=sources_df, code=code)
# slider = Slider(start=years[0], end=years[-1], value=1, step=1, title="Year",
#                 callback=callback)
# callback.args["renderer_source"] = renderer_source
# callback.args["slider"] = slider
# callback.args["text_source"] = text_source
#
# # create output fileoutput_file("bar.html")
# output_file("bar.html")
# p_l = column(s1, p)
# lay_out = layout([[p_l], [slider]])
#
# js, div = components(lay_out)
# cdn_js = CDN.js_files[0]
# cdn_css = CDN.css_files[0]
