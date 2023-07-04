import streamlit as st
import plotly.graph_objects as go
import numpy as np

x = np.linspace(0.0045, 0.02, 100)  # x-values for the green and red area charts
y_green = x * 0.3  # y-values for the green area chart
y_red = x * -0.3  # y-values for the red area chart

# Create the figure and add the traces
fig = go.Figure()

# Green area chart
fig.add_trace(go.Scatter(
    x=x,
    y=y_green,
    fill='tozeroy',
    fillcolor='rgba(50, 200, 50, 0.5)',
    line=dict(color='rgba(0, 0, 0, 0)'),
    hoverinfo='skip'
))

# Red area chart
fig.add_trace(go.Scatter(
    x=x,
    y=y_red,
    fill='tozeroy',
    fillcolor='rgba(200, 50, 50, 0.5)',
    line=dict(color='rgba(0, 0, 0, 0)'),
    hoverinfo='skip'
))

# Add the dashed lines and annotations
fig.add_hline(y=0.0006, line_dash="dot")
fig.add_hline(y=0.002, line_dash="dot")
fig.add_hline(y=0.004, line_dash="dot")
fig.add_vline(x=0.0045, line_dash="dot")


fig.add_annotation(
    x=0.007,
    y=0.0045,
    text="Trailing activation",
    showarrow=False,
    font=dict(size= 40, color="white")
)

fig.add_annotation(
    x=0.007,
    y=0.0025,
    text="Trailing delta",
    showarrow=False,
    font=dict(size= 40, color="white")
)
fig.add_annotation(
    x=0.007,
    y=0.0011,
    text="Fee Zone",
    showarrow=False,
    font=dict(size= 40, color="white")
)

fig.add_annotation(
    x=0.005,
    y=-0.0025,
    text="Target thold",
    showarrow=False,
    font=dict(size= 40, color="white")
)

# Update the layout
fig.update_layout(
    xaxis=dict(title="Target", range=[0, 0.02]),
    yaxis=dict(title="Ret %", range=[-0.005, 0.005]),
    title="Position config",
    showlegend=False
)



# Display the chart
st.plotly_chart(fig, use_container_width=True)