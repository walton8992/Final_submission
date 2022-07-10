# -*- coding: utf-8 -*-
"""
Dashboard to show cpd results in interactive table with plots

@author: Alex
"""
from utilities import load_data
from dash import Dash, dash_table
import pandas as pd
import collections


def remove_unuseful_plots(dictionary: dict):
    """
    Want to remove those with just line at the end of the plot plot
    """

    new_dict = collections.defaultdict(dict)
    plot_dict = dictionary
    for key, item in plot_dict.items():
        if len(list(item.values())[0]) == 1:
            pass
        else:
            sortedlist = item["all"]
            sortedlist = sorted(sortedlist)
            new_dict[key] = sortedlist
            # new_dict[key] = new_dict[key].sort()
    return new_dict


# TODO generate plot and table of dict from output of results
#   test

path_do_dict = r"C:\Users\Alex\Documents\Georgia Tech Official MSC\Pract_final\practicum_2022\Results\binseg_flat"
load_dict = load_data(path_do_dict)
df = remove_unuseful_plots(load_dict)
df_dash = pd.DataFrame.from_dict(df, orient="index")
df_dash = df_dash.reset_index()
app = Dash(__name__)
test = df_dash.to_dict("records"), [
    {"name": i, "id": i} for i in df_dash.columns
]
app.layout = dash_table.DataTable(
    df_dash.to_dict("records"), [{"name": i, "id": i} for i in df_dash.columns]
)
if __name__ == "__main__":
    app.run_server(debug=False)

# %%
# df_dict = pd.DataFrame.from_dict(df, orient="index")

import pandas as pd
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_table import DataTable
import plotly.graph_objects as go


app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="graph"),
        DataTable(
            id="table",
            columns=[{"name": "values", "id": "values"}],
            data=df,
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
    app.run_server(debug=False)
