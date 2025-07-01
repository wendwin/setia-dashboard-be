import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from models import db, Topic, Suggestion, Summary
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

load_dotenv() 
frontend_url = os.environ.get("FRONTEND_URL")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": frontend_url}})

basedir = os.path.abspath(os.path.dirname(__file__))
database = os.environ.get("DATABASE")
# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, database)}"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db.init_app(app)

# with app.app_context():
#     db.create_all()


@app.route('/')
def index():
    return 'App running!'

@app.route('/api/data-gmaps', methods=['GET'])
def dataGmaps():
    data_all = pd.read_csv('./static/data/df_gmaps_reviews2.csv')
    reviews = data_all[['name', 'review', 'rating', 'location', 'type_rs']]

    count_reviews = len(reviews)
    count_positive = len(reviews[reviews['rating'].isin([4, 5])])
    count_negative = len(reviews[reviews['rating'].isin([1, 2, 3])])

    location_filter = request.args.get('location', 'all')
    rating_filter = request.args.get('rating', 'all')
    type_filter = request.args.get('type', 'all')

    reviews['location'] = reviews['location'].str.lower().str.replace(r'\s+', '_', regex=True)

    filtered_reviews = reviews.copy()
    # filter
    if location_filter != 'all':
        filtered_reviews = filtered_reviews[filtered_reviews['location'].str.contains(location_filter, case=False)]    

    if rating_filter != 'all':
        try:
            rating_filter_value = float(rating_filter)
            filtered_reviews = filtered_reviews[filtered_reviews['rating'] == rating_filter_value]
        except ValueError:
            return jsonify({"error": "Invalid ratingFilter value"}), 400       

    if type_filter != 'all':
        filtered_reviews = filtered_reviews[filtered_reviews['type_rs'].str.lower() == type_filter.lower()]    

    # Pagination hanya berdasarkan hasil filter
    page = int(request.args.get('page', 1))
    per_page = 10
    filtered_total = len(filtered_reviews)
    total_pages = (filtered_total // per_page) + (1 if filtered_total % per_page > 0 else 0)       

    paginated_reviews = filtered_reviews.iloc[(page - 1) * per_page : page * per_page]     

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
            "rating_filter": rating_filter,
            "type_filter": type_filter
        },
        "count": count_reviews,           
        "countPositive": count_positive,  
        "countNegative": count_negative   
    })


@app.route('/api/data-gmaps/preprocessing/<step>', methods=['GET'])
def dataGmapsPreprocessing(step):
    def format_kata(step):
        text = re.sub(r'-', ' ', step)
        return text.title()

    data_all = pd.read_csv('./static/data/data_topik_rs_4.csv')
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
    filtered_reviews = reviews.copy()
    # filter
    if location_filter != 'all':
        filtered_reviews = filtered_reviews[filtered_reviews['location'].str.contains(location_filter, case=False)]    

    if rating_filter != 'all':
        try:
            rating_filter_value = float(rating_filter)
            filtered_reviews = filtered_reviews[filtered_reviews['rating'] == rating_filter_value]
        except ValueError:
            return jsonify({"error": "Invalid ratingFilter value"}), 400       

    if type_filter != 'all':
        filtered_reviews = filtered_reviews[filtered_reviews['type_rs'].str.lower() == type_filter.lower()]    

    # Pagination hanya berdasarkan hasil filter
    page = int(request.args.get('page', 1))
    per_page = 10
    filtered_total = len(filtered_reviews)
    total_pages = (filtered_total // per_page) + (1 if filtered_total % per_page > 0 else 0)       

    paginated_reviews = filtered_reviews.iloc[(page - 1) * per_page : page * per_page]     

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
            "rating_filter": rating_filter,
             "type_filter": type_filter
        },
        "count": count_reviews,
        "step": step_cleaned
    })

