import pandas as pd
from flask import Flask, render_template
import json
import plotly
import plotly.express as px
# BELLCURVE
import plotly.figure_factory as ff

import numpy as np
from scipy import stats
import plotly.graph_objs as go 
from plotly.graph_objs import *
from plotly.offline import init_notebook_mode, iplot
from scipy.stats import norm

# import chart_studio.tools as tls 
import base64

def customer_classifier(input):
    if(input=='an Average Performer'):
        return "you do not frecuently"
    elif(input=='a Low Performer'):
        return "you rarely"
    elif(input=='Top Performer'):
        return "you are one of the best performers and frequently"

#BAR GRAPH FOR USAGE:
def figbar_sliding(funnel_tdh,funnel_tah,funnel_teh,drivepilot_enable_events,ffunnel_tdh,ffunnel_tah,ffunnel_teh,fdrivepilot_enable_events,encoded_vin):

    time_periods = ['week', 'month', '3month']
    max_value_3month = max(ffunnel_tdh['3month'], ffunnel_tah['3month'], ffunnel_teh['3month'],
                       funnel_tdh['3month'], funnel_tah['3month'], funnel_teh['3month'])
    # Create the initial bar chart for the first time period
    figbar = go.Figure()

    # Add the Fleet bars
    figbar.add_trace(go.Bar(
        name='Fleet',
        x=[ffunnel_tdh[time_periods[0]], ffunnel_tah[time_periods[0]], ffunnel_teh[time_periods[0]]],
        y=['Total driving hours', 'Hours with DrivePilot available', 'Hours with DrivePilot enabled'],
        orientation='h',
        marker=dict(color='rgba(178, 24, 43,255)'),
        text=[ffunnel_tdh[time_periods[0]], ffunnel_tah[time_periods[0]], ffunnel_teh[time_periods[0]]],
        textposition='auto',
        textfont=dict(size=30, color='white'),
        texttemplate='%{text:.1f}'
    ))

    # Add the You bars
    figbar.add_trace(go.Bar(
        name='You',
        x=[funnel_tdh[time_periods[0]], funnel_tah[time_periods[0]], funnel_teh[time_periods[0]]],
        y=['Total driving hours', 'Hours with DrivePilot available', 'Hours with DrivePilot enabled'],
        orientation='h',
        marker=dict(color='rgba(103, 0, 31,255)'),
        text=[funnel_tdh[time_periods[0]], funnel_tah[time_periods[0]], funnel_teh[time_periods[0]]],
        textposition='auto',
        textfont=dict(size=30, color='white'),
        texttemplate='%{text:.1f}'
    ))

    # Create frames for the animation, excluding the drivepilot_enable_events
    frames = [
        go.Frame(
            data=[
                go.Bar(
                    name='Fleet',
                    x=[ffunnel_tdh[period], ffunnel_tah[period], ffunnel_teh[period]],
                    y=['Total driving hours', 'Hours with DrivePilot available', 'Hours with DrivePilot enabled'],
                    orientation='h',
                    marker=dict(color='rgba(178, 24, 43,255)'),
                    text=[ffunnel_tdh[period], ffunnel_tah[period], ffunnel_teh[period]],
                    textposition='auto',
                    textfont=dict(size=30, color='white'),
                    texttemplate='%{text:.1f}'
                ),
                go.Bar(
                    name='You',
                    x=[funnel_tdh[period], funnel_tah[period], funnel_teh[period]],
                    y=['Total driving hours', 'Hours with DrivePilot available', 'Hours with DrivePilot enabled'],
                    orientation='h',
                    marker=dict(color='rgba(103, 0, 31,255)'),
                    text=[funnel_tdh[period], funnel_tah[period], funnel_teh[period]],
                    textposition='auto',
                    textfont=dict(size=30, color='white'),
                    texttemplate='%{text:.1f}'
                )
            ],
            name=period,
            # Add an annotation for the drivepilot_enable_events
            layout=go.Layout(
                annotations=[
                    dict(
                        x=0.5,
                        y=1.15,
                        xref='paper',
                        yref='paper',
                        text=f'DrivePilot engagements: {drivepilot_enable_events[period]:.0f}',
                        showarrow=False,
                        font=dict(size=22, color='white')
                    )
                ]
            )
        )
        for period in time_periods
    ]

    # Add frames to the figure
    figbar.frames = frames

    # Set up the slider
    sliders = [{
        'steps': [
            {
                'args': [[frame.name], {'frame': {'duration': 300, 'redraw': True}, 'mode': 'immediate'}],
                'label': frame.name,
                'method': 'animate'
            }
            for frame in frames
        ],
        'transition': {'duration': 300},
        'x': 0,
        'y': 0,
        'currentvalue': {
            'visible': False,
        },
        'len': 1.0,
        'font': {'color': 'white'}
    }]

    # Update the layout
    figbar.update_layout(
        title='You compared to the fleet from 01.01.2024 to 31.03.2024',
        paper_bgcolor='rgba(59,56,56,255)',
        plot_bgcolor='rgba(59,56,56,255)',
        title_font=dict(color='white', size=26),
        legend=dict(font=dict(color='white', size=20)),
        xaxis=dict(
            titlefont=dict(color='white', size=18),
            tickfont=dict(color='white', size=18),
            linecolor='white',
            zerolinecolor='white',
            range=[0,max_value_3month],
            fixedrange=True
        ),
        yaxis=dict(
            tickfont=dict(color='white', size=18),
            linecolor='white',
            autorange='reversed',
            fixedrange=True
        ),
        sliders=sliders,
    )
    figbar['layout']['sliders'][0]['pad']=dict(r= 10, t= 50,)
    figbar.update_layout(hovermode=False)
    figbar.write_html('./webserver/fleet/{}/figbar_sliding.html'.format(encoded_vin),config = {'displayModeBar': False})
    return 0


