import pandas as pd
from plotly.subplots import make_subplots
import global_data
import plotly.express as px
import database.db_queries as db
import pycountry
import plotly.graph_objects as go


def create_piechart_conf_countries(conference):
    data = db.obtain_countries_from_conference(conference, global_data.FIRST_YEAR, global_data.LAST_YEAR)
    df = pd.DataFrame(data)

    figs = []
    for year in df.columns:
        fig = px.pie(
            names=df.index,
            values=df[year],
            template="plotly",
        )
        fig.update_traces(textinfo='percent+label', textposition="inside")
        figs.append(fig)

    subplot = make_subplots(rows=2, cols=6, specs=[[{'type': 'pie'}] * 6] * 2, subplot_titles=list(df.columns))
    for i, fig in enumerate(figs):
        row = i // 6 + 1
        col = i % 6 + 1
        subplot.add_trace(fig.data[0], row=row, col=col)

    subplot.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Countries of {conference}</b>",
    )
    subplot.show()
    #subplot.write_html(f'../html/piechart_{conference}_countries.html')


def scatter_geo_countries(conference):
    data = db.obtain_countries_from_conference(conference, global_data.FIRST_YEAR, global_data.LAST_YEAR)
    df = pd.DataFrame(data)

    new_df = df.reset_index().melt(id_vars='index', var_name='Year', value_name='Repetitions')
    new_df.columns = ['Country', 'Year', 'Repetitions']

    new_df = new_df[new_df['Country'] != 'None']
    new_df['Country_ISO3'] = new_df['Country'].apply(lambda x: pycountry.countries.get(alpha_2=x).alpha_3 if pd.notnull(x) else None)
    new_df['Country Name'] = new_df['Country_ISO3'].apply(lambda x: pycountry.countries.get(alpha_3=x) if pd.notnull(x) else None)
    new_df.dropna(subset=['Repetitions'], inplace=True)

    fig = px.scatter_geo(
        new_df,
        locations="Country_ISO3",
        locationmode="ISO-3",
        hover_name="Country_ISO3",
        size="Repetitions",
        color="Repetitions",
        projection="natural earth",
        size_max=40,
        animation_frame="Year",
        animation_group="Country_ISO3",
        color_continuous_scale='portland',
        labels = {'Repetitions': 'Institutions from this country', 'Country_ISO3':'Country Code'}
    )
    fig.update_geos(showland=True, landcolor="lightgray")
    fig.update_layout(
        coloraxis=dict(
            cmin=new_df['Repetitions'].min(),
            cmax=new_df['Repetitions'].max(),
            colorbar=dict(
                title='Number of institutions',
                title_font = dict(size=18, family="Arial, sans-serif", color="black")
            )
        ),
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Number of institutions from each country in {conference}</b>"
    )
    fig.show()
    #fig.write_html(f'../html/scatter_geo_countries_{conference}.html')



def linechart_countries_conference():
    conf_res = {}
    for conf in global_data.conferences:
        data = db.obtain_countries_from_conference(conf, global_data.FIRST_YEAR, global_data.LAST_YEAR)
        conf_res[conf] = data

    df = pd.DataFrame(conf_res)
    df_melted = pd.melt(df.reset_index(), id_vars=['index'], var_name='Conference', value_name='Repetitions')
    df_melted['No Data'] =  df_melted['Repetitions'].apply(lambda rep: rep.get('None', 0))
    df_melted['Num Countries'] = df_melted['Repetitions'].apply(lambda rep: sum(1 for key in rep.keys() if key != 'None'))
    df_melted = df_melted.rename(columns={'index': 'Year'})

    fig = px.line(df_melted, x='Year', y='Num Countries', color='Conference')
    line_dash_dict = {'middleware': 'dash', 'cloud': 'dash', 'nsdi': 'dash'}
    for conference, line_dash in line_dash_dict.items():
        conference_data = df_melted[df_melted['Conference'] == conference]
        fig.add_trace(go.Scatter(
            x=conference_data['Year'],
            y=conference_data['Num Countries'] + conference_data['No Data'],
            mode='lines',
            name=f'{conference} with None Countries',
            line=dict(dash=line_dash)
        ))
    fig.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Number of countries per conference</b>",
    )
    fig.show()
    #fig.write_html(f'../html/NEW_linechart_num_countries.html')


