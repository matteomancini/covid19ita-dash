import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
from dash.dependencies import Input, Output, State

import json
import pandas as pd
import numpy as np
from urllib.request import urlopen
from shapely import geometry

app = dash.Dash(__name__)

server = app.server

geojson_url = 'https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_provinces.geojson'
dataset_url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv'

with urlopen(geojson_url) as response:
    prov = json.load(response)

data = pd.read_csv(dataset_url)

prov_coords={}
for n,p in enumerate(prov['features']):
    prov_code = p['properties']['prov_istat_code_num']
    if len(p['geometry']['coordinates'][0])>4:
        pts = p['geometry']['coordinates'][0]
    else:
        pts = p['geometry']['coordinates'][0][0]
    coords = [c[0] for c in geometry.Polygon(pts).centroid.coords.xy]
    coords.reverse()
    prov_coords[prov_code] = coords

month_dict = {'01': 'Gen', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'Mag', '06': 'Giu',
              '07': 'Lug', '08': 'Ago', '09': 'Set', '10': 'Ott', '11': 'Nov', '12': 'Dec'}
temp_label = 'In fase di aggiornamento'

data = data.replace('In fase di definizione/aggiornamento', temp_label)
data['data'] = [d.split('T')[0] for d in data['data']]

full_dates = data.data.unique()
full_dates.sort()
date_labels = [month_dict[f.split("-")[1]] + f.split("-")[2] for f in full_dates]

dates = {d: n for n, d in enumerate(full_dates)}
labels = {d: l for d, l in zip(full_dates, date_labels)}
data['date_index'] = data.apply(lambda ind: dates[ind['data']], axis=1)
data['date_labels'] = data.apply(lambda ind: labels[ind['data']], axis=1)

x_max = data['date_index'].max()
y_max = data['totale_casi'].max()

prov_codename = dict(zip(data.codice_provincia, data.denominazione_provincia))

data = data.sort_values(['denominazione_regione', 'denominazione_provincia', 'date_index'])

data['var'] = data['totale_casi'].diff()
data['varper'] = data['totale_casi'].pct_change() * 100
data = data.round(2)

for r in data[data.date_index == 0].index:
    data.at[r, 'var'] = np.nan
    data.at[r, 'varper'] = np.nan
data = data.replace(np.inf, np.nan)

for r in data[data.denominazione_provincia == temp_label].index:
    data.at[r, 'var'] = np.nan
    data.at[r, 'varper'] = np.nan

data['Latitudine'] = data.apply(lambda loc: prov_coords.get(loc['codice_provincia'],[np.nan])[0], axis=1)
data['Longitudine'] = data.apply(lambda loc: prov_coords.get(loc['codice_provincia'],[np.nan, np.nan])[1], axis=1)

data = data.rename(columns={'totale_casi': 'Totale casi', 'data': 'Data',
                            'var': 'Variazione (abs)',
                            'varper': 'Variazione (%)', 'denominazione_regione': 'Regione',
                            'denominazione_provincia': 'Provincia'})

measures = ['Totale casi', 'Variazione (abs)', 'Variazione (%)']

table_cols = ['Data', 'Regione', 'Provincia', 'Totale casi',
              'Variazione (abs)', 'Variazione (%)']

slider_marks = {int(i): {'label': day, 'style': {'transform': 'rotate(45deg)', 'font-size': '16px'}}
if (x_max - int(i)) % 3 == 0 else ''
                for i, day in zip(data['date_index'].unique(), data['date_labels'].unique())}

app.layout = html.Div([html.Div(html.H1('COVID-19 in Italia: i contagi per provincia'), className='title'),
                       html.Div(dcc.Dropdown(id='selectmeasure',
                                             options=[{'label': i, 'value': i} for i in measures],
                                             value=measures[0]), className='dropdown-container'),
                       html.Div([html.Div([dcc.Graph(id='prov-mapbox')], className='graph'),
                                 html.Div([dcc.Graph(id='plot',
                                                     figure=dict(
                                                         data=[],
                                                         layout=dict(
                                                             xaxis=dict(range=[0, x_max]),
                                                             yaxis=dict(range=[0, y_max]),
                                                             clickmode='event+select',
                                                             showlegend=True,
                                                             margin=dict(r=50, l=50,
                                                                         t=20, b=50),
                                                             padding=dict(r=0, l=0,
                                                                          t=0, b=0))))],
                                          className='graph')], className='graph-container'),
                       html.Div([dcc.Slider(
                           id='date-slider',
                           min=data['date_index'].min(),
                           max=data['date_index'].max(),
                           value=data['date_index'].max(),
                           marks=slider_marks,
                           step=None,
                           included=False,
                           updatemode='drag')],
                           className='slider-container'),
                       html.Div([dash_table.DataTable(
                           id='table', columns=[{'name': i, 'id': i} for i in table_cols],
                           data=[])], className='table')], className='main')


@app.callback(
    [Output('prov-mapbox', 'figure'),
     Output('table', 'data')],
    [Input('date-slider', 'value'),
     Input('selectmeasure', 'value')],
    [State('prov-mapbox', 'figure')])
def update_figure(selected_date, measure, figure):
    filtered_df = data[data.date_index == selected_date]
    table_data = filtered_df.to_dict('rows')
    filtered_df = filtered_df.dropna(subset=[measure])
    filtered_df[measure] = filtered_df[measure].abs()

    if figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        lat = 42
        lon = 13
        zoom = 4

    figure = px.scatter_mapbox(filtered_df, lat="Latitudine", lon="Longitudine", labels={},
                               mapbox_style='carto-positron',
                               hover_name='Provincia', hover_data=[measure], color=measure, size=measure,
                               color_continuous_scale=px.colors.cyclical.IceFire, size_max=20, zoom=5)

    figure["layout"]["margin"] = dict(r=0, l=0, t=0, b=0)
    figure["layout"]["mapbox"]["center"]["lat"] = lat
    figure["layout"]["mapbox"]["center"]["lon"] = lon
    figure["layout"]["mapbox"]["zoom"] = zoom

    return [figure, table_data]


@app.callback(
    Output('plot', 'figure'),
    [Input('prov-mapbox', 'clickData'),
     Input('plot', 'clickData'),
     Input('selectmeasure', 'value')],
    [State('plot', 'figure')]
)
def update_state_click(choro_click, plot_click, measure, plot):
    ctx = dash.callback_context

    y_min = data[data.Provincia != temp_label][measure].min()
    y_max = data[data.Provincia != temp_label][measure].max()
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'selectmeasure':
        plot['data'] = []
        plot['layout']['xaxis'] = dict(range=[0, x_max])
        plot['layout']['yaxis'] = dict(range=[y_min, y_max])

    displayed_provs = [p['name'] for p in plot['data']]
    if choro_click is not None:
        if choro_click['points'][0]['hovertext'] not in displayed_provs and \
                ctx.triggered[0]['prop_id'].split('.')[0] == 'prov-mapbox':
            df_prov = data[data.Provincia == choro_click['points'][0]['hovertext']].sort_values('date_index')
            plot['data'].append(
                dict(x=df_prov['date_labels'], y=df_prov[measure], name=df_prov['Provincia'].tolist()[0]))
            plot['layout']['yaxis'] = dict(range=[0, y_max])
    if plot_click is not None and ctx.triggered[0]['prop_id'].split('.')[0] == 'plot':
        plot['data'].pop(plot_click['points'][0]['curveNumber'])
    return plot


if __name__ == '__main__':
    app.run_server(debug=True)
