# -*- coding: utf-8 -*-
"""
Dashboard to show cpd results in interactive table with plots

@author: Alex
"""
from utilities import load_data, change_working_dir, plot_changepoints
import Plotting
from dash import Dash, dash_table
import pandas as pd
import collections

change_working_dir(
    r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final\practicum_2022"
)
data = Plotting.load_list_data("Results/test_data/Window_all/")
dict_sites_melt = load_data(
    r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final\practicum_2022\Data\melted_dict_data\site_data_melted"
)
clean_data = dict(Plotting.remove_unuseful_plots(data))
Function = "Max_Rank"

# %%
# test=[(x,y) for x,y in clean_data.items()]
dict_cost_norm = dict(
    (x, s)
    for x, y in clean_data.items()
    for r, s in y.items()
    if r == Function
)
# get plots in
#%%
plot_changepoints(dict_cost_norm, dict_sites_melt, None)

# %% Dash
import pandas as pd
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_table import DataTable
import plotly.graph_objects as go

df = pd.DataFrame(
    {
        "values": [1, 2, 3, 4],
        "labels": ["value 1", "value 2", "value 3", "value 4"],
    }
)

app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="graph"),
        DataTable(
            id="table",
            columns=[{"name": "values", "id": "values"}],
            data=df.to_dict("records"),
        ),
    ]
)


@app.callback(
    Output("graph", "figure"),
    Input("table", "active_cell"),
    prevent_initial_call=True,
)
def update_output_div(active_cell):
    selected_value = df.iloc[active_cell["row"], active_cell["column"]]
    num_values = len(df["values"])

    fig = go.Figure(go.Bar(x=[selected_value], y=[selected_value]))
    fig.update_layout(yaxis_range=[0, num_values])

    fig.update_layout(
        yaxis=dict(
            tickmode="array",
            tickvals=df["values"],
            ticktext=df["labels"],
        ),
    )
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[selected_value],
            ticktext=[selected_value],
        )
    )

    return fig


if __name__ == "__main__":
    app.run_server()
