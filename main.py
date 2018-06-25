"""
Interactive map for exploring the Memorialbook from Bundesarchiv and the Minority Census from 1939
This python script is best used in bokeh directory format.

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

IMPORTANT: The script uses a customized tile_providers.py file from bokeh to use the DARK_MATTER tiles
from CartoDB. As long it is not merged with bokeh have that in mind.

Change in tile_providers.py is as follows:

 @property
    def CARTODB_DARK_MATTER(self):
        from bokeh.models.tiles import WMTSTileSource
        return WMTSTileSource(
            url='http://tiles.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
            attribution=self._CARTO_ATTRIBUTION
        )

Todo:
    * Optimize speed
    * Optimize layout
    * find standard values
    * can it made responsive?

Ideas:
    * Add synagoges and other important points

"""


import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, layout
from bokeh.models import ColumnDataSource, Select, HoverTool, TableColumn
from bokeh.models.widgets import Div, DataTable
from bokeh.plotting import figure
from bokeh.tile_providers import STAMEN_TERRAIN, STAMEN_TONER, STAMEN_TERRAIN_RETINA, CARTODBPOSITRON_RETINA, \
    CARTODBPOSITRON, CARTODB_DARK_MATTER
import sqlite3
import copy

# connect to database
conn = sqlite3.connect("adresses_31.db")

df = pd.read_sql('SELECT * FROM census_merge WHERE x_mercator_census IS NOT NULL', conn)
df = df[['vorname', 'nachname', 'geboren', 'geburtsdatum', 'geburtsort_x', 'adresse', 'zusatz', 'bezirk',
         'x_mercator_census', 'y_mercator_census', 'inhaftierung_1', 'emigration_1', 'emigration_1_zeitpunkt',
         'deportationsziel', 'deportationsdatum', 'schicksal', 'todesort', 'todesdatum']]
df['x_mercator_census'] = df['x_mercator_census'].astype('float')
df['y_mercator_census'] = df['y_mercator_census'].astype('float')
# filter dataframe for unique values - needed for options menu
unique_deporationsziel = df.deportationsziel.unique().tolist()
unique_deporationsziel = list(filter(None.__ne__, unique_deporationsziel))

unique_deporationsdatum = df.deportationsdatum.unique().tolist()
unique_deporationsdatum = list(filter(None.__ne__, unique_deporationsdatum))

unique_todesort = df.todesort.unique().tolist()
unique_todesort = list(filter(None.__ne__, unique_todesort))

unique_emigration = df.emigration_1.unique().tolist()
unique_emigration = list(filter(None.__ne__, unique_emigration))

unique_schicksal = df.schicksal.unique().tolist()
unique_schicksal = list(filter(None.__ne__, unique_schicksal))

unique_inhaftierung = df.inhaftierung_1.unique().tolist()
unique_inhaftierung = list(filter(None.__ne__, unique_inhaftierung))

unique_bezirk = df.bezirk.unique().tolist()
unique_bezirk = list(filter(None.__ne__, unique_bezirk))

# Webmercator Values for Berlin (estimated)
BERLIN = x_range, y_range = ((1470000, 1530000), (6860000, 6930000))

