from dash import Dash, html, dcc, Input, Output, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd
from datetime import datetime
import time

# Initialize Dash app with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)

# Custom styles
CARD_STYLE = {
    "transition": "transform 0.3s, box-shadow 0.3s",
    "boxShadow": "0 4px 8px rgba(0,0,0,0.2)",
    "border": "none",
    "borderRadius": "15px",
    "background": "linear-gradient(145deg, #2c3e50, #34495e)",
    "color": "white"
}

HOVER_STYLE = {
    "transform": "translateY(-5px)",
    "boxShadow": "0 8px 16px rgba(0,0,0,0.3)"
}

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H1("COVID-19 Dashboard", className="display-4 mb-4 text-center"),
                            html.P("Real-time Global Statistics", className="lead text-center text-muted")
                        ],
                        className="my-4"
                    ),
                    width=12
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            html.I(className="fas fa-virus fa-3x text-danger me-3"),
                                            html.Div(
                                                [
                                                    html.Span("Total Cases", className="card-title h6 text-uppercase text-muted"),
                                                    html.H2(id="total-cases", className="mb-0 mt-2 animate-number")
                                                ]
                                            )
                                        ],
                                        className="d-flex align-items-center"
                                    ),
                                    html.Small(id="cases-updated", className="text-muted")
                                ]
                            )
                        ],
                        style=CARD_STYLE,
                        className="mb-4 h-100"
                    ),
                    md=4, className="mb-4"
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            html.I(className="fas fa-skull-crossbones fa-3x text-warning me-3"),
                                            html.Div(
                                                [
                                                    html.Span("Total Deaths", className="card-title h6 text-uppercase text-muted"),
                                                    html.H2(id="total-deaths", className="mb-0 mt-2 animate-number")
                                                ]
                                            )
                                        ],
                                        className="d-flex align-items-center"
                                    ),
                                    html.Small(id="deaths-updated", className="text-muted")
                                ]
                            )
                        ],
                        style=CARD_STYLE,
                        className="mb-4 h-100"
                    ),
                    md=4, className="mb-4"
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.Div(
                                        [
                                            html.I(className="fas fa-heartbeat fa-3x text-success me-3"),
                                            html.Div(
                                                [
                                                    html.Span("Total Recovered", className="card-title h6 text-uppercase text-muted"),
                                                    html.H2(id="total-recovered", className="mb-0 mt-2 animate-number")
                                                ]
                                            )
                                        ],
                                        className="d-flex align-items-center"
                                    ),
                                    html.Small(id="recovered-updated", className="text-muted")
                                ]
                            )
                        ],
                        style=CARD_STYLE,
                        className="mb-4 h-100"
                    ),
                    md=4, className="mb-4"
                )
            ],
            className="g-4"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Visualization Options", className="h5"),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Select(
                                                    id="chart-type",
                                                    options=[
                                                        {"label": "3D Bar Chart", "value": "3d"},
                                                        {"label": "Pie Chart", "value": "pie"},
                                                        {"label": "Line Chart", "value": "line"}
                                                    ],
                                                    value="pie",
                                                    className="mb-3"
                                                ),
                                                md=6
                                            ),
                                            dbc.Col(
                                                dbc.Select(
                                                    id="metric-selector",
                                                    options=[
                                                        {"label": "Total Numbers", "value": "total"},
                                                        {"label": "Per Million", "value": "per_million"}
                                                    ],
                                                    value="total",
                                                    className="mb-3"
                                                ),
                                                md=6
                                            )
                                        ]
                                    ),
                                    dbc.Spinner(
                                        dcc.Graph(id="covid-chart", config={"displayModeBar": False}),
                                        color="primary"
                                    )
                                ]
                            )
                        ],
                        style=CARD_STYLE,
                        className="h-100"
                    ),
                    md=8
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Detailed Statistics", className="h5"),
                            dbc.CardBody(
                                [
                                    dbc.Spinner(
                                        dbc.Table(
                                            id="data-table",
                                            striped=True,
                                            hover=True,
                                            responsive=True,
                                            className="table-dark"
                                        ),
                                        color="primary"
                                    )
                                ]
                            )
                        ],
                        style=CARD_STYLE,
                        className="h-100"
                    ),
                    md=4
                )
            ],
            className="g-4"
        ),
        dcc.Interval(id="interval-component", interval=60*1000, n_intervals=0),
        dcc.Store(id='data-store'),
        html.Div(
            [
                html.Small("Data Source: disease.sh API", className="text-muted"),
                html.Br(),
                html.Small(id="last-updated", className="text-muted")
            ],
            className="text-center mt-4"
        ),
        html.Div(id="dummy-output", style={"display": "none"})
    ],
    className="py-4"
)

