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
from bokeh.models import ColumnDataSource, Select, HoverTool
from bokeh.models.widgets import Div
from bokeh.plotting import figure
from bokeh.tile_providers import STAMEN_TERRAIN, STAMEN_TONER, STAMEN_TERRAIN_RETINA, CARTODBPOSITRON_RETINA, \
    CARTODBPOSITRON, CARTODB_DARK_MATTER
import sqlite3

# connect to database
conn = sqlite3.connect("adresses_31.db")

df = pd.read_sql('SELECT * FROM census_merge', conn)
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

unique_geburtsort = df.geburtsort_x.unique().tolist()
unique_geburtsort = list(filter(None.__ne__, unique_geburtsort))

# Webmercator Values for Berlin (estimated)
BERLIN = x_range, y_range = ((1470000, 1530000), (6860000, 6930000))

plot_width = int(750)
plot_height = int(plot_width // 1.2)


def get_dataset(src, category, category_value):
    ds = src.query('{} == "{}"'.format(category, category_value))
    return ColumnDataSource(data=ds)

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
    options = dict(line_color=None, fill_color='violet', size=3, alpha=0.6)
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


def update_plot_deportationsziel(attrname, old, new):
    deportation = deportation_select.value
    plot.title.text = "Menschen, die nach {} deportiert wurden".format(deportation)

    src = get_dataset(df, 'deportationsziel', deportation)
    source.data.update(src.data)


def update_plot_deportationsdatum(attrname, old, new):
    deportationsdatum = deportation_datum_select.value
    plot.title.text = "Menschen, die am {} deportiert wurden".format(deportationsdatum)

    src = get_dataset(df, 'deportationsdatum', deportationsdatum)
    source.data.update(src.data)


def update_plot_todesort(attrname, old, new):
    todesort = todesort_select.value
    plot.title.text = "Menschen, die in {} gestorben sind".format(todesort)

    src = get_dataset(df, 'todesort', todesort)
    source.data.update(src.data)


def update_plot_emigration(attrname, old, new):
    emigration = emigration_select.value
    plot.title.text = "Menschen, die nach {} emigriert sind".format(emigration)

    src = get_dataset(df, 'emigration_1', emigration)
    source.data.update(src.data)


def update_plot_schicksal(attrname, old, new):
    schicksal = schicksal_select.value
    plot.title.text = "Schicksal: {}".format(schicksal)

    src = get_dataset(df, 'schicksal', schicksal)
    source.data.update(src.data)


def update_plot_inhaftierung(attrname, old, new):
    inhaftierung = inhaftierung_select.value
    plot.title.text = "Menschen, die in {} inhaftiert waren".format(inhaftierung)

    src = get_dataset(df, 'inhaftierung_1', inhaftierung)
    source.data.update(src.data)


def update_plot_geburtsort(attrname, old, new):
    geburtsort = geburtsort_select.value
    plot.title.text = "Menschen, die in {} geboren sind".format(geburtsort)

    src = get_dataset(df, 'geburtsort_x', geburtsort)
    source.data.update(src.data)


deportation_select = Select(value='None', title='Deportationsziel', options=sorted(unique_deporationsziel))
deportation_datum_select = Select(value='None', title='Deportationsdatum', options=sorted(unique_deporationsdatum))
todesort_select = Select(value='None', title='Todesort', options=sorted(unique_todesort))
emigration_select = Select(value='None', title='Emigration', options=sorted(unique_emigration))
schicksal_select = Select(value='None', title='Schicksal', options=sorted(unique_schicksal))
inhaftierung_select = Select(value='None', title='Inhaftierungsort', options=sorted(unique_inhaftierung))
geburtsort_select = Select(value='None', title='Geburtsort', options=sorted(unique_geburtsort))

# just a standard value
# TODO: find a better start value
source = get_dataset(df, 'bezirk', 'Lichtenberg')
plot = make_plot(source)

div = Div(text="""<p align="justify"><h2>Deportationen aus Berlin</h2>Bereits ab Mitte Oktober 1941 begann die systematische Deportation von Juden aus Deutschland. Die aus dem Deutschen Reich verschleppten Juden wurden nicht direkt am Zielort umgebracht. Im November 1941 stellte man nach sieben Transporten nach Minsk die Deportation kurzzeitig ein, nahm diese jedoch im Mai 1942 schon wieder auf. Bevor einzelne Transporte 1942 zwar schon in den Vernichtungslagern wie Sobibor oder Maly Trostinez endeten, wurden die meisten von ihnen aber zunächst unter widrigen Lebensbedingungen in Ghettos oder Arbeitslagern einquartiert. Viele starben vor Ort, andere wiederum wurden später in die Vernichtungslager weitertransportiert und ermordet. Ab Ende 1942 fuhren die Züge auch ohne Umweg nach Auschwitz-Birkenau.

Der von der Gestapo bezeichnete „Straftransport“ mit 201 Berliner Jüdinnen und Juden verließ im Juni 1942 auch Berlin. In dem »16. Berliner Osttransportes« befanden sich namhafte Angehörige der »Reichsvereinigung« wie beispielsweise die Gemeindevertreterinnen Cora Berliner (1890 – 1942) und Paula Fürst (1894 – 1942) sowie der Gemeindevertreter Arthur Lilienthal (1899 – 1942). Die bisherige Forschung ist der Annahme, dass jener Berliner (Teil-)Transport via Königsberg nach Minsk gelangte. In Königsberg wurden zeitgleich 465 Königsberger Jüdinnen und Juden zusammengetrieben, die ebenfalls nach Minsk deportiert werden sollten. Am 24. Juni 1942 verließ der Transport mit der Zugnummer »Da 40« Königsberg und erreichte Minsk zwei Tage später, am 26. Juni 1942. In diesem Transport befanden sich mit hoher Wahrscheinlichkeit auch die 201 Berliner Jüdinnen und Juden. Überlebende dieses Transportes gibt es keine.</p>
<h2>Die Reichsvereinigung der Juden</h2>Bis 1933 waren Juden nicht unbedingt organisiert. Zwar gab es jüdische Sport- und Kulturvereine und selbstverständlich die religiösen Gemeinden. Überall dort war man natürlich freiwillig Mitglied, aufgrund des Glaubens oder der persönlichen Interessen. Das sollte sich jedoch nach der Machtübergabe an die Nazis ändern.

Im Spätsommer 1933 hatten fast alle bedeutenden jüdischen Organisationen sowie alle größeren Kultusgemeinden eine landesweite gemeinsame Interessenvertretung gegründet, die “Reichsvertretung der Deutschen Juden”. Ihr Präsident wurde der Berliner Rabbiner Leo Baeck. Ihre Ziele waren die Unterstützung des Zusammenhalts, die jüdische Selbsthilfe und – in realistischer Einschätzung der kommenden Verhältnisse – die Vorbereitung der Emigration nach Palästina. Es folgten mehrere erzwungene Namenswechsel (“Reichsvertretung …”, “Reichsverband …”, “Reichsvereinigung der Juden in Deutschland”).  

In den Jahren 1939 bis 1941 versuchten die Funktionäre der Reichsvereinigung, möglichst vielen Juden bei der Flucht aus Deutschland behilflich zu sein. Am 4. Juli 1939 wurde die Reichsvereinigung der Juden in Deutschland durch die 10. Verordnung zum Reichsbürgergesetz von den nationalsozialistischen Machthabern übernommen und hatte ab September 1939 den Anweisungen der Gestapo zu folgen. Alle Personen, die nach den Nürnberger Gesetzen als Juden galten, wurden in der Reichsvereinigung unweigerlich eingegliedert und mussten Pflichtbeiträge entrichten. Mit Ausnahme derjenigen, die in „previligierten Mischehen“ leben; diese mussten sich zunächst noch nicht anschließen. Ab 1942 wurden sie jedoch Zwangsmitglied, sofern sie einem jüdischen Religionsverband angehörten. 1943 wurden uneingeschränkt alle Personen, die nach nationalsozialistischer Definition Juden waren, beitragspflichtig in der Reichsvereinigung organisiert. Die Hauptaufgabe der Reichsvereinigung bestand darin, die Zurückgebliebenen zu versorgen. Zugleich musste die Reichsvereinigung bei den Deportationen mitwirken, versuchte aber dabei, das Geschehen zu verzögern und Härten abzumildern. Die Reichsvereinigung organisierte auch Schulunterricht, da jüdische Kinder keine staatlichen Schulen mehr besuchen durften. Sie organisierte Kleiderkammern und brachte obdachlose Mitglieder in sogenannten “Judenhäusern” unter. 

Für die leitenden Mitglieder der Reichsvereinigung begann ein tragischer Weg, der meistens mit ihrem eigenen Tod endete: Zunächst versuchten sie noch möglichst vielen Juden die Auswanderung zu ermöglichen und die Auswirkungen des sich immer mehr steigernden Terrors abzumildern. Nach dem Auswanderungsverbot vom Herbst 1941 und dem Beginn der systematischen Deportationen ließen sie sich – immer in der Hoffnung, die Lage der Betroffenen noch verbessern zu können – auf eine Art Kooperation mit den Nazibehörden ein und übernahmen konkrete Aufgaben bei der Vorbereitung und Durchführung der Deportationen, bis sie selbst verschleppt und zumeist ermordet wurden.</p>""",
          width=700, height=300)

deportation_select.on_change('value', update_plot_deportationsziel)
deportation_datum_select.on_change('value', update_plot_deportationsdatum)
todesort_select.on_change('value', update_plot_todesort)
emigration_select.on_change('value', update_plot_emigration)
schicksal_select.on_change('value', update_plot_schicksal)
inhaftierung_select.on_change('value', update_plot_inhaftierung)
geburtsort_select.on_change('value', update_plot_geburtsort)

controls = widgetbox(
    [geburtsort_select, inhaftierung_select, schicksal_select, emigration_select, deportation_datum_select,
     deportation_select, todesort_select], width=500)

text = row([div])

curdoc().add_root(layout([plot, controls], [text]))
curdoc().title = "CdV 2017 Visualisierung jüdischen Lebens"
