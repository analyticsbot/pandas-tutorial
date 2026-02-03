# agent_dashboard.py
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import time

# Paths to tracking files
SUMMARY_CSV = Path("agent_summary.csv")
CURRENT_STATE_JSON = Path("current_state.json")

# Initialize Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Pandas Book Agent Dashboard"),
    dcc.Interval(id='interval-component', interval=2000, n_intervals=0),
    
    html.H2("Live Agent Status"),
    dash_table.DataTable(id='live-table', columns=[
        {"name": "chapter", "id": "chapter"},
        {"name": "file", "id": "file"},
        {"name": "agent", "id": "agent"},
        {"name": "status", "id": "status"},
        {"name": "time", "id": "time"}
    ]),
    
    html.H2("Historical Summary"),
    dcc.Graph(id='summary-graph'),

    html.H2("PDF References"),
    dash_table.DataTable(id='pdf-table', columns=[
        {"name": "chapter", "id": "chapter"},
        {"name": "file", "id": "file"},
        {"name": "agent", "id": "agent"},
        {"name": "notes", "id": "notes"}
    ]),
])

# ---------------- Callbacks ----------------
@app.callback(
    Output('live-table', 'data'),
    Output('summary-graph', 'figure'),
    Output('pdf-table', 'data'),
    Input('interval-component', 'n_intervals')
)
def update_dashboard(n):
    # Live agent status
    live_data = []
    if CURRENT_STATE_JSON.exists():
        with open(CURRENT_STATE_JSON) as f:
            try:
                state = json.load(f)
                live_data.append({
                    "chapter": state.get("chapter"),
                    "file": state.get("file"),
                    "agent": state.get("agent"),
                    "status": state.get("status"),
                    "time": time.strftime('%H:%M:%S', time.localtime(state.get("time",0)))
                })
            except:
                pass

    # Historical summary graph
    if SUMMARY_CSV.exists():
        df = pd.read_csv(SUMMARY_CSV)
        fig = px.bar(df.groupby('agent')['success'].count().reset_index(),
                     x='agent', y='success', title='Agent Actions Count')
    else:
        fig = px.bar()

    # PDF references table
    pdf_data = []
    if SUMMARY_CSV.exists():
        df = pd.read_csv(SUMMARY_CSV)
        pdf_data = df[df['notes'].str.contains("PDF")].to_dict('records')

    return live_data, fig, pdf_data

# ---------------- Run App ----------------
# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(debug=True)   # <- replace run_server with run