plot_width = int(750)
plot_height = int(plot_width // 1.2)

def get_dataset(src, category_values):
    query_list = []
    v_dict = copy.deepcopy(category_values)
    for category in category_values.keys():
        if category_values[category] == 'None':
            v_dict.pop(category)

    keys = list(v_dict.keys())
    for i in range(0, len(keys)):
        if i+2 > len(keys):
            query_list.append('{} == "{}"'.format(keys[i], v_dict[keys[i]]))
        else:
            query_list.append('{} == "{}" & '.format(keys[i], v_dict[keys[i]]))

    if len(query_list) <= 0:
        ds = src.query('geburtsort_x == "None"')
    else:
        ds = src.query('{}'.format(''.join(query_list)))
    return ColumnDataSource(data=ds)

#def get_dataset(src, category, category_value):
#    if category_value is not None:
#        ds = src.query('{} == "{}"'.format(category, category_value))
#        return ColumnDataSource(data=ds)
#    else:
#        ds = src.query('{} == "{}"'.format(category, category_value))
#        return ColumnDataSource(data=ds)

# function for a standard plot
def base_plot(tools='hover,pan,wheel_zoom,reset,save', plot_width=plot_width, plot_height=plot_height, **plot_args):
    p = figure(tools=tools, plot_width=plot_width, plot_height=plot_height,
               x_range=x_range, y_range=y_range, outline_line_color=None,
               min_border=0, min_border_left=0, min_border_right=0,
               min_border_top=0, min_border_bottom=0, **plot_args)

    p.axis.visible = False
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    return p


# Creates a plot and adds hover tooltips. For some reason when used in Directory format, the hover tips are empty.
# Custom hovertool works.
def make_plot(source):
    options = dict(line_color=None, fill_color='#ffd800', size=3, alpha=0.6)
    p = base_plot()
    p.add_tile(CARTODB_DARK_MATTER)
    p.circle(x='x_mercator_census', y='y_mercator_census', source=source, **options)
    p.select_one(HoverTool).tooltips = '''
    <div>
        <span style="font-size: 10px; color: #0099FF;">Name:</span>
        <span style="font-size: 10px; color: #000000;">@nachname</span>
     </div>
     <div>
        <span style="font-size: 10px; color: #0099FF;">Vorname:</span>
        <span style="font-size: 10px; color: #000000;">@vorname</span>
     </div>
     <div>
        <span style="font-size: 10px; color: #0099FF;">Geburtsdatum:</span>
        <span style="font-size: 10px; color: #000000;">@geburtsdatum</span>
     </div>
     <div>
        <span style="font-size: 10px; color: #0099FF;">Todesdatum:</span>
        <span style="font-size: 10px; color: #000000;">@todesdatum</span>
     </div>
     <div>
        <span style="font-size: 10px; color: #0099FF;">Adresse:</span>
        <span style="font-size: 10px; color: #000000;">@adresse</span>
     </div>
     '''
    # p.select_one(HoverTool).tooltips = [
    #     ("Name", "@name"),
    #     ("Vorname", "@vorname"),
    #     ("Geburtsdatum", "@geburtsdatum"),
    #     ("Todesdatum", "@todesdatum"),
    #     ("Adresse", "@adresse")
    # ]
    return p

def get_values_from_selects():
    values_dict = {'deportationsziel': deportation_select.value, 'deportationsdatum': deportation_datum_select.value,
                   'todesort': todesort_select.value, 'emigration_1': emigration_select.value, 'schicksal': schicksal_select.value,
                   'inhaftierung': inhaftierung_select.value, 'bezirk': bezirk_select.value}

    return values_dict


def update_plot(attrname, old, new):
    values = get_values_from_selects()
    src = get_dataset(df, values)
    source.data.update(src.data)


deportation_select = Select(value='None', title='Deportationsziel', options=sorted(unique_deporationsziel))
deportation_datum_select = Select(value='None', title='Deportationsdatum', options=sorted(unique_deporationsdatum))
todesort_select = Select(value='None', title='Todesort', options=sorted(unique_todesort))
emigration_select = Select(value='None', title='Emigration', options=sorted(unique_emigration))
schicksal_select = Select(value='None', title='Schicksal', options=sorted(unique_schicksal))
inhaftierung_select = Select(value='None', title='Inhaftierungsort', options=sorted(unique_inhaftierung))
bezirk_select = Select(value='None', title='Bezirk', options=sorted(unique_bezirk))

# just a standard value
# TODO: find a better start value
source = get_dataset(df, get_values_from_selects())
plot = make_plot(source)

deportation_select.on_change('value', update_plot)
deportation_datum_select.on_change('value', update_plot)
todesort_select.on_change('value', update_plot)
emigration_select.on_change('value', update_plot)
schicksal_select.on_change('value', update_plot)
inhaftierung_select.on_change('value', update_plot)
bezirk_select.on_change('value', update_plot)

columns = [TableColumn(field=Ci, title=Ci) for Ci in df.columns]
data_table = DataTable(source=source, width=1200, columns=columns, height=280)

controls = widgetbox(
    [bezirk_select, inhaftierung_select, schicksal_select, emigration_select, deportation_datum_select,
     deportation_select, todesort_select], width=500)

curdoc().add_root(layout([plot, controls], [data_table]))
curdoc().title = "CdV 2017 Visualisierung jüdischen Lebens"
