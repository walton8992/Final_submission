# -*- coding: utf-8 -*-
"""
utility helper

"""

import plotly.express as px

def plot_change_points_pyplot(data_test,dict_sites_melt,save_fig=False,show_fig=False):
    for key,data in data_test.items():
        # for cost,points in data.items():
            y_sns=dict_sites_melt[key][['datetime','value','variable']]
          
            for cost,date in data.items():
                if len(data)==0:
                    pass
                else:
                    fig = px.line(y_sns, x="datetime", y="value",color='variable',title=key+'_'+cost)
                    for x in date:
                        if len(data) ==1:
                            #we only have end point
                            pass
                        else:
                            date_plot=y_sns['datetime'][x-1]
                            fig.add_vline(date_plot,line_width=2, line_dash='dash',line_color='red')
                    if show_fig:
                        fig.show()
                    if save_fig:
                        fig.write_html("plots/rupture_plots/{}_plot.html".format(key+'_'+cost))