def driveratio_sliding(av_week,en_week,av_month,en_month,av_threemonth,en_threemonth,encoded_vin):

    values= [
        [av_week-en_week,en_week],
        [av_month-en_month,en_month],
        [av_threemonth-en_threemonth,en_threemonth]
    ]

    theme = {
    'font_color': 'white',
    'bg_color': 'rgba(59,56,56,1)',  # Adjusted alpha to 1 for full opacity
    'colors': ['rgba(178, 24, 43, 1)', 'rgba(103, 0, 31, 1)']  # Red and dark red
    }

    fig = go.Figure(
        data=[go.Pie(labels=['DrivePilot not used', 'DrivePilot used'], values=values[0], marker_colors=theme['colors'], textinfo='percent', insidetextorientation='radial')]
    )
    time_periods=['Week','Month','Three months']
    frames = [
    go.Frame(
        data=[go.Pie(labels=['DrivePilot not used', 'DrivePilot used'], values=value_set, marker_colors=theme['colors'], textinfo='percent', insidetextorientation='radial')],
        name=str(time_period)
    )
    for time_period, value_set in zip(time_periods, values)
    ]
    fig.frames = frames

    # Set up the slider
    sliders = [{
        'steps': [
            {
                'args': [[frame.name], {'frame': {'duration': 300, 'redraw': True}, 'mode': 'immediate'}],
                'label': frame.name,
                'method': 'animate'
            }
            for frame in frames
        ],
        'transition': {'duration': 300},
        'x': 0,
        'y': 0,
        'currentvalue': {
            'visible': False,
        },
        'len': 1.0
    }]

    # Update the layout with the theme
    fig.update_layout(
        title='Your DrivePilot usage ratio',
        sliders=sliders,
        showlegend=True,
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font=dict(color=theme['font_color'],size=20),
    )

    # Add play and pause button
   
    fig.update_layout(hovermode=False)
    fig.write_html('./webserver/fleet/{}/ratioanimated_sliding.html'.format(encoded_vin),config = {'displayModeBar': False})
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    return 0





def hourscomparaison_sliding(week_hours,month_hours,threemonth_hours,fweek_hours,fmonth_hours,fthreemonth_hours,encoded_vin):
    timeofuse = pd.DataFrame({"timeperiod": ["week","month","3month"],"yourhours": [2,11,38],"fleethours":[8,50,139]})


    df = pd.DataFrame({
        'timeperiod': ['week', 'month', '3month'],
        'Your DrivePilot hours': [week_hours,month_hours,threemonth_hours],
        'Fleet DrivePilot average hours': [fweek_hours,fmonth_hours,fthreemonth_hours],
    })
    color_map = {
        'Your DrivePilot hours': 'rgba(178, 24, 43,255)',  # Change to your desired colors
        'Fleet DrivePilot average hours': 'rgba(103, 0, 31,255)'    # Change to your desired colors
    }
    theme = {
    'font_color': 'white',
    'bar_colors': color_map,
    'bg_color': 'rgba(0,0,0,0)',  # Transparent background
    'title': 'Your Hours vs Fleet Hours Over Time'
    }

    df_long = df.melt(id_vars='timeperiod', var_name='category', value_name='hours')
    df_long['color'] = df_long['category'].map(color_map)
    fig = px.bar(
        df_long,
        y='category',
        x='hours',
        orientation='h',
        animation_frame='timeperiod',
        range_x=[0, df_long['hours'].max()],
        title='Your Hours vs Fleet Hours Over Time',
        color='category',
        color_discrete_map=color_map
    )

    fig.layout.updatemenus = None

    fig.update_traces(textposition='inside',
        textfont=dict(size=24),
        texttemplate='%{x:.1f}',
        selector=dict(type='bar')
        )

    fig.update_layout(
        uniformtext_minsize=24,
        paper_bgcolor='rgba(59,56,56,1)',
        plot_bgcolor='rgba(59,56,56,1)',
        title_font=dict(color='white',size=26),
        legend=dict(font=dict(color='white',size=24)),
        title_font_color='white',
        legend_title_font_color='white',
        legend_font_color='white',
        xaxis=dict(
            titlefont=dict(color='white',size=20),
            tickfont=dict(color='white',size=20),
            linecolor='white',  # Set the x-axis line color to white
            zerolinecolor='white',  # Set the zero line color to white (if needed)
            fixedrange=True
        ),
        yaxis=dict(
            title_font=dict(color='white'),
            tickfont=dict(color='white',size=20),
            linecolor='white',  # Set the y-axis line color to white
            autorange='reversed',
            fixedrange=True
        ),
        sliders=[{
            'activebgcolor': 'white',
            'bgcolor': 'white',
            'currentvalue': {
                'font': {'color': 'white','size': 20},
                'visible':False
            },
            'font': {'color': 'white'}
        }],
        showlegend=False
    )
    fig.update_layout(hovermode=False)
    fig.update_traces(marker=dict(color=[color_map[category] for category in df_long['category']]))
    fig.write_html('./webserver/fleet/{}/hourcomparaison_sliding.html'.format(encoded_vin),config = {'displayModeBar': False})

    return 0