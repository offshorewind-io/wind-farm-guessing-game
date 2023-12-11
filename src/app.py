import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State, ALL
import csv
import random
import plotly.graph_objs as go
import pandas as pd


wind_farm_data = pd.read_csv('./src/wind_farms.csv')
wind_farm_names = wind_farm_data['Name'].unique()


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
#server = app.server

# Function to create a new game challenge
def create_challenge():
    correct_choice = random.choice(wind_farm_names)
    wrong_choices = random.sample([wf for wf in wind_farm_names if wf != correct_choice], 2)
    options = [correct_choice] + wrong_choices
    return correct_choice, options

def create_option_buttons(options):
    option_buttons = [dbc.Button(option, className="me-1", outline=True, color="primary", id={'type': 'option-button', 'index': i}, n_clicks=0) for i, option in enumerate(options)]
    random.shuffle(option_buttons)
    return option_buttons

app.layout = html.Div([
    html.H1("Wind Farm Guessing Game"),
    dcc.Graph(id='wind-farm-layout'),
    html.Div(id='name-options'),
    html.Div(id='score-display'),
    html.Div(id='game-result'),
    html.Div(id='final-score', style={'display': 'none'}),
    dbc.Button('Restart Game', color="secondary", outline=True, className="me-1", id='restart-button', n_clicks=0, style={'display': 'none'})
],
style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'height': '100vh'
    }

)


@app.callback(
    [Output('wind-farm-layout', 'figure'),
     Output('name-options', 'children'),
     Output('score-display', 'children'),
     Output('game-result', 'children'),
     Output('final-score', 'children'),
     Output('restart-button', 'style')],
    [Input({'type': 'option-button', 'index': ALL}, 'n_clicks'),
     Input('restart-button', 'n_clicks')],
    [State('final-score', 'children')]
)
def update_game(option_n_clicks, restart_n_clicks, score):

    new_correct_choice, new_options = create_challenge()
    ctx = dash.callback_context

    # Determine which button was clicked
    button_id, button_index = '', None
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handle an option button click
    if 'option-button' in button_id:
        button_index = eval(button_id)['index']
        current_score = int(score)
        if button_index == 0:
            return (create_figure(new_correct_choice),
                    create_option_buttons(new_options),
                    f"Score: {current_score + 1}",
                    "Correct!",
                    str(current_score + 1),
                    {'display': 'none'})
        else:
            # Incorrect guess
            return (create_figure(None),
                    [],
                    f"Score: {current_score}",
                    "Incorrect! Game Over.",
                    str(current_score),
                    {'display': 'block'})

    # Default return for initial load
    return (create_figure(new_correct_choice), create_option_buttons(new_options), "Score: 0", "Good luck!", "0", {'display': 'none'})



def create_figure(wind_farm):

    fig = go.Figure()
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        )
    fig.update_yaxes(scaleanchor="x", scaleratio=1,showticklabels=False)
    fig.update_xaxes(showticklabels=False)


    if wind_farm is None:
        return fig


    wind_farm_data_selected = wind_farm_data[wind_farm_data['Name'] == wind_farm]

    fig.add_trace(go.Scatter(
        x=wind_farm_data_selected['X'], y=wind_farm_data_selected['Y'],
        mode='markers', marker=dict(size=12, color='black')))


    return fig 


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)  # Replace 8080 with your desired port number