# Add custom CSS through assets folder or inline
app.clientside_callback(
    """
    function(n) {
        // Add animation to numbers
        const animateNumbers = () => {
            document.querySelectorAll('.animate-number').forEach(el => {
                el.style.transition = 'all 0.5s ease';
                el.style.transform = 'scale(1.1)';
                setTimeout(() => { el.style.transform = 'scale(1)'; }, 500);
            });
        }
        setTimeout(animateNumbers, 100);
        return '';
    }
    """,
    Output("dummy-output", "children"),
    Input("interval-component", "n_intervals")
)

@app.callback(
    [
        Output("total-cases", "children"),
        Output("total-deaths", "children"),
        Output("total-recovered", "children"),
        Output("covid-chart", "figure"),
        Output("data-table", "children"),
        Output("last-updated", "children"),
        Output("cases-updated", "children"),
        Output("deaths-updated", "children"),
        Output("recovered-updated", "children")
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("chart-type", "value"),
        Input("metric-selector", "value")
    ]
)
def update_data(n, chart_type, metric):
    ctx = callback_context
    try:
        response = requests.get("http://covid-dashboard.com/api/covid-data", timeout=10)
        response.raise_for_status()
        data = response.json()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format numbers
        total_cases = f"{data['cases']:,}"
        total_deaths = f"{data['deaths']:,}"
        total_recovered = f"{data['recovered']:,}"

        # Create DataFrame
        df = pd.DataFrame({
            "Metric": ["Cases", "Deaths", "Recovered"],
            "Total": [
                data["cases"],
                data["deaths"],
                data["recovered"]
            ],
            "Per Million": [
                data["casesPerOneMillion"],
                data["deathsPerOneMillion"],
                data["recoveredPerOneMillion"]
            ]
        })

        # Create visualization
        if chart_type == "3d":
            fig = px.bar_3d(
                df,
                x="Metric",  
                y=[metric], 
                z="Total" if metric == "total" else "Per Million", 
                color="Metric", 
                title=f"COVID-19 {'Total' if metric == 'total' else 'Per Million'} Statistics (3D)"
            )
        elif chart_type == "pie":
            fig = px.pie(
                df,
                names="Metric",
                values="Total" if metric == "total" else "Per Million",
                hole=0.4,
                title=f"COVID-19 Distribution ({'Total' if metric == 'total' else 'Per Million'})"
            )
        else:
            fig = px.line(
                df,
                x="Metric",
                y="Total" if metric == "total" else "Per Million",
                markers=True,
                title=f"COVID-19 Trend ({'Total' if metric == 'total' else 'Per Million'})"
            )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        # Create table
        table_header = [html.Thead(html.Tr([html.Th("Metric"), html.Th("Total"), html.Th("Per Million")]))]
        table_body = [html.Tbody([
            html.Tr([html.Td("Cases"), html.Td(f"{data['cases']:,}"), html.Td(f"{data['casesPerOneMillion']:,.2f}")]),
            html.Tr([html.Td("Deaths"), html.Td(f"{data['deaths']:,}"), html.Td(f"{data['deathsPerOneMillion']:,.2f}")]),
            html.Tr([html.Td("Recovered"), html.Td(f"{data['recovered']:,}"), html.Td(f"{data['recoveredPerOneMillion']:,.2f}")])
        ])]

        return (
            total_cases,
            total_deaths,
            total_recovered,
            fig,
            table_header + table_body,
            f"Last updated: {timestamp}",
            f"Updated: {timestamp}",
            f"Updated: {timestamp}",
            f"Updated: {timestamp}"
        )

    except Exception as e:
        print(f"Error: {e}")
        return (
            "N/A", "N/A", "N/A",
            px.scatter(title="Error Loading Data").update_layout(template="plotly_dark"),
            html.Div(dbc.Alert("Failed to fetch data", color="danger")),
            "Last update failed",
            "Update failed",
            "Update failed",
            "Update failed"
        )

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)