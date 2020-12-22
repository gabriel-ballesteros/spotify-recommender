from flask import render_template, make_response
from app import app
import base64
from io import BytesIO
from matplotlib.figure import Figure
import seaborn as sns

def generate_plot():
    pass

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', page='home')

@app.route('/dataset')
def dataset():
    fig = Figure(figsize=(16,6))
    ax = fig.subplots()
    sns.set_style("whitegrid")
    plot=sns.barplot(x=[2010,2011,2012,2013,2014,2015,2016], y=[112,121,130,102,119,109,140], color='lightskyblue', ax=ax)
    #plot.set_xlabel("Year",fontsize=20)
    #plot.set_ylabel("Album count",fontsize=20)
    plot.tick_params(labelsize=15)
    buf = BytesIO()
    fig.savefig(buf, format="png",bbox_inches='tight')
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    artist_list = ['Aerosmith','Bon Jovi','Calvin Harris']
    
    return render_template('dataset.html', page='dataset', artist_list=artist_list, dist_year=data)

@app.route('/about')
def about():
    return render_template('about.html', page='about')