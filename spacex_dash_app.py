# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
                style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    html.Br(),
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site is selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # TASK 3: Add a slider to select payload range
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)},
        value=[0, 10000]
    ),
    
    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2 Callback function
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        success_counts = spacex_df['class'].value_counts().reset_index()
        success_counts.columns = ['Outcome', 'Count']
        fig = px.pie(success_counts, values='Count', names='Outcome', title='Launch Success and Failure (All Sites)')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['Outcome', 'Count']
        fig = px.pie(success_counts, values='Count', names='Outcome', title=f'Launch Success and Failure for {entered_site}')
        return fig

# TASK 4 Callback function
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id="payload-slider", component_property="value")
    ]
)
def get_scatter_plot(entered_site, payload_range):
    # Filter data based on selected payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # If 'ALL' sites are selected, use all rows in the dataframe
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',  # Payload mass on the X-axis
            y='class',  # Mission outcome (0 or 1) on the Y-axis
            color='Booster Version Category',  # Color points by Booster Version
            title='Launch Success vs Payload Mass for All Sites',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'}
        )
        return fig
    else:
        # Filter data for the selected launch site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        # Create scatter plot for the selected site
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',  # Payload mass on the X-axis
            y='class',  # Mission outcome (0 or 1) on the Y-axis
            color='Booster Version Category',  # Color points by Booster Version
            title=f'Launch Success vs Payload Mass for {entered_site}',
            labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'}
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
