from dash import Dash, html, dash_table, dcc, callback, Output, Input, no_update
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc


def dashboardRt():
        
    # Initialize the app - incorporate a Dash Mantine theme
    external_stylesheets = [dmc.theme.DEFAULT_COLORS]
    app = Dash(__name__, external_stylesheets=external_stylesheets)

    # App layout
    app.layout = dmc.Container([
        dmc.Title('Crypto Analysis and Prediction App', color="blue", size="h3"),
    
        dmc.Grid([
            dmc.RadioGroup(
                [dmc.Radio(i, value=i) for i in  ['volumeUsd24Hr', 'marketCapUsd', 'priceUsd', '1_day prediction','3_days prediction','1_week prediction','1_month prediction']],
                id='my-dmc-radio-item',
                value='priceUsd',
                size="sm",
                mb=5,
                mt=5
            ),
            dmc.Col([
                dash_table.DataTable(id='table', page_size=12, style_table={'overflowX': 'auto'})
            ], span=12),
            dmc.Col([
                dcc.Graph(id='graph-placeholder')
            ], span=12),
        ]),
        dcc.Interval(
                id='interval-component',
                interval=1*1000, # in milliseconds
                n_intervals=0
        )
    ], fluid=True)

    # Add controls to build the interaction
    @callback(
        [Output(component_id='table', component_property='data'),
        Output(component_id='graph-placeholder', component_property='figure')],
        [Input(component_id='my-dmc-radio-item', component_property='value'),
        Input(component_id='interval-component', component_property='n_intervals')]
    )
    def update_graph(col_chosen, n):
    
        df = pd.read_csv('realtimeCrypto.csv')  # Move this line here to read the data at each interval
        # Filtrer le DataFrame pour les 20 premières cryptomonnaies
        df_top20 = df[df['rank'] <= 20]

        fig = px.histogram(df_top20, x='symbol', y=col_chosen)
        return df.to_dict('records'), fig

    # Run the App
    if __name__ == '__main__':
        app.run(debug=True)
