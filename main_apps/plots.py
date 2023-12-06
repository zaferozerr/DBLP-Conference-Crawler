import pandas as pd
from plotly.subplots import make_subplots
import global_data
import plotly.express as px
import database.db_queries as db
import pycountry


def create_piechart_conf_countries(conference):
    data = db.obtain_countries_from_conference(conference, global_data.FIRST_YEAR, global_data.LAST_YEAR)
    df = pd.DataFrame(data)

    figs = []
    for year in df.columns:
        fig = px.pie(
            names=df.index,
            values=df[year],
            title=f'{conference} {year}',
            template="plotly",
        )
        fig.update_traces(textinfo="label", textposition="inside")
        figs.append(fig)

    subplot = make_subplots(rows=2, cols=6, specs=[[{'type': 'pie'}] * 6] * 2, subplot_titles=list(df.columns))
    for i, fig in enumerate(figs):
        row = i // 6 + 1
        col = i % 6 + 1
        subplot.add_trace(fig.data[0], row=row, col=col)

    subplot.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>11 years of {conference}</b>",
    )
    subplot.show()


def create_heat_map_countries(conference):
    data = db.obtain_countries_from_conference(conference, global_data.FIRST_YEAR, global_data.LAST_YEAR)
    df = pd.DataFrame(data).T.reset_index()
    df = pd.melt(df, id_vars=['index'], var_name='Country', value_name='Frequency')
    df = df.rename(columns={'index': 'Year'})

    # Filter None values
    df = df[df['Country'] != 'None']

    df['Country_ISO3'] = df['Country'].apply(lambda x: pycountry.countries.get(alpha_2=x).alpha_3 if pd.notnull(x) else None)

    #df['Frequency'].fillna(0, inplace=True)
    df.dropna(subset=['Frequency'], inplace=True)

    fig = px.choropleth(
        df,
        locations='Country_ISO3',
        color='Frequency',
        color_continuous_scale=px.colors.sequential.Plasma,
        labels={'Frequency': 'Frequency'},
        animation_frame='Year',
        range_color=[1, df['Frequency'].max()]
    )
    fig.update_geos(showland=True, landcolor="lightgray")

    fig.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Number of times that a country appeared on {conference}</b>",
    )
    # show plot
    fig.show()


def create_piechart_members_with_papers(conference):
    data = db.count_members_with_papers(conference, global_data.FIRST_YEAR, global_data.LAST_YEAR)
    df = pd.DataFrame(data)

    figs = []
    for year in df.columns:
        fig = px.pie(
            names=list(data[year].keys()),
            values=list(data[year].values()),
            title=f'Committee Members with papers in {year}',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        fig.update_traces(textinfo="value", textposition="inside")
        figs.append(fig)

    subplot = make_subplots(rows=2, cols=6, specs=[[{'type': 'pie'}] * 6] * 2, subplot_titles=list(df.columns))
    for i, fig in enumerate(figs):
        row = i // 6 + 1
        col = i % 6 + 1
        subplot.add_trace(fig.data[0], row=row, col=col)

    subplot.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Committee members that have published a paper in {conference}</b>",
    )
    subplot.show()



def create_barchart_conf_countries():
    res = {}
    for conf in global_data.conferences:
        data = db.obtain_countries_from_conference(conf, global_data.FIRST_YEAR, global_data.LAST_YEAR)

        unique_countries = set()
        for year_data in data.values():
            for country in year_data.keys():
                if country != 'None':
                    unique_countries.add(country)

        res[conf] = len(unique_countries)

    conferences = list(res.keys())
    values = list(res.values())

    fig = px.bar(x=conferences, y=values, labels={'x': 'Conference', 'y': 'Number of Countries'}, color=conferences, color_continuous_scale='Viridis')
    fig.update_layout(title=f'Number of Countries on each conference', width=800, height=800)
    fig.show()


def create_how_many_papers_have_a_country(country):
    results_for_conference = {}
    for conf in global_data.conferences:
        data = db.papers_by_countries(conf, global_data.FIRST_YEAR, global_data.LAST_YEAR)
        res = {"Year": [], "Type": [], "Value": []}
        for year in data.keys():
            count = {"With Country": 0, "Without Country": 0}      # [0] -> with country  [1] -> without country
            for elem in data[year]:
                title, countries = elem
                found_country = False
                if countries is None: continue
                for c in countries.split(","):
                    if c == country:
                        count["With Country"] = count.get("With Country") + 1
                        found_country = True
                        break
                if not found_country:
                    count["Without Country"] = count.get("Without Country") + 1

            res["Year"].append(year)
            res["Year"].append(year)
            res["Type"].append("With Country")
            res["Value"].append(count["With Country"])
            res["Type"].append("Without Country")
            res["Value"].append(count["Without Country"])
        results_for_conference[conf] = res

    for conf in global_data.conferences:
        df = pd.DataFrame(results_for_conference[conf])
        fig = px.bar(df, x='Year', y='Value', color='Type',
                     title=f"<b style='font-size: 24px;'>Number of papers in {conf} that some institution is from {country}</b>",
                     labels={'Value': 'Number of Papers Published', 'Year': 'Year', 'Type': 'Type of Paper'},
                     text_auto=True)

        fig.update_traces(name=f'With {country}', selector=dict(name='With Country'))
        fig.update_traces(name=f'Without {country}', selector=dict(name='Without Country'))

        fig.update_xaxes(tickmode='array', tickvals=df['Year'], ticktext=df['Year'])
        fig.show()


if __name__ == '__main__':
    create_how_many_papers_have_a_country("US")
    create_barchart_conf_countries()
    for conf in global_data.conferences:
        create_piechart_members_with_papers(conf)
        create_piechart_conf_countries(conf)
        create_heat_map_countries(conf)