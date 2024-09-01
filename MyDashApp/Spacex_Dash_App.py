# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import requests
import io

# Read the airline data into pandas dataframe
URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
response = requests.get(URL)
dataset_csv = io.StringIO(response.text)
spacex_df = pd.read_csv(dataset_csv)

# Map 'class' to 'Landing Outcome'
spacex_df['Landing Outcome'] = spacex_df['class'].map({1: 'Success', 0: 'Failure'})

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
server = app.server

# Dropdown options
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': site, 'value': site} for site in launch_sites]
dropdown_options.insert(0, {'label': 'All Sites', 'value': 'ALL'})

# Define custom color palette
custom_colors = ['#D9D9D9', '#9B9AD4', '#6361D4', '#0B06DB', '#009BB1']

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#FFFFFF',
                                               'font-size': 40, 'font-family': 'Kadwa, sans-serif'}),
                                # Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=dropdown_options,
                                            value='ALL',
                                            placeholder="Select a launch site",
                                            searchable=True),
                                html.Br(),

                                # Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):", style={'font-family': 'Kadwa, sans-serif', 'color': '#FFFFFF'}),
                                # Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload,
                                                max=max_payload,
                                                step=100,  # Adjust the step as needed
                                                marks={i: f'{i}' for i in range(int(min_payload), int(max_payload)+1, 1000)},
                                                value=[min_payload, max_payload]),

                                # Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart'))
                                ])

# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Filter for successful launches
        success_df = spacex_df[spacex_df['Landing Outcome'] == 'Success']
        # Aggregate to count successful launches per site
        launch_counts = success_df['Launch Site'].value_counts().reset_index()
        launch_counts.columns = ['Launch Site', 'Success_Count']

        # Create a pie chart with aggregated data
        fig = px.pie(launch_counts, values='Success_Count', names='Launch Site',
                     title='Total Successful Landings per Site',
                     color_discrete_sequence=custom_colors)
    else:
        # If a specific site is selected, show Success vs. Failed counts for that site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, names='Landing Outcome',
                     title=f"Success vs. Failed Landings for site {entered_site}",
                     color_discrete_sequence=custom_colors)

    fig.update_layout({
        'paper_bgcolor': '#002343',
        'plot_bgcolor': '#002343',
        'font': {'family': 'Kadwa, sans-serif', 'color': '#FFFFFF'},  # Set the font family and text color here
        'title': {'x': 0.5}  # Center the title
    })
    return fig

# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# Callback for the scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter(entered_site, payload_range):
    # Filter the DataFrame based on the selected site and payload range
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) & 
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    # Create a scatter plot
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='Landing Outcome', 
                     color='Booster Version Category',
                     title=f"Payload vs. Outcome for {entered_site}",
                     color_discrete_sequence=custom_colors)

    fig.update_layout({
        'paper_bgcolor': '#002343',
        'plot_bgcolor': '#002343',
        'font': {'family': 'Kadwa, sans-serif', 'color': '#FFFFFF'},  # Set the font family and text color here
        'yaxis': {'zerolinecolor': '#00396E', 'gridcolor': '#00396E'},  # Adjusted for new column
        'xaxis': {'zerolinecolor': '#00396E', 'gridcolor': '#00396E'},
        'title': {'x': 0.5}  # Center the title
    })
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
