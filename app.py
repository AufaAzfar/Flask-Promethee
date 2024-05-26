from flask import Flask, render_template, request
import matplotlib
matplotlib.use('agg')
from pyDecision.algorithm import promethee_ii
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load the data
data = pd.read_excel('/Users/aufazaydan/Downloads/promethee/skincaredata.xlsx')

# Functions to adjust price and skin type values
def adjust_price_values(df, price_preference):
    data = df.copy()

    if price_preference.lower() == 'cheap':
        data['Harga'] = data['Harga'].apply(lambda x: 6 - x)
    return data

def adjust_skin_type_values(df, skin_type_preference):
    data = df.copy()
    if skin_type_preference.lower() == 'sensitif':
        data['Jenis Kulit'] = data['Jenis Kulit'].apply(lambda x: 7 - x if x == 2 or x == 5 else x)
    elif skin_type_preference.lower() == 'berminyak':
        data['Jenis Kulit'] = data['Jenis Kulit'].apply(lambda x: 9 - x if x == 4 or x == 5 else x)
    elif skin_type_preference.lower() == 'kering':
        data['Jenis Kulit'] = data['Jenis Kulit'].apply(lambda x: 8 - x if x == 3 or x == 5 else x)
    return data

# Function to perform PROMETHEE II analysis and return top 3 products
def get_top_3_products(price_preference, skin_type_preference):
    df = data.copy()
    df = adjust_price_values(df, price_preference)
    df = adjust_skin_type_values(df, skin_type_preference)

    decision_matrix = df.iloc[:, 5:].values
    criteria_weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
    Q = [0.1, 0.1, 0.1, 0.1, 0.1]
    S = [0.1, 0.1, 0.1, 0.1, 0.1]
    P = [0.2, 0.2, 0.2, 0.2, 0.2]
    F = ['t2', 't2', 't2', 't2', 't2']

    result = promethee_ii(decision_matrix, criteria_weights, Q, S, P, F, graph=True)
    ranking = result[:, 1]
    ranked_indices = result[:, 0].astype(int) - 1
    sorted_indices = np.argsort(ranking)[::-1]

    top_3 = []
    for rank, sorted_index in enumerate(sorted_indices[:3], start=1):
        original_index = ranked_indices[sorted_index]
        product = {
            "ProductID": int(df['ProductID'].iloc[original_index]),
            "ProductName": df['Merk'].iloc[original_index],
            "Image": df['Gambar'].iloc[original_index],
            "RealPrice": int(df['Harga Asli'].iloc[original_index]),
            "RealSkinType": df['Jenis Kulit'].iloc[original_index],
            "Rating": int(df['Rating'].iloc[original_index])
        }
        top_3.append(product)

    return top_3

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        price_preference = request.form['price_preference']
        skin_type_preference = request.form['skin_type_preference']
        top_3_products = get_top_3_products(price_preference, skin_type_preference)
        return render_template('result.html', top_3_products=top_3_products)
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        price_preference = request.form['price_preference']
        skin_type_preference = request.form['skin_type_preference']
        top_3_products = get_top_3_products(price_preference, skin_type_preference)
        return render_template('result.html', top_3_products=top_3_products)
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
