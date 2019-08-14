from matscholar_web.view.common import header, nav, footer


def serve_layout(path):
    #     top, html.Div([search_bar, filter_boxes_and_results],
    #                   id="search-layout")])
    #
    # filters = None
    # if path is not None and len(path) > len("/search"):
    #     path = path[len("/search") + 1::]
    #     path = path.replace("%20", " ")
    #     ent_type, ent, query = path.split("/")
    #     filters = defaultdict(list)
    #     filters[ent_type].append(ent)
    #     for key, value in eval(query):
    #         filters[key] += value
    #
    # search_bar = search_bar_html()
    # filter_boxes = [html.Div([html.Label("Filters")])]
    # if not filters:
    #     filter_boxes += [search_filter_box_html(label) for label in valid_filters]
    # else:
    #     for label in valid_filters:
    #         if label in filters:
    #             filter_boxes.append(search_filter_box_html(label, filters[label]))
    #         else:
    #             filter_boxes.append(search_filter_box_html(label))
    #
    # filter_boxes_and_results = html.Div(
    #     [html.Div(filter_boxes, style={'width': '25%', 'float': 'left', 'display': 'inline-block'}),
    #      dcc.Loading(id="loading-1", children=[
    #          html.Div(id='results', style={'width': '75%', 'float': 'right', 'display': 'inline-block'})],
    #                  type="default")])
    # radio = html.Div(dcc.RadioItems(id="search-radio",
    #                                 options=[
    #                                     {'label': "Search", 'value': "search"},
    #                                     {"label": "Summary", "value": "summary"}
    #                                 ],
    #                                 value='search',
    #                                 labelStyle={'display': 'inline-block'}
    #                                 ),
    #                  style={"display": "table-cell", "verticalAlign": "top", "paddingLeft": "10px", "float": "left"})
    # button = html.Div(html.Button(
    #     "Search",
    #     className="button-search",
    #     id="search-btn", style={"height": "50px", "width": "150px", "font-size": 16}),
    #     style={"display": "table-cell", "verticalAlign": "top", "paddingLeft": "10px", "float": "right"})
    # top = html.Div([radio, button], className="row", style={"display": "table", "marginTop": "10px", "width": "100%"})
    # layout = html.Div([top, html.Div([search_bar, filter_boxes_and_results], id="search-layout")])

    layout = html.Div([header, nav, app, footer],
                      id="explore-layout",
                      className="container")

    return layout
