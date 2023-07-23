# Import required libraries
import pandas as pd
import dash
from dash import html    # custom code; original deprecated code: import dash_html_components as html
from dash import dcc     # custom code; original deprecated code: import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()    # custom note: to be used in task 3
min_payload = spacex_df['Payload Mass (kg)'].min()    # custom note: to be used in task 3

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={
                'textAlign': 'center',
                'color': '#503D36',
                'font-size': 40
            }
        ),
        
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {
                'label': 'All Sites',
                'value': 'ALL'
                },
                {
                'label': 'CCAFS LC-40',
                'value': 'CCAFS LC-40'
                },
                {
                'label': 'CCAFS SLC-40',
                'value': 'CCAFS SLC-40'
                },
                {
                'label': 'KSC LC-39A',
                'value': 'KSC LC-39A'
                },
                {
                'label': 'VAFB SLC-4E',
                'value': 'VAFB SLC-4E'
                },
            ],
            value='ALL',
            placeholder='Select a Launch Site',
            searchable=True
        ),
        html.Br(),
        
        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(
            dcc.Graph(
                id='success-pie-chart'
            )
        ),
        html.Br(),
        
        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=100,
            value=[
                min_payload,
                max_payload
            ],
            marks={
                0: '0',
                2500: '2500',
                5000: '5000',
                7500: '7500',
                10000: '10000'
            },
        ),
        
        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(
            dcc.Graph(
                id='success-payload-scatter-chart'
            )
        ),
    ],
    style={'font-family': 'sans-serif'}    # custom code: font style set to sans-serif
)

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(
        component_id='success-pie-chart',    #custom note: from html.Div(dcc.Graph(id='success-pie-chart')), above
        component_property='figure'
    ),
    Input(
        component_id='site-dropdown',    # custom note: from id='site-dropdown' above
        component_property='value'    # custom note: from options=[...'value':] above 
    )
)


def pie_chart(launch_site):
    sites_all = spacex_df[['Launch Site', 'class']]    # data
    # sites_all = launch_df.groupby('Launch Site').sum().reset_index()
    sites_one = sites_all[sites_all['Launch Site']==launch_site]    # custom note: filtering based on picked value
    sites_one = sites_one.value_counts().to_frame('count').reset_index()    # custom code: count 0/1 outcomes ('count')
    sites_one = sites_one.replace([0, 1], ['unsuccessful', 'successful'])    # custom code: (re)naming the outcome labels
    
    if launch_site == 'ALL':
        # If ALL sites are selected: render and return a pie chart graph to show the total success launches
        fig = px.pie(
            sites_all,
            names='Launch Site',
            values='class',
            hover_data=['Launch Site'],
            title='Total Success By Site'
        )
        return fig
    else:
        # # If a specific launch site is selected: return the outcomes piechart for a selected site
        fig = px.pie(
            sites_one,
            names='class',
            values='count',
            hover_data=['class'],
            title=f'Total Success Launches for site {launch_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(
        component_id='success-payload-scatter-chart',     # custom note: dcc.Graph(id='success-payload-scatter-chart')
        component_property='figure'
    ),
    [
        Input(
            component_id='site-dropdown',    # launch site
            component_property='value'        
        ),
        Input(
            component_id='payload-slider',    # payload range
            component_property='value'
        )
    ]
)


def scatter_plot(launch_site, payload_range):
    payload_lo, payload_hi = payload_range
    sites_all = spacex_df[['Launch Site', 'class', 'Payload Mass (kg)','Booster Version Category']]
    sites_all = sites_all[(sites_all['Payload Mass (kg)']>payload_lo) & (sites_all['Payload Mass (kg)']<payload_hi)]
    sites_one = sites_all[sites_all['Launch Site'] == launch_site]
    
    if launch_site == 'ALL':
        # If ALL sites are selected: render a scatter plot to display all values for variable Payload Mass (kg) and variable class            
        fig = px.scatter(
            sites_all,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            hover_data=['Booster Version Category'],
            title = f'Correlation between Payload and Success for all Sites ({payload_lo}-{payload_hi}Kg)'
        )
        return fig
    
    else:
        # If a specific launch site is selected: render a scatter chart to show values Payload Mass (kg) and class for the selected site
        pass
        fig = px.scatter(
            sites_one,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            hover_data=['Booster Version Category'],
            title = f'Correlation between Payload and Success for site {launch_site} ({payload_lo}-{payload_hi}Kg)'
        )
        return fig        
    

# Run the app
if __name__ == '__main__':
    app.run_server()