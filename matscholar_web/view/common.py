import dash_html_components as html
import dash_core_components as dcc

# Header with logo
header = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Img(
        src="https://matscholar-web.s3-us-west-1.amazonaws.com/matscholar_logo+alpha.png",
        style={
            'width': '450px',
            "display": "block",
            'max-width': "100%",
            "margin": "5px auto",
        })],
    id="header_container",
    className="row")

# Navigation bar
nav = html.Nav(
        style={
            "margin": "3px 1px",
            "padding": "3px 1px",
            "textAlign": "center"},
        children=[
            dcc.Link("Explore", href="/explore"),
            html.Span(" | ", style={"color": "whitesmoke"}),
            dcc.Link("Analyze", href="/analyze"),
        ],
        id="nav_bar")

# Footer with about info and privacy policy
footer = html.Div([
    html.Div(
        [html.Span("Note: This is an alpha release of Matscholar for the purpose of collecting feedback.")],
        className="row"),
    html.Div([
        html.A("About Matscholar",
               href="https://github.com/materialsintelligence/matscholar-web",
               target="_blank"),
        html.Span(" | "),
        html.A("Privacy Policy",
               href='https://www.iubenda.com/privacy-policy/55585319',
               target="_blank"),
        html.Span(" | "),
        html.A("Submit Feedback",
               href='https://github.com/materialsintelligence/matscholar-web/issues',
               target="_blank")],
        className="row"),
    html.Div(html.Span('Copyright © 2019 - Materials Intelligence'))],
    id="footer_container",
    className="row",
    style={
        "color": "grey",
        "textAlign": "center",
        "width": "100%"})