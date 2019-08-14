import dash_html_components as html
from dash.dependencies import Input, Output, State
from matscholar import Rester
from collections import defaultdict
from matscholar_web.view.search_app import serve_layout
import json
import pandas as pd
import urllib

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

def generate_nr_results(n):
    """
    Generates a message to be displayed at top of results page.
    Args:
        n (int): Number of results returned.

    Returns:
        (str or list) Message to be displayed.

    """
    if n == 0:
        return "No Results"
    elif n >= max_results:
        return ['Showing {} of > {:,} results. For full results, use the '.format(max_results, n),
                html.A('Matscholar API.', href='https://github.com/materialsintelligence/matscholar')]
    else:
        return 'Showing {} of {:,} results'.format(min(max_results, n), n)

def format_result(result):
    """
    Takes in one row of a dataframe and formats it for display in the
    search results table.

    Title of the paper is the first line
    Author 1, Author 2... - Title of Journal, Year - Publisher
    First 200 characters of abstract.
    Entities

    Args:
        result: Row of dataframe to be formatted for display.

    Returns:
        html.Div of formatted result
    """

    columns = ['title', 'authors', 'year', 'journal', 'abstract', ]

    title = html.Div(html.A(result['title'],
                            href=result["link"],
                            target="_blank",
                            style={"font-size":"120%"}
                            )
                     )

    # Format the 2nd line "authors - journal, year" with ellipses for overflow
    characters_remaining = 120 # max line length
    characters_remaining -= 5 # spaces, '-', and ','

    year = result['year']
    characters_remaining -= 4

    journal = result['journal']
    if len(journal) > 20:
        journal = journal if len(journal) < 33 else journal[0:30] +"..."
    characters_remaining -= len(journal)

    authors = result["authors"]
    full_author_list = authors.split(", ")
    num_authors = len(full_author_list)
    reduced_author_list = []
    while len(full_author_list) > 0:
        author = full_author_list.pop(0)
        if characters_remaining > len(author):
            reduced_author_list.append(author)
            characters_remaining -= len(author) + 2
    authors = ", ".join(reduced_author_list)
    if len(reduced_author_list) < num_authors:
        authors += "..."

    ajy = "{} - {}, {}".format(authors, journal, year)
    authors_journal_and_year = html.Div(ajy, style={"color":"green"})
    abstract = html.Div(result["abstract"])
    return html.Tr(html.Td(html.Div([title,
                                     authors_journal_and_year,
                                     abstract])))


def format_authors(author_list):
    if isinstance(author_list, (list, tuple)):
        return(", ".join([format_authors(author) for author in author_list]))
    else:
        if ", " in author_list:
            author_list = author_list.split(", ")
            author_list.reverse()
            author_list = " ".join(author_list)
        elif "," in author_list:
            author_list = author_list.split(",")
            author_list.reverse()
            author_list = " ".join(author_list)
        return author_list


def results_html(results, max_rows=max_results):
    columns=['title', 'authors', 'year', 'journal', 'abstract']
    formattedColumns = ['Title', 'Authors', 'Year', 'Journal', 'Abstract (preview)']
    if results is not None:
        df = pd.DataFrame(results)
    else:
        pd.DataFrame()
    if not df.empty:
        df['authors'] = df['authors'].apply(format_authors)
        def word_limit(abstract):
            try:
                return abstract[:200]+"..."
            except IndexError:
                return abstract
        df['abstract'] = df['abstract'].apply(word_limit)
        hm = highlight_material

        results = [format_result(df.iloc[i]) for i in range(min(len(df), max_rows))]
        return html.Div([html.Label(generate_nr_results(len(results)), id="number_results"), html.Table(
            # Header
            # [html.Tr([html.Th(formattedColumns[i]) for i,col in enumerate(columns)])] +
            # Body
            results,
            id="table-element")])
    return html.Div([html.Label(generate_nr_results(len(results)), id="number_results"),
            html.Table(id="table-element")])

