from flask import Flask
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from IPython.display import Image
from flask import send_file


app = Flask(__name__)
 

def split_data(dframe):
    min_year = dframe['year'].min()
    max_year = dframe['year'].max()
    
    data_year_wise = {
        year : dframe[dframe['year'] == year] for year in range(min_year, max_year + 1)
    }
    
    return data_year_wise

def categorize_crimes_district(data_source, state_unit, district=None):
    crime_list = list(data_source[2001].columns[3:])
    all_crimes_year_wise = {}
    for (y, d) in data_source.items():
        
        y_df = d[d['district'] == district.title()]
       
        if state_unit:
            y_df = y_df[y_df['state_unit'] == state_unit.title()]
        crime_dict = {col : y_df[col].sum() for col in crime_list}
        all_crimes_year_wise[y] = crime_dict
    return all_crimes_year_wise


def plot_overall_crimes_by_year(data_source, state_unit=None, kind='bar'):
    crimes_data = categorize_crimes(data_source=data_source, state_unit=state_unit)
    year_sum_crimes = {y : sum(list(cr.values())) for (y, cr) in crimes_data.items()}
    
    y_keys = list(year_sum_crimes.keys())
    y_vals = list(year_sum_crimes.values())
    
    t = 'Total Crimes - {}'
    title = t.format(state_unit.title()) if state_unit else t.format('India')

    fig = go.Figure()
    
    if kind == 'bar':
        # trace = go.Bar(x=y_keys, y=y_vals)
        fig.add_trace(go.Bar(x=y_keys, y=y_vals))
    elif kind == 'barh':
        # trace = go.Bar(x=y_keys, y=y_vals)
        fig.add_trace(go.Bar(x=y_vals, y=y_keys, orientation='h'))
    elif kind == 'pie':
        # trace = go.Pie(labels=y_keys, values=y_vals)
        fig.add_trace(go.Pie(labels=y_keys, values=y_vals))
    elif kind == 'area':
      fig.add_trace(go.Scatter(
          name = title,
          x = y_keys,
          y = y_vals,
          stackgroup = 'one',
          mode = 'none'
      ))
    elif kind == 'line':
      fig.add_trace(go.Scatter(
          name = title,
          x = y_keys,
          y = y_vals
      ))
    elif kind == 'scatter':
      fig = px.scatter(x = y_keys, y = y_vals)

    elif kind == 'box':
      df = px.data.tips()
      fig = px.box(df, y= y_vals)



    fig.update_layout(
        height=400,
        width=600,
        title=title,
        margin=dict(l=0, r=0, b=0, t=100)
    )
    
    # fig.update_layout(layout=layout)
    
    # return fig.show()
    
    # return None

    # return str( fig.to_image(format="png"))
    base64 =fig.to_image(format="png")


    return base64
 

def categorize_crimes(data_source, state_unit=None):
    crime_list = list(data_source[2001].columns[3:])


    all_crimes_year_wise = {}
    for (y, d) in data_source.items():
        y_df = d[d['district'].str.contains('Total')]
        if state_unit:
            y_df = y_df[y_df['state_unit'] == state_unit.title()]
        crime_dict = {col : y_df[col].sum() for col in crime_list}
        all_crimes_year_wise[y] = crime_dict
    
    return all_crimes_year_wise

@app.route("/")
def home_view():
       path = Path("./crimes_against_women_2001-2014.csv")
       df = pd.read_csv(path, index_col=0)
       df.columns = ['state_unit', 'district', 'year', 'rape', 'kidnap_abduction', 'dowry_deaths', 
              'women_assault', 'women_insult', 'husband_relative_cruelty', 'girl_importation']
       df.index = list(range(df.shape[0]))
       for col in df.columns:
        df[col] = df[col].apply(lambda x : x.title() if isinstance(x, str) else x)

        replacements = {
             'A & N Islands' : 'Andaman and Nicobar',
             'A&N Islands' : 'Andaman and Nicobar',
             'Daman & Diu' : 'Daman and Diu',
             'Delhi Ut' : 'Delhi',
             'D & N Haveli' : 'Dadra and Nagar Haveli',
             'D&N Haveli' : 'Dadra and Nagar Haveli',
             'Odisha' : 'Orissa',
             'Jammu & Kashmir' : 'Jammu and Kashmir'
        }

        for (o, r) in replacements.items():
            df['state_unit'].replace(to_replace=o, value=r, inplace=True)

        data_splits = split_data(dframe=df)

        result = plot_overall_crimes_by_year(data_source=data_splits,state_unit = "West Bengal", kind = 'area')
        
       return send_file(result,download_name='logo.png',mimetype='image/png')

