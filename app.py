from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

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
    def format_kata(step):
        text = re.sub(r'-', ' ', step)
        return text.title()

    data_all = pd.read_csv('./static/data/data_topic_rs_3.csv')
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


    step_cleaned = format_kata(step)

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
        "step": step_cleaned
    })

@app.route('/api/sentiment-analysis', methods=['GET'])
def sentimentAnalysisReview():
    data =  pd.read_csv('./static/data/data_topic_rs_3.csv')
    sentiment = data[['rating', 'type_rs','stemmed_text_done', 'location', 'label', 'predicted_sentiment']]

    sentiment['predicted_sentiment'] = sentiment['predicted_sentiment'].replace({1: 'Positif', -1: 'Negatif'})

    # count_sentiment_positif = sentiment[sentiment['label'].str.contains('Positif', case=False)].shape[0]
    # count_sentiment_negatif = sentiment[sentiment['label'].str.contains('Negatif', case=False)].shape[0]
    # count_prediction_positif = sentiment[sentiment['predicted_sentiment'].str.contains('Positif', case=False)].shape[0]
    # count_prediction_negatif = sentiment[sentiment['predicted_sentiment'].str.contains('Negatif', case=False)].shape[0]

    # Pisahkan ulasan berdasarkan label Positif dan Negatif
    # positive_reviews = sentiment[sentiment['predicted_sentiment'] == 'Positif']
    # negative_reviews = sentiment[sentiment['predicted_sentiment'] == 'Negatif']

    # # Membuat model CountVectorizer untuk Positif
    # vectorizer_pos = CountVectorizer(stop_words='english', max_features=25)
    # X_pos = vectorizer_pos.fit_transform(positive_reviews['stemmed_text_done'])
    # words_pos = vectorizer_pos.get_feature_names_out()
    # frequencies_pos = X_pos.sum(axis=0).A1
    # word_freq_pos = pd.DataFrame(list(zip(words_pos, frequencies_pos)), columns=['Word', 'Frequency'])
    # word_freq_pos = word_freq_pos.sort_values(by='Frequency', ascending=False).head(25)

    # # Membuat model CountVectorizer untuk Negatif
    # vectorizer_neg = CountVectorizer(stop_words='english', max_features=25)
    # X_neg = vectorizer_neg.fit_transform(negative_reviews['stemmed_text_done'])
    # words_neg = vectorizer_neg.get_feature_names_out()
    # frequencies_neg = X_neg.sum(axis=0).A1
    # word_freq_neg = pd.DataFrame(list(zip(words_neg, frequencies_neg)), columns=['Word', 'Frequency'])
    # word_freq_neg = word_freq_neg.sort_values(by='Frequency', ascending=False).head(25)

    location_filter = request.args.get('location', 'all')
    rating_filter = request.args.get('rating', 'all')
    type_filter = request.args.get('type', 'all')

    sentiment['location'] = sentiment['location'].str.lower().str.replace(r'\s+', '_', regex=True)

    # Filter 
    if location_filter != 'all':
        sentiment = sentiment[sentiment['location'].str.contains(location_filter, case=False)]

    if rating_filter != 'all':
        try:
            rating_filter_value = float(rating_filter)
            sentiment = sentiment[sentiment['rating'] == rating_filter_value]
        except ValueError:
            return jsonify({"error": "Invalid ratingFilter value"}), 400

    if type_filter != 'all':
        sentiment = sentiment[sentiment['type_rs'].str.lower() == type_filter.lower()]

    # Pagination
    per_page = 10
    page = request.args.get('page', 1, type=int)

    start = (page - 1) * per_page
    end = start + per_page

    paginated_reviews = sentiment.iloc[start:end]

    # Total pages
    total_reviews = len(sentiment)
    total_pages = (total_reviews + per_page - 1) // per_page

    # Rentang halaman untuk pagination
    num_range = 2
    start_range = max(1, page - num_range)
    end_range = min(total_pages, page + num_range)
    page_range = list(range(start_range, end_range + 1))

    return jsonify({
        "sentiment": paginated_reviews.to_dict(orient='records'),
        "pagination": {
            "page": page,
            "total_pages": total_pages,
            "page_range": page_range
        },
        "filters": {
            "location_filter": location_filter,
            "rating_filter": rating_filter
        },

        # "count_sentiment_positif": count_sentiment_positif,
        # "count_sentiment_negatif": count_sentiment_negatif,
        # "count_prediction_positif": count_prediction_positif,
        # "count_prediction_negatif": count_prediction_negatif
    })