def gen_output(most_common, entity_type, query, class_name="three column"):
    query = [(key, value) for key, value in query.items()]
    table = html.Table(
        [html.Tr([html.Th(entity_type), html.Th("score", style={"textAlign": "right", "fontWeight": "normal"})],
                 className="summary-header")] +
        [html.Tr([
            html.Td(html.A(ent, href="/search/{}/{}/{}".format(entity_type.lower(), ent, query))),
            html.Td('{:.2f}'.format(score), style={"textAlign": "right"})], style={'color': 'black'})
            for ent, count, score in most_common],
        className="summary-table")
    return html.Div(table, className="summary-div " + class_name, style={"width": "20%"})

def gen_table(results_dict, query=None):
    return html.Div([
                html.Div([
                    gen_output(results_dict["PRO"], "Property", query),
                    gen_output(results_dict["APL"], "Application", query),
                    gen_output(results_dict["SMT"], "Synthesis", query)],  className="row", style={"width": "130%"}),
                html.Div([
                    gen_output(results_dict["DSC"], "Sample descriptor", query),
                    gen_output(results_dict["MAT"], "Material", query),
                    gen_output(results_dict["CMT"], "Characterization", query)], className="row", style={"width": "130%"}),
                html.Div([gen_output(results_dict["SPL"], "Phase", query)], className="row", style={"width": "130%"})
            ])

def split_inputs(input):
    if input is not None:
        return [inp.strip() for inp in input.split(",")]
    else:
        return []

def get_details(dois):
    return html.Details([
        html.Summary('Show dois?'),
        html.Span([html.A("{}; ".format(doi), href="http://www.doi.org/{}".format(doi), target="_blank")
                   for doi in dois[:20]],
                  style={"white-space": "nowrap"})
        ])

def gen_output_matsearch(result):
    table = html.Table(
        [html.Tr([html.Th("Material"), html.Th("Counts"), html.Th("Clickable doi links",
                                                                  style={"white-space": "nowrap"})])] +
        [html.Tr([
            html.Td(mat),
            html.Td(count), html.Td(get_details(dois))])
            for mat, count, dois in result],
        style={"width": "100px"})
    return html.Div(table, style={"width": "100px"})

def gen_df(result):
    mats = [mat for mat, _, _ in result]
    counts = [count for _, count, _ in result]
    dois = [" ".join(dois) for _, _, dois in result]
    df = pd.DataFrame()
    df["Material"] = mats
    df["counts"] = counts
    df["dois"] = dois
    return df

def bind(app):
    @app.callback(
        Output('results', 'children'),
        [Input('search-btn','n_clicks')],
        [State('search-input','value')]+[State(f+'-filters', 'value') for f in VALID_FILTERS]+
        [State("material-search-input", "value"), State("element-filters-input", "value"), State("search-radio", "value")])
    def show_results(*args, **kwargs):
        if list(args)[0] is not None:
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
            else:
                entities = list(args)[-3]
                elements = list(args)[-2]
                # Extract the data
                entities = split_inputs(entities)
                elements = elements if elements != "" else None
                elements = split_inputs(elements)
                result = rester.materials_search_ents(entities, elements)
                result = [(mat, count, dois) for mat, count, dois in result
                          if (not mat.isupper()) and len(mat) > 2 and "oxide" not in mat]

                # Update the download link
                df = gen_df(result)
                csv_string = df.to_csv(index=False, encoding='utf-8')
                csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
                return html.Div([html.Label("Showing top 20 materials - download csv for full results" if df.shape[0] >= 20 else ""),
                                 html.A("Download data as csv",
                                        id="download-link",
                                        download="matscholar_data.csv",
                                        href=csv_string,
                                        target="_blank"),
                                 gen_output_matsearch(result[:20])])

    @app.callback(
        [Output("search-input", "style"), Output("material-search-panel", "style"), Output("filter-boxes", "style")],
        [Input("search-radio", "value")],
        [State("search-radio", "value")]
    )
    def toggle_inputs(radio_in, radio_val):
        if radio_val == "search":
            return {"display": "table-cell", "width": "100%"}, {"display": "none"}, {'width': '25%', 'float': 'left', 'display': 'inline-block'}
        elif radio_val == "summary":
            return {"display": "none"}, {"display": "none"}, {'width': '25%', 'float': 'left', 'display': 'inline-block'}
        else:
            return {"display": "none"}, {"width": "250px", "display": "inline-block"}, {"display": "none"}