def create_piechart_members_with_papers(conference):
    data = db.count_members_with_papers(conference, global_data.FIRST_YEAR, global_data.LAST_YEAR)
    df = pd.DataFrame(data)
    df.loc['Members without papers'] = df.loc['All members'] - df.loc['Members with papers']
    df = df.drop('All members')

    figs = []
    for year in df.columns:
        fig = px.pie(
            names=df.index,
            values=list(data[year].values()),
            title=f'Committee Members with papers in {year}',
            template = 'plotly',
            hole = 0.3
        )
        fig.update_traces(textinfo="percent", textposition="inside")
        figs.append(fig)

    subplot = make_subplots(rows=2, cols=6, specs=[[{'type': 'pie'}] * 6] * 2, subplot_titles=list(df.columns))
    for i, fig in enumerate(figs):
        row = i // 6 + 1
        col = i % 6 + 1
        subplot.add_trace(fig.data[0], row=row, col=col)

    subplot.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Members that published a paper in {conference}</b>",
    )
    subplot.show()
    #subplot.write_html(f'../html/piechart_members_{conference}_with_papers.html')



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
    fig.update_layout(width=500, height=500, title_text=f"<b style='font-size: 24px;'>Number of Countries on each conference</b>")
    fig.show()
    #fig.write_html('../html/barchart_countries_conf.html')



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
        fig = px.line(df, x='Year', y='Value', color='Type',
                labels={'Value': 'Number of Papers Published', 'Year': 'Year', 'Type': 'Type of Paper'})

        fig.update_traces(name=f'With {country}', selector=dict(name='With Country'))
        fig.update_traces(name=f'Without {country}', selector=dict(name='Without Country'))
        fig.update_layout(
            showlegend=True,
            title_text=f"<b style='font-size: 24px;'>{country} institutions on {conf} papers</b>",
        )
        fig.show()
        #fig.write_html(f'../html/{conf}_how_many_papers_have_us.html')


def linechart_only_us_papers():
    conf_res = {}
    for conf in global_data.conferences:
        data = db.obtain_num_papers_only_us(conf, global_data.FIRST_YEAR, global_data.LAST_YEAR)
        conf_res[conf] = data

    df = pd.DataFrame(conf_res)
    df_melted = pd.melt(df.reset_index(), id_vars=['index'], var_name='Conference', value_name='Num Papers')
    df_melted.columns = ['Year', 'Conference', 'Num Papers']

    fig = px.line(df_melted, x='Year', y='Num Papers', color='Conference')
    fig.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Number of papers with only USA institutions</b>",
    )
    fig.show()
    #fig.write_html('../html/linechart_only_us.html')


def linechart_num_papers():
    conf_res = {}
    for conf in global_data.conferences:
        data = db.obtain_num_papers(conf, global_data.FIRST_YEAR, global_data.LAST_YEAR)
        conf_res[conf] = data

    df = pd.DataFrame(conf_res)
    df_melted = pd.melt(df.reset_index(), id_vars=['index'], var_name='Conference', value_name='Num_Papers')
    df_melted.columns = ['Year', 'Conference', 'Num Papers']

    fig = px.line(df_melted, x='Year', y='Num Papers', color='Conference')
    fig.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Total number of papers</b>",
    )
    fig.show()
    #fig.write_html('../html/linechart_num_papers.html')



if __name__ == '__main__':
    create_how_many_papers_have_a_country("US")
    create_barchart_conf_countries()
    linechart_only_us_papers()
    linechart_num_papers()
    linechart_countries_conference()
    for conf in global_data.conferences:
        scatter_geo_countries(conf)
        create_piechart_members_with_papers(conf)
        create_piechart_conf_countries(conf)