@app.route('/api/sentiment-analysis/word-cloud/type-a', methods=['GET'])
def wordCloudA():
    data =  pd.read_csv('./static/data/data_topic_rs_3.csv')
    sentiment = data[['rating', 'type_rs','stemmed_text_done', 'location', 'label', 'predicted_sentiment']]
    sentiment = sentiment[sentiment['type_rs'] == 'A']

    sentiment['predicted_sentiment'] = sentiment['predicted_sentiment'].replace({1: 'Positif', -1: 'Negatif'})

    # Pisahkan ulasan berdasarkan label Positif dan Negatif
    positive_reviews = sentiment[sentiment['predicted_sentiment'] == 'Positif']
    negative_reviews = sentiment[sentiment['predicted_sentiment'] == 'Negatif']

    # Membuat model CountVectorizer untuk Positif
    vectorizer_pos = CountVectorizer(stop_words='english', max_features=25)
    X_pos = vectorizer_pos.fit_transform(positive_reviews['stemmed_text_done'])
    words_pos = vectorizer_pos.get_feature_names_out()
    frequencies_pos = X_pos.sum(axis=0).A1
    word_freq_pos = pd.DataFrame(list(zip(words_pos, frequencies_pos)), columns=['Word', 'Frequency'])
    word_freq_pos = word_freq_pos.sort_values(by='Frequency', ascending=False).head(25)

    # Membuat model CountVectorizer untuk Negatif
    vectorizer_neg = CountVectorizer(stop_words='english', max_features=25)
    X_neg = vectorizer_neg.fit_transform(negative_reviews['stemmed_text_done'])
    words_neg = vectorizer_neg.get_feature_names_out()
    frequencies_neg = X_neg.sum(axis=0).A1
    word_freq_neg = pd.DataFrame(list(zip(words_neg, frequencies_neg)), columns=['Word', 'Frequency'])
    word_freq_neg = word_freq_neg.sort_values(by='Frequency', ascending=False).head(25)

    return jsonify({

        "word_freq_pos": word_freq_pos.to_dict(orient='records'),
        "word_freq_neg": word_freq_neg.to_dict(orient='records'),
    })

@app.route('/api/sentiment-analysis/word-cloud/type-b', methods=['GET'])
def wordCloudB():
    data =  pd.read_csv('./static/data/data_topic_rs_3.csv')
    sentiment = data[['rating', 'type_rs','stemmed_text_done', 'location', 'label', 'predicted_sentiment']]
    sentiment = sentiment[sentiment['type_rs'] == 'B']

    sentiment['predicted_sentiment'] = sentiment['predicted_sentiment'].replace({1: 'Positif', -1: 'Negatif'})

    # Pisahkan ulasan berdasarkan label Positif dan Negatif
    positive_reviews = sentiment[sentiment['predicted_sentiment'] == 'Positif']
    negative_reviews = sentiment[sentiment['predicted_sentiment'] == 'Negatif']

    # Membuat model CountVectorizer untuk Positif
    vectorizer_pos = CountVectorizer(stop_words='english', max_features=25)
    X_pos = vectorizer_pos.fit_transform(positive_reviews['stemmed_text_done'])
    words_pos = vectorizer_pos.get_feature_names_out()
    frequencies_pos = X_pos.sum(axis=0).A1
    word_freq_pos = pd.DataFrame(list(zip(words_pos, frequencies_pos)), columns=['Word', 'Frequency'])
    word_freq_pos = word_freq_pos.sort_values(by='Frequency', ascending=False).head(25)

    # Membuat model CountVectorizer untuk Negatif
    vectorizer_neg = CountVectorizer(stop_words='english', max_features=25)
    X_neg = vectorizer_neg.fit_transform(negative_reviews['stemmed_text_done'])
    words_neg = vectorizer_neg.get_feature_names_out()
    frequencies_neg = X_neg.sum(axis=0).A1
    word_freq_neg = pd.DataFrame(list(zip(words_neg, frequencies_neg)), columns=['Word', 'Frequency'])
    word_freq_neg = word_freq_neg.sort_values(by='Frequency', ascending=False).head(25)

    return jsonify({

        "word_freq_pos": word_freq_pos.to_dict(orient='records'),
        "word_freq_neg": word_freq_neg.to_dict(orient='records'),
    })

