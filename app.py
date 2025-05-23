from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/api/data-gmaps', methods=['GET'])
def dataGmaps():
    data_all = pd.read_csv('./static/data/df_gmaps_reviews.csv')
    reviews = data_all[['name', 'review', 'rating', 'location', 'type_rs']]
    count_reviews = len(reviews)

    location_filter = request.args.get('location', 'all')
    rating_filter = request.args.get('rating', 'all')
    type_filter = request.args.get('type', 'all')

    reviews['location'] = reviews['location'].str.lower().str.replace(r'\s+', '_', regex=True)

    # Filter 
    if location_filter != 'all':
        reviews = reviews[reviews['location'].str.contains(location_filter, case=False)]

    if rating_filter != 'all':
        try:
            rating_filter_value = float(rating_filter)
            reviews = reviews[reviews['rating'] == rating_filter_value]
        except ValueError:
            return jsonify({"error": "Invalid ratingFilter value"}), 400

    if type_filter != 'all':
        reviews = reviews[reviews['type_rs'].str.lower() == type_filter.lower()]

    # Pagination
    page = int(request.args.get('page', 1))
    per_page = 10
    total_reviews = reviews.shape[0]
    total_pages = (total_reviews // per_page) + (1 if total_reviews % per_page > 0 else 0)

    paginated_reviews = reviews.iloc[(page - 1) * per_page : page * per_page]

    start_page = max(page - 5, 1)
    end_page = min(page + 5, total_pages)
    page_range = list(range(start_page, end_page + 1))

    return jsonify({
        "reviews": paginated_reviews.to_dict(orient='records'),
        "pagination": {
            "page": page,
            "total_pages": total_pages,
            "page_range": page_range
        },
        "filters": {
            "location_filter": location_filter,
            "rating_filter": rating_filter
        },
        "count": count_reviews
    })


@app.route('/api/data-gmaps/preprocessing/<step>', methods=['GET'])
def dataGmapsPreprocessing(step):
    data_all = pd.read_csv('./static/data/df_clean.csv')
    if step == 'case-folding':
        reviews = data_all[['casefold_text', 'rating', 'location', 'type_rs']]
    elif step == 'data-cleaning':
        reviews = data_all[['clean_text', 'rating', 'location', 'type_rs']]
    elif step == 'normalization':
        reviews = data_all[['slang_text', 'rating', 'location', 'type_rs']]
    elif step == 'tokenization':
        reviews = data_all[['token_text', 'rating', 'location', 'type_rs']]
    else:
        reviews = data_all[['stemmed_text_done', 'rating', 'location', 'type_rs']]

    count_reviews = len(reviews)

    location_filter = request.args.get('location', 'all')
    rating_filter = request.args.get('rating', 'all')
    type_filter = request.args.get('type', 'all')

    reviews['location'] = reviews['location'].str.lower().str.replace(r'\s+', '_', regex=True)

    # Filter 
    if location_filter != 'all':
        reviews = reviews[reviews['location'].str.contains(location_filter, case=False)]

    if rating_filter != 'all':
        try:
            rating_filter_value = float(rating_filter)
            reviews = reviews[reviews['rating'] == rating_filter_value]
        except ValueError:
            return jsonify({"error": "Invalid ratingFilter value"}), 400

    if type_filter != 'all':
        reviews = reviews[reviews['type_rs'].str.lower() == type_filter.lower()]

    # Pagination
    page = int(request.args.get('page', 1))
    per_page = 10
    total_reviews = reviews.shape[0]
    total_pages = (total_reviews // per_page) + (1 if total_reviews % per_page > 0 else 0)

    paginated_reviews = reviews.iloc[(page - 1) * per_page : page * per_page]

    start_page = max(page - 5, 1)
    end_page = min(page + 5, total_pages)
    page_range = list(range(start_page, end_page + 1))

    return jsonify({
        "reviews": paginated_reviews.to_dict(orient='records'),
        "pagination": {
            "page": page,
            "total_pages": total_pages,
            "page_range": page_range
        },
        "filters": {
            "location_filter": location_filter,
            "rating_filter": rating_filter
        },
        "count": count_reviews,
        "step": step
    })


if __name__ == '__main__':
    app.run(debug=True)
