from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
import logging
import signal

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:tnadmin@localhost/cbvis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup logging
logging.basicConfig(level=logging.DEBUG)

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class SrsAdp(db.Model):
    __tablename__ = 'srs_adp'
    series_id = db.Column(db.String, primary_key=True)
    series_name = db.Column(db.String)
    units = db.Column(db.String)
    units_short = db.Column(db.String)
    frequency = db.Column(db.String)
    frequency_short = db.Column(db.String)
    seasonal_adjustment = db.Column(db.String)
    release_name = db.Column(db.String)
    release_id = db.Column(db.String)
    source_name = db.Column(db.String)
    source_id = db.Column(db.String)
    observation_start = db.Column(db.String)
    observation_end = db.Column(db.String)
    last_updated = db.Column(db.String)

class ObsAdp(db.Model):
    __tablename__ = 'obs_adp'
    date = db.Column(db.String, primary_key=True)
    value = db.Column(db.Float)
    series_id = db.Column(db.String, db.ForeignKey('srs_adp.series_id'), primary_key=True)

def timeout_handler(signum, frame):
    raise TimeoutError("Request timed out")

# Set signal for Unix-based systems
if hasattr(signal, 'SIGALRM'):
    signal.signal(signal.SIGALRM, timeout_handler)



@app.route('/api/series_names', methods=['GET'])
def get_series_names():
    try:
        offset = request.args.get('offset', default=0, type=int)
        limit = request.args.get('limit', default=20, type=int)
        series = db.session.query(SrsAdp.series_id, SrsAdp.series_name).offset(offset).limit(limit).all()
        return jsonify({"series_names": [{"series_id": s.series_id, "series_name": s.series_name} for s in series]})
    except SQLAlchemyError as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500




@app.route('/api/series_values', methods=['GET'])
def get_series_values():
    try:
        series_id = request.args.get('series_id')
        if not series_id:
            return jsonify({"error": "series_id parameter is required"}), 400
        series_values = db.session.query(ObsAdp).filter(ObsAdp.series_id == series_id).all()
        return jsonify([{"date": value.date, "value": value.value} for value in series_values])
    except SQLAlchemyError as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500



# Fetch filter options
@app.route('/api/filter_options', methods=['GET'])
def get_filter_options():
    try:
        filters = {
            "seasonal_adjustment": [],
            "source_name": [],
            "release_name": []
        }
        filters["seasonal_adjustment"] = [row[0] for row in db.session.query(SrsAdp.seasonal_adjustment).distinct().all()]
        filters["source_name"] = [row[0] for row in db.session.query(SrsAdp.source_name).distinct().all()]
        filters["release_name"] = [row[0] for row in db.session.query(SrsAdp.release_name).distinct().all()]
        return jsonify(filters)
    except SQLAlchemyError as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Fetch filtered series data
@app.route('/api/filtered_series', methods=['POST'])
def get_filtered_series():
    try:
        if hasattr(signal, 'alarm'):
            signal.alarm(120)  # Set a 120-second alarm for Unix-based systems
        data = request.json
        selected_filters = data.get('filters', {})
        app.logger.debug(f"Selected filters: {selected_filters}")

        query = db.session.query(SrsAdp)

        if selected_filters.get('seasonal_adjustment'):
            query = query.filter(SrsAdp.seasonal_adjustment.in_(selected_filters['seasonal_adjustment']))
        if selected_filters.get('source_name'):
            query = query.filter(SrsAdp.source_name.in_(selected_filters['source_name']))
        if selected_filters.get('release_name'):
            query = query.filter(SrsAdp.release_name.in_(selected_filters['release_name']))

        series = query.all()
        series_ids = [s.series_id for s in series]
        app.logger.debug(f"Filtered series IDs: {len(series_ids)}")

        if not series_ids:
            app.logger.debug("No series IDs found matching the filters.")
            return jsonify([])

        # Fetch data from obs_adp with series_ids as columns
        data_query = db.session.query(ObsAdp).filter(ObsAdp.series_id.in_(series_ids)).all()
        app.logger.debug(f"Data query result: {len(data_query)}")

        result = []
        for row in data_query:
            result.append({"date": row.date, "value": row.value, "series_id": row.series_id})
        app.logger.debug(f"Filtered data: {len(result)}")
        return jsonify(result)
    except TimeoutError:
        app.logger.error("Request timed out")
        return jsonify({"error": "Request timed out"}), 504
    except SQLAlchemyError as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if hasattr(signal, 'alarm'):
            signal.alarm(0)  # Disable the alarm

# API to handle user registration
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