@app.route('/api/sentiment-analysis/word-cloud/type-c', methods=['GET'])
def wordCloudC():
    data =  pd.read_csv('./static/data/data_topic_rs_3.csv')
    sentiment = data[['rating', 'type_rs','stemmed_text_done', 'location', 'label', 'predicted_sentiment']]
    sentiment = sentiment[sentiment['type_rs'] == 'C']

    sentiment['predicted_sentiment'] = sentiment['predicted_sentiment'].replace({1: 'Positif', -1: 'Negatif'})

    # Pisahkan ulasan berdasarkan label Positif dan Negatif
    positive_reviews = sentiment[sentiment['predicted_sentiment'] == 'Positif']
    negative_reviews = sentiment[sentiment['predicted_sentiment'] == 'Negatif']

    # Membuat model CountVectorizer untuk Positif
    vectorizer_pos = CountVectorizer(stop_words='english', max_features=25)
    X_pos = vectorizer_pos.fit_transform(positive_reviews['stemmed_text_done'])
    words_pos = vectorizer_pos.get_feature_names_out()
    frequencies_pos = X_pos.sum(axis=0).A1
    word_freq_pos = pd.DataFrame(list(zip(words_pos, frequencies_pos)), columns=['Word', 'Frequency'])
    word_freq_pos = word_freq_pos.sort_values(by='Frequency', ascending=False).head(25)

    # Membuat model CountVectorizer untuk Negatif
    vectorizer_neg = CountVectorizer(stop_words='english', max_features=25)
    X_neg = vectorizer_neg.fit_transform(negative_reviews['stemmed_text_done'])
    words_neg = vectorizer_neg.get_feature_names_out()
    frequencies_neg = X_neg.sum(axis=0).A1
    word_freq_neg = pd.DataFrame(list(zip(words_neg, frequencies_neg)), columns=['Word', 'Frequency'])
    word_freq_neg = word_freq_neg.sort_values(by='Frequency', ascending=False).head(25)

    return jsonify({

        "word_freq_pos": word_freq_pos.to_dict(orient='records'),
        "word_freq_neg": word_freq_neg.to_dict(orient='records'),
    })
@app.route('/api/sentiment-analysis/word-cloud/type-d', methods=['GET'])
def wordCloudD():
    data =  pd.read_csv('./static/data/data_topic_rs_3.csv')
    sentiment = data[['rating', 'type_rs','stemmed_text_done', 'location', 'label', 'predicted_sentiment']]
    sentiment = sentiment[sentiment['type_rs'] == 'D']

    sentiment['predicted_sentiment'] = sentiment['predicted_sentiment'].replace({1: 'Positif', -1: 'Negatif'})

    # Pisahkan ulasan berdasarkan label Positif dan Negatif
    positive_reviews = sentiment[sentiment['predicted_sentiment'] == 'Positif']
    negative_reviews = sentiment[sentiment['predicted_sentiment'] == 'Negatif']

    # Membuat model CountVectorizer untuk Positif
    vectorizer_pos = CountVectorizer(stop_words='english', max_features=25)
    X_pos = vectorizer_pos.fit_transform(positive_reviews['stemmed_text_done'])
    words_pos = vectorizer_pos.get_feature_names_out()
    frequencies_pos = X_pos.sum(axis=0).A1
    word_freq_pos = pd.DataFrame(list(zip(words_pos, frequencies_pos)), columns=['Word', 'Frequency'])
    word_freq_pos = word_freq_pos.sort_values(by='Frequency', ascending=False).head(25)

    # Membuat model CountVectorizer untuk Negatif
    vectorizer_neg = CountVectorizer(stop_words='english', max_features=25)
    X_neg = vectorizer_neg.fit_transform(negative_reviews['stemmed_text_done'])
    words_neg = vectorizer_neg.get_feature_names_out()
    frequencies_neg = X_neg.sum(axis=0).A1
    word_freq_neg = pd.DataFrame(list(zip(words_neg, frequencies_neg)), columns=['Word', 'Frequency'])
    word_freq_neg = word_freq_neg.sort_values(by='Frequency', ascending=False).head(25)

    return jsonify({

        "word_freq_pos": word_freq_pos.to_dict(orient='records'),
        "word_freq_neg": word_freq_neg.to_dict(orient='records'),
    })




if __name__ == '__main__':
    app.run(debug=True)