@app.route('/api/sentiment-analysis', methods=['GET'])
def sentimentAnalysisReview():
    data =  pd.read_csv('./static/data/data_topik_rs_4.csv')
    sentiment = data[['rating', 'type_rs','stemmed_text_done', 'location', 'label', 'predicted_sentiment']]

    count_reviews = len(sentiment)
    sentiment['predicted_sentiment'] = sentiment['predicted_sentiment'].replace({1: 'Positif', -1: 'Negatif'})

    location_filter = request.args.get('location', 'all')
    rating_filter = request.args.get('rating', 'all')
    type_filter = request.args.get('type', 'all')

    sentiment['location'] = sentiment['location'].str.lower().str.replace(r'\s+', '_', regex=True)

    # Filter 
    filtered_reviews = sentiment.copy()
    # filter
    if location_filter != 'all':
        filtered_reviews = filtered_reviews[filtered_reviews['location'].str.contains(location_filter, case=False)]    

    if rating_filter != 'all':
        try:
            rating_filter_value = float(rating_filter)
            filtered_reviews = filtered_reviews[filtered_reviews['rating'] == rating_filter_value]
        except ValueError:
            return jsonify({"error": "Invalid ratingFilter value"}), 400       

    if type_filter != 'all':
        filtered_reviews = filtered_reviews[filtered_reviews['type_rs'].str.lower() == type_filter.lower()]    

    # Pagination hanya berdasarkan hasil filter
    page = int(request.args.get('page', 1))
    per_page = 10
    filtered_total = len(filtered_reviews)
    total_pages = (filtered_total // per_page) + (1 if filtered_total % per_page > 0 else 0)       

    paginated_reviews = filtered_reviews.iloc[(page - 1) * per_page : page * per_page]     

    start_page = max(page - 5, 1)
    end_page = min(page + 5, total_pages)
    page_range = list(range(start_page, end_page + 1))     

    return jsonify({
        "sentiment": paginated_reviews.to_dict(orient='records'),
        "pagination": {
            "page": page,
            "total_pages": total_pages,
            "page_range": page_range
        },
        "filters": {
            "location_filter": location_filter,
            "rating_filter": rating_filter,
             "type_filter": type_filter
        },
         "count": count_reviews,  
        # "count_sentiment_positif": count_sentiment_positif,
        # "count_sentiment_negatif": count_sentiment_negatif,
        # "count_prediction_positif": count_prediction_positif,
        # "count_prediction_negatif": count_prediction_negatif
    })

@app.route('/api/sentiment-analysis/word-cloud/<type>', methods=['GET'])
def wordCloud(type):
    data =  pd.read_csv('./static/data/data_topik_rs_4.csv')
    sentiment = data[['rating', 'type_rs','stemmed_text_done', 'location', 'label', 'predicted_sentiment']]

    if type == 'type-a':
        sentiment = sentiment[sentiment['type_rs'] == 'A']
    elif type == 'type-b':
        sentiment = sentiment[sentiment['type_rs'] == 'B']
    elif type == 'type-c':
        sentiment = sentiment[sentiment['type_rs'] == 'C']
    else:
        sentiment = sentiment[sentiment['type_rs'] == 'D']    

    sentiment['predicted_sentiment'] = sentiment['predicted_sentiment'].replace({1: 'Positif', -1: 'Negatif'})

    # Pisahkan ulasan berdasarkan label Positif dan Negatif
    positive_reviews = sentiment[sentiment['predicted_sentiment'] == 'Positif']
    negative_reviews = sentiment[sentiment['predicted_sentiment'] == 'Negatif']

    # Membuat model CountVectorizer untuk Positif
    vectorizer_pos = CountVectorizer(stop_words='english', max_features=50)
    X_pos = vectorizer_pos.fit_transform(positive_reviews['stemmed_text_done'])
    words_pos = vectorizer_pos.get_feature_names_out()
    frequencies_pos = X_pos.sum(axis=0).A1
    word_freq_pos = pd.DataFrame(list(zip(words_pos, frequencies_pos)), columns=['Word', 'Frequency'])
    word_freq_pos = word_freq_pos.sort_values(by='Frequency', ascending=False).head(50)

    # Membuat model CountVectorizer untuk Negatif
    vectorizer_neg = CountVectorizer(stop_words='english', max_features=50)
    X_neg = vectorizer_neg.fit_transform(negative_reviews['stemmed_text_done'])
    words_neg = vectorizer_neg.get_feature_names_out()
    frequencies_neg = X_neg.sum(axis=0).A1
    word_freq_neg = pd.DataFrame(list(zip(words_neg, frequencies_neg)), columns=['Word', 'Frequency'])
    word_freq_neg = word_freq_neg.sort_values(by='Frequency', ascending=False).head(50)

    return jsonify({
        "word_freq_pos": word_freq_pos.to_dict(orient='records'),
        "word_freq_neg": word_freq_neg.to_dict(orient='records'),
    })


@app.route("/api/topics", methods=["GET"])
def get_grouped_suggestions():
    type_filter = request.args.get("type")
    if not type_filter:
        return jsonify({"error": "Parameter 'type' wajib diisi"}), 400

    type_upper = type_filter.upper()
    positif_topics = Topic.query.filter_by(topic_type=type_upper, sentiment="positif").all()
    negatif_topics = Topic.query.filter_by(topic_type=type_upper, sentiment="negatif").all()

    def serialize_grouped_suggestions(topics):
        result = []
        for topic in topics:
            result.append({
                "topic": topic.title,
                "suggestions": [
                    {
                        "id": s.id,
                        "content": s.content,
                        "created_at": s.created_at.isoformat(),
                        "updated_at": s.updated_at.isoformat()
                    }
                    for s in topic.suggestions
                ]
            })
        return result

    return jsonify({
        "typeTopic": type_upper,
        "positive": serialize_grouped_suggestions(positif_topics),
        "negative": serialize_grouped_suggestions(negatif_topics)
    })

@app.route("/api/summary", methods=["GET"])
def get_summary_by_type():
    type_filter = request.args.get("type")
    if not type_filter:
        return jsonify({"error": "Parameter 'type' wajib diisi"}), 400

    type_upper = type_filter.upper()

    summary_pos = Summary.query.filter_by(type_name=type_upper, sentiment="positif").first()
    summary_neg = Summary.query.filter_by(type_name=type_upper, sentiment="negatif").first()

    result = {
        "summary": {
            "positive": {
                "id": summary_pos.id if summary_pos else None,
                "type_name": summary_pos.type_name if summary_pos else type_upper,
                "sentiment": "positif",
                "content": summary_pos.content if summary_pos else None
            },
            "negative": {
                "id": summary_neg.id if summary_neg else None,
                "type_name": summary_neg.type_name if summary_neg else type_upper,
                "sentiment": "negatif",
                "content": summary_neg.content if summary_neg else None
            }
        }
    }

    return jsonify(result)


@app.route("/api/suggestions/bulk-update", methods=["PUT"])
def bulk_update_suggestions():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Data harus berupa list"}), 400

    for item in data:
        suggestion_id = item.get("id")
        content = item.get("content")

        if not suggestion_id or not content:
            continue

        suggestion = Suggestion.query.get(suggestion_id)
        if suggestion:
            suggestion.content = content

    db.session.commit()
    return jsonify({"message": "Suggestions updated"}), 200

@app.route("/api/summaries/bulk-update", methods=["PUT"])
def bulk_update_summary():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Data harus berupa list"}), 400

    for item in data:
        summary_id = item.get("id")
        content = item.get("content")

        if not summary_id or content is None:
            continue

        summary = Summary.query.get(summary_id)
        if summary:
            summary.content = content

    db.session.commit()
    return jsonify({"message": "Summary updated successfully."}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
