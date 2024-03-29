# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import os

# Read the airline data into pandas dataframe

def find_path_to_file(file_name):
    pythonfile = 'spacex_launch_dash.csv'
    # if the file is present in current directory,
    # then no need to specify the whole location
    for root, dirs, files in os.walk(r'/home'): # change this if using windows or mac
        for name in files:
        
            # As we need to get the provided python file, 
            # comparing here like this
            if name == pythonfile: 
                return os.path.abspath(os.path.join(root, name))
    return None


local_path = find_path_to_file('spacex_launch_dash.csv')
spacex_df = pd.read_csv(local_path)
# spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

sites = spacex_df['Launch Site'].unique()
for site in sites:
    print(site)

dropdown_options=[{'label': 'All Sites', 'value': 'ALL'},
                  {'label': 'CCAFS LC-40', 'value': sites[0]},
                  {'label': 'VAFB SLC-4E', 'value': sites[1]},
                  {'label': 'KSC LC-39A', 'value': sites[2]},
                  {'label': 'CCAFS SLC-40', 'value': sites[3]}]

min_value = 0
max_value = 10000

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                html.Div([
                                    html.Label("Select Lanch Site:"),
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=dropdown_options,
                                        placeholder='Select a Launch Site',
                                        value='ALL',
                                        searchable=True
                                    )
                                ]), 
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                html.Div([
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                       100: '100',
                                                       500: '500',
                                                       1000: '1000',
                                                       2500: '2500',
                                                       5000: '5000',
                                                       7500: '7500',
                                                       10000: '10000'
                                                       },
                                                       value=[min_value, max_value])
                                ]),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                            ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    [Output(component_id='success-pie-chart', component_property='figure'),
     Output(component_id='success-payload-scatter-chart', component_property='figure')],
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')])
def get_charts(entered_site, slider_range):
    low, high = slider_range
    mask = (spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)
    fig_payload = px.scatter(spacex_df[mask], 
                                x='Payload Mass (kg)', 
                                y='class', 
                                color='Booster Version Category',
                                hover_data=['Payload Mass (kg)'],
                                )
    if entered_site == 'ALL':
        filtered_df_pie = spacex_df.groupby(spacex_df['Launch Site']).sum().reset_index()
        fig_pie_launches = px.pie(filtered_df_pie,
                                  values='class',
                                  names='Launch Site',
                                  title='Total Success Lanches by Site')
        fig_payload.update_layout(title=f'Total Payload (All Sites)')
        
    else:
        filtered_df_pie = spacex_df[['Launch Site','class']].value_counts().reset_index()
        fig_pie_launches = px.pie(filtered_df_pie[filtered_df_pie['Launch Site'] == entered_site], 
                                  values='count',
                                  names='class',
                                  title=f'Total Success Lanches for site {entered_site}')
        fig_payload.update_layout(title=f'Total Payload for site {entered_site}')
        

    return [fig_pie_launches, fig_payload]

# Run the app
if __name__ == '__main__':
    app.run_server()
