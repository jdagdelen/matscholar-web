import dash_html_components as html
from dash.dependencies import Input, Output, State
from matscholar import Rester
from collections import defaultdict
from matscholar_web.view.search_app import serve_layout
import json
import pandas as pd

rester = Rester()
VALID_FILTERS = ["material", "property", "application", "descriptor", "characterization", "synthesis", "phase"]
max_results = 50

def highlight_material(body, material):
    highlighted_phrase = html.Mark(material)
    if len(material) > 0 and material in body:
        chopped = body.split(material)
        newtext = []
        for piece in chopped[:-1]:
            newtext.append(piece)
            newtext.append(highlighted_phrase)
        newtext.append(chopped[-1])
        return newtext
    return body

def generate_nr_results(n, search=None, material=None, filters=None):
    if n == 0:
        return "No Results"
    elif n >= max_results:
        return ['Showing {} of > {:,} results. For full results, use the '.format(max_results, n), html.A('Matscholar API.', href='https://github.com/materialsintelligence/matscholar')]
    else:
        return 'Showing {} of {:,} results'.format(min(max_results, n), n)

def results_html(results,
                   max_rows=max_results):
    columns=['title', 'authors', 'year', 'journal', 'abstract']
    formattedColumns = ['Title', 'Authors', 'Year', 'Journal', 'Abstract (preview)']
    if results is not None:
        df = pd.DataFrame(results)
    else:
        pd.DataFrame()
    if not df.empty:
        format_authors = lambda author_list: ", ".join(author_list)
        df['authors'] = df['authors'].apply(format_authors)
        def word_limit(abstract):
            try:
                return abstract[:200]+"..."
            except IndexError:
                return abstract
        df['abstract'] = df['abstract'].apply(word_limit)
        hm = highlight_material
        return [html.Label(generate_nr_results(len(results)), id="number_results"), html.Table(
            # Header
            [html.Tr([html.Th(formattedColumns[i]) for i,col in enumerate(columns)])] +
            # Body
            [html.Tr([
                html.Td(html.A(str(df.iloc[i][col]),
                               href=df.iloc[i]["link"], target="_blank")) if col == "title"
                # else html.Td(
                #     hm(str(df.iloc[i][col]), df.iloc[i]['to_highlight'] if materials else search)) if col == "abstract"
                else html.Td(df.iloc[i][col]) for col in columns])
                for i in range(min(len(df), max_rows))],
            id="table-element")]
    return html.Div([html.Label(generate_nr_results(len(results)), id="number_results"),
            html.Table(id="table-element")])

def gen_output(most_common, entity_type, query, class_name="three column"):
    query = [(key, value) for key, value in query.items()]
    table = html.Table(
        [html.Tr([html.Th(entity_type), html.Th("score", style={"textAlign": "right", "fontWeight": "normal"})],
                 className="summary-header")] +
        [html.Tr([
            html.Td(html.A(ent, href="/search/{}/{}/{}".format(entity_type.lower(), ent, query))),
            html.Td('{:.2f}'.format(100*score), style={"textAlign": "right"})], style={'color': 'black'})
            for ent, count, score in most_common],
        className="summary-table")
    return html.Div(table, className="summary-div " + class_name, style={"width": "20%"})

def gen_table(results_dict, query=None):
    return html.Div([
                html.Div([
                    gen_output(results_dict["PRO"], "Property", query),
                    gen_output(results_dict["APL"], "Application", query),
                    gen_output(results_dict["CMT"], "Characterization", query),
                    gen_output(results_dict["SMT"], "Synthesis", query)],  className="row"),
                html.Div([
                    gen_output(results_dict["DSC"], "Sample descriptor", query),
                    gen_output(results_dict["SPL"], "Phase", query),
                    gen_output(results_dict["MAT"], "Material", query)], className="row"),
            ])

def bind(app):
    @app.callback(
        Output('results', 'children'),
        [Input('search-btn','n_clicks')],
        [State('search-input','value')]+[State(f+'-filters', 'value') for f in VALID_FILTERS]+[State("search-radio", "value")])
    def show_results(*args,**kwargs):
        if list(args)[0] is not None:
            print(list(args))
            if list(args)[-1] == "search":
                text = str(args[1])
                filters = {f: [s.strip() for s in args[i+2].split(',')] for i,f in enumerate(VALID_FILTERS) if ((list(args)[i+2] is not None) and (args[i+2].split(',') != ['']))}
                results = rester.search_text_with_ents(text,filters,cutoff=max_results)
                return results_html(results)
            elif list(args)[-1] == "summary":
                query = defaultdict(list)
                for filter, ents in zip(VALID_FILTERS, args[2:-1]):
                    if ents:
                        ents = [ent.strip() for ent in ents.split(",")]
                        query[filter] += ents
                dumped = json.dumps(query)
                summary = rester.get_summary(dumped)
                return gen_table(summary, query=query)

    @app.callback(
        Output("search-input", "style"),
        [Input("search-radio", "value")],
        [State("search-radio", "value")]
    )
    def toggle_inputs(radio_in, radio_val):
        if radio_val == "search":
            return {"display": "table-cell", "width": "100%"}
        else:
            return {"display": "none"}


