import pandas as pd
from plotly.subplots import make_subplots
import global_data
import plotly.express as px
import database.db_queries as db
import pycountry
import plotly.graph_objects as go


def piechart_countries(conference):
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
    #subplot.show()
    subplot.write_html(f'../html/{conference}_piechart_countries.html')


def scatter_geo_countries(conference):
    data = db.obtain_countries_from_conference(conference, global_data.FIRST_YEAR, global_data.LAST_YEAR)
    df = pd.DataFrame(data)

    df = df.reset_index().melt(id_vars='index', var_name='Year', value_name='Repetitions')
    df.columns = ['Country', 'Year', 'Repetitions']

    df = df[df['Country'] != 'None']
    df['Country_ISO3'] = df['Country'].apply(lambda x: pycountry.countries.get(alpha_2=x).alpha_3 if pd.notnull(x) else None)
    df['Country Name'] = df['Country_ISO3'].apply(lambda x: pycountry.countries.get(alpha_3=x) if pd.notnull(x) else None)
    df.dropna(subset=['Repetitions'], inplace=True)

    fig = px.scatter_geo(df,
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
            cmin=df['Repetitions'].min(),
            cmax=df['Repetitions'].max(),
            colorbar=dict(
                title='Number of institutions',
                title_font = dict(size=18, family="Arial, sans-serif", color="black")
            )
        ),
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Number of institutions from each country in {conference}</b>"
    )
    #fig.show()
    fig.write_html(f'../html/{conference}_scatter_geo_countries.html')



def num_countries_per_conference():
    conf_res = {}
    for conf in global_data.conferences:
        data = db.obtain_countries_from_conference(conf, global_data.FIRST_YEAR, global_data.LAST_YEAR)
        conf_res[conf] = data

    df = pd.DataFrame(conf_res)
    df = pd.melt(df.reset_index(), id_vars=['index'], var_name='Conference', value_name='Repetitions')
    df['No Data'] =  df['Repetitions'].apply(lambda rep: rep.get('None', 0))
    df['Num Countries'] = df['Repetitions'].apply(lambda rep: sum(1 for key in rep.keys() if key != 'None'))
    df = df.rename(columns={'index': 'Year'})

    fig = px.line(df, x='Year', y='Num Countries', color='Conference', markers=True)
    line_dash_dict = {'middleware': 'dash', 'cloud': 'dash', 'nsdi': 'dash'}
    for conference, line_dash in line_dash_dict.items():
        conference_data = df[df['Conference'] == conference]
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
    #fig.show()
    fig.write_html(f'../html/num_countries_per_conference.html')


def committee_members_with_papers(conference):
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
            hole = 0.2,
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
    #subplot.show()
    subplot.write_html(f'../html/{conference}_committee_members_with_papers.html')


def country_ratio_in_conferences(country):
    res_per_conf = {}
    for conf in global_data.conferences:
        data = db.papers_by_countries(conf, global_data.FIRST_YEAR, global_data.LAST_YEAR, country)
        result = {}
        for year, elem in data.items():
            result[year] = elem['Only Country'] / elem['Total']
        res_per_conf[conf] = result

    df = pd.DataFrame(res_per_conf)
    df = pd.melt(df.reset_index(), id_vars=['index'], var_name='Conference', value_name='Ratio')
    df.columns = ['Year', 'Conference', 'Ratio']

    fig = px.line(df, x='Year', y='Ratio', color='Conference',
                labels={'Ratio': f'% of papers from {country}'}, markers=True)
    fig.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Ratio of papers from {country}</b>")

    #fig.show()
    fig.write_html(f'../html/{country}_ratio_in_conferences.html')


def linechart_only_us_papers():
    conf_res = {}
    for conf in global_data.conferences:
        data = db.obtain_num_papers_only_us(conf, global_data.FIRST_YEAR, global_data.LAST_YEAR)
        conf_res[conf] = data

    df = pd.DataFrame(conf_res)
    df = pd.melt(df.reset_index(), id_vars=['index'], var_name='Conference', value_name='Num Papers')
    df.columns = ['Year', 'Conference', 'Num Papers']

    fig = px.line(df, x='Year', y='Num Papers', color='Conference')
    fig.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Number of papers with only USA institutions</b>",
    )
    #fig.show()
    fig.write_html('../html/linechart_only_us.html')


def linechart_num_papers():
    conf_res = {}
    for conf in global_data.conferences:
        data = db.obtain_num_papers(conf, global_data.FIRST_YEAR, global_data.LAST_YEAR)
        conf_res[conf] = data

    df = pd.DataFrame(conf_res)
    df = pd.melt(df.reset_index(), id_vars=['index'], var_name='Conference', value_name='Num_Papers')
    df.columns = ['Year', 'Conference', 'Num Papers']

    fig = px.line(df, x='Year', y='Num Papers', color='Conference')
    fig.update_layout(
        showlegend=True,
        title_text=f"<b style='font-size: 24px;'>Total number of papers</b>",
    )
    #fig.show()
    fig.write_html('../html/linechart_num_papers.html')




if __name__ == '__main__':
    country_ratio_in_conferences("US")
    country_ratio_in_conferences("CN")
    country_ratio_in_conferences("DE")
    country_ratio_in_conferences("FR")
    linechart_only_us_papers()
    linechart_num_papers()
    num_countries_per_conference()
    for conf in global_data.conferences:
        scatter_geo_countries(conf)
        committee_members_with_papers(conf)
        piechart_countries(conf)