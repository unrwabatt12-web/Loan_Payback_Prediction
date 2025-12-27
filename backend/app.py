from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import pandas as pd
import time
from functools import wraps
from database import Database
from model import LoanPredictionModel

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production-2024'
app.config['JWT_EXPIRATION_HOURS'] = 24

# Initialize ML model
predictor = LoanPredictionModel()

# Initialize database
db = Database()

# JWT token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'detail': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'detail': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db.get_user_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({'detail': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'detail': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'detail': 'Invalid token'}), 401
        except Exception as e:
            print(f" Token verification error: {e}")
            return jsonify({'detail': 'Token verification failed'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


# Admin token decorator
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'detail': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'detail': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db.get_user_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({'detail': 'User not found'}), 401
            
            if not current_user.get('is_admin'):
                return jsonify({'detail': 'Admin access required'}), 403
                
        except jwt.ExpiredSignatureError:
            return jsonify({'detail': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'detail': 'Invalid token'}), 401
        except Exception as e:
            print(f" Token verification error: {e}")
            return jsonify({'detail': 'Token verification failed'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


# ============= HEALTH CHECK =============
@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Loan Payback Prediction API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'register': '/register',
            'login': '/token',
            'user_info': '/me',
            'forgot_password': '/forgot-password',
            'reset_password': '/reset-password',
            'update_profile': '/me/update',
            'predict_single': '/predict',
            'predict_batch': '/predict/batch',
            'prediction_history': '/history/predictions',
            'batch_history': '/history/batch',
            'batch_details': '/history/batch/<id>',
            'statistics': '/statistics',
            'user_stats': '/statistics/user',
            'credit_score_analysis': '/statistics/credit-score',
            'admin_users': '/admin/users',
            'admin_statistics': '/admin/statistics'
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    db_connected = False
    try:
        db_connected = db.ensure_connection()
    except:
        db_connected = False
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': predictor.model is not None,
        'database_connected': db_connected,
        'features': len(predictor.feature_names) if predictor.feature_names else 0
    })


# ============= AUTHENTICATION ENDPOINTS =============
@app.route('/register', methods=['POST'])
def register():
    """User registration"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'detail': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'detail': 'Username must be at least 3 characters'}), 400
        
        if not email or '@' not in email:
            return jsonify({'detail': 'Valid email is required'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'detail': 'Password must be at least 6 characters'}), 400
        
        # Check if user exists
        existing_user = db.get_user_by_username(username)
        if existing_user:
            return jsonify({'detail': 'Username already exists'}), 400
        
        existing_email = db.get_user_by_email(email)
        if existing_email:
            return jsonify({'detail': 'Email already registered'}), 400
        
        # Create user
        user_id = db.create_user(username, email, password, full_name)
        
        if not user_id:
            return jsonify({'detail': 'Failed to create user'}), 500
        
        # Generate token
        token = jwt.encode({
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        print(f" User registered: {username} (ID: {user_id})")
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': token,
            'token_type': 'bearer',
            'user': {
                'id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name
            }
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'detail': f'Registration failed: {str(e)}'}), 500


@app.route('/token', methods=['POST'])
def login():
    """User login"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return jsonify({'detail': 'Username and password required'}), 400
        
        print(f" Login attempt for user: {username}")
        
        # Verify credentials
        if not db.verify_password(username, password):
            print(f"Invalid credentials for: {username}")
            return jsonify({'detail': 'Invalid username or password'}), 401
        
        # Get user
        user = db.get_user_by_username(username)
        
        if not user:
            return jsonify({'detail': 'User not found'}), 401
        
        # Update last login
        db.update_last_login(user['id'])
        
        # Generate token
        token = jwt.encode({
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.utcnow() + timedelta(hours=app.config['JWT_EXPIRATION_HOURS'])
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        print(f"Login successful: {username}")
        
        return jsonify({
            'access_token': token,
            'token_type': 'bearer',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'is_admin': user.get('is_admin', False)
            }
        }), 200
        
    except Exception as e:
        print(f" Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'detail': f'Login failed: {str(e)}'}), 500


@app.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user info"""
    try:
        return jsonify({
            'id': current_user['id'],
            'username': current_user['username'],
            'email': current_user['email'],
            'full_name': current_user['full_name'],
            'is_admin': current_user.get('is_admin', False),
            'created_at': current_user['created_at'].isoformat() if current_user.get('created_at') else None,
            'last_login': current_user['last_login'].isoformat() if current_user.get('last_login') else None
        }), 200
    except Exception as e:
        print(f"Get user error: {e}")
        return jsonify({'detail': str(e)}), 500


@app.route('/me/update', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'detail': 'No data provided'}), 400
        
        full_name = data.get('full_name')
        email = data.get('email')
        
        # If email is being changed, check if it's already taken
        if email and email != current_user['email']:
            existing = db.get_user_by_email(email)
            if existing and existing['id'] != current_user['id']:
                return jsonify({'detail': 'Email already in use'}), 400
        
        # Update profile
        if db.update_user_profile(current_user['id'], full_name, email):
            updated_user = db.get_user_by_id(current_user['id'])
            print(f" Profile updated for: {current_user['username']}")
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': updated_user['id'],
                    'username': updated_user['username'],
                    'email': updated_user['email'],
                    'full_name': updated_user['full_name']
                }
            }), 200
        
        return jsonify({'detail': 'Failed to update profile'}), 500
        
    except Exception as e:
        print(f" Profile update error: {e}")
        return jsonify({'detail': str(e)}), 500


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'detail': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'detail': 'Email is required'}), 400
        
        user = db.get_user_by_email(email)
        
        # Always return success to prevent email enumeration
        if user:
            token = db.create_reset_token(user['id'])
            
            print(f" Password reset token generated for: {email}")
            print(f"Token: {token}")
            
            return jsonify({
                'message': 'Password reset instructions sent',
                'reset_token': token  # Remove this in production!
            }), 200
        
        return jsonify({
            'message': 'If email exists, reset instructions have been sent'
        }), 200
        
    except Exception as e:
        print(f" Forgot password error: {e}")
        return jsonify({'detail': str(e)}), 500


@app.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'detail': 'No data provided'}), 400
        
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        
        if not token or not new_password:
            return jsonify({'detail': 'Token and new password required'}), 400
        
        if len(new_password) < 8:
            return jsonify({'detail': 'Password must be at least 8 characters'}), 400
        
        # Verify token
        token_data = db.verify_reset_token(token)
        
        if not token_data:
            return jsonify({'detail': 'Invalid or expired token'}), 400
        
        # Update password
        if db.update_password(token_data['user_id'], new_password):
            db.use_reset_token(token)
            print(f"Password reset successful for user ID: {token_data['user_id']}")
            return jsonify({'message': 'Password reset successful'}), 200
        
        return jsonify({'detail': 'Failed to reset password'}), 500
        
    except Exception as e:
        print(f" Reset password error: {e}")
        return jsonify({'detail': str(e)}), 500


# ============= PREDICTION ENDPOINTS =============
@app.route('/predict', methods=['POST'])
@token_required
def predict_single(current_user):
    """Single loan prediction"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        if predictor.model is None:
            return jsonify({'detail': 'Model not loaded'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'detail': 'No data provided'}), 400
        
        # Extract and validate features
        try:
            features = {
                'annual_income': float(data.get('annual_income', 0)),
                'debt_to_income_ratio': float(data.get('debt_to_income_ratio', 0)),
                'credit_score': int(data.get('credit_score', 0)),
                'loan_amount': float(data.get('loan_amount', 0)),
                'interest_rate': float(data.get('interest_rate', 0)),
                'gender': str(data.get('gender', 'Male')),
                'marital_status': str(data.get('marital_status', 'Single')),
                'education_level': str(data.get('education_level', 'High School')),
                'employment_status': str(data.get('employment_status', 'Employed')),
                'loan_purpose': str(data.get('loan_purpose', 'Other')),
                'grade_subgrade': str(data.get('grade_subgrade', 'C1'))
            }
        except (ValueError, TypeError) as e:
            return jsonify({'detail': f'Invalid data format: {str(e)}'}), 400
        
        # Make prediction
        result = predictor.predict_single(features)
        
        # Save to database
        prediction_data = {
            'applicant_name': data.get('applicant_name', 'Unknown'),
            **features,
            'prediction': result['prediction'],
            'probability': result['probability'],
            'risk_score': result.get('risk_score'),
            'rejection_reasons': result.get('rejection_reasons')
        }
        
        prediction_id = db.save_prediction(current_user['id'], prediction_data)
        
        print(f" Prediction made for {current_user['username']}: {result['status']}")
        
        return jsonify({
            'prediction': result['prediction'],
            'probability': result['probability'],
            'status': result['status'],
            'risk_score': result.get('risk_score'),
            'rejection_reasons': result.get('rejection_reasons'),
            'prediction_id': prediction_id
        }), 200
        
    except Exception as e:
        print(f" Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'detail': f'Prediction failed: {str(e)}'}), 500


@app.route('/predict/batch', methods=['POST'])
@token_required
def predict_batch(current_user):
    """Batch loan predictions from CSV"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        if predictor.model is None:
            return jsonify({'detail': 'Model not loaded'}), 500
        
        if 'file' not in request.files:
            return jsonify({'detail': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'detail': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'detail': 'Only CSV files are supported'}), 400
        
        start_time = time.time()
        
        # Get file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        file_size_kb = round(file_size / 1024, 2)
        
        # Read CSV
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return jsonify({'detail': f'Failed to read CSV: {str(e)}'}), 400
        
        if df.empty:
            return jsonify({'detail': 'CSV file is empty'}), 400
        
        print(f" Processing batch of {len(df)} applications for {current_user['username']}")
        
        results = []
        batch_details = []
        approved_count = 0
        rejected_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                features = {
                    'annual_income': float(row.get('annual_income', 0)),
                    'debt_to_income_ratio': float(row.get('debt_to_income_ratio', 0)),
                    'credit_score': int(row.get('credit_score', 0)),
                    'loan_amount': float(row.get('loan_amount', 0)),
                    'interest_rate': float(row.get('interest_rate', 0)),
                    'gender': str(row.get('gender', 'Male')),
                    'marital_status': str(row.get('marital_status', 'Single')),
                    'education_level': str(row.get('education_level', 'High School')),
                    'employment_status': str(row.get('employment_status', 'Employed')),
                    'loan_purpose': str(row.get('loan_purpose', 'Other')),
                    'grade_subgrade': str(row.get('grade_subgrade', 'C1'))
                }
                
                result = predictor.predict_single(features)
                applicant_name = str(row.get('applicant_name', f'Applicant {idx + 1}'))
                
                if result['prediction'] == 1:
                    approved_count += 1
                else:
                    rejected_count += 1
                
                # For API response
                results.append({
                    'row_number': idx + 1,
                    'applicant_name': applicant_name,
                    'prediction': result['prediction'],
                    'probability': result['probability'],
                    'credit_score': features['credit_score'],
                    'debt_to_income_ratio': features['debt_to_income_ratio'],
                    'status': result['status'],
                    'risk_score': result.get('risk_score'),
                    'rejection_reasons': result.get('rejection_reasons')
                })
                
                # For database storage
                batch_details.append({
                    'row_number': idx + 1,
                    'applicant_name': applicant_name,
                    **features,
                    'prediction': result['prediction'],
                    'probability': result['probability'],
                    'risk_score': result.get('risk_score'),
                    'rejection_reasons': result.get('rejection_reasons')
                })
                
            except Exception as e:
                error_count += 1
                results.append({
                    'row_number': idx + 1,
                    'applicant_name': str(row.get('applicant_name', f'Applicant {idx + 1}')),
                    'error': str(e)
                })
        
        processing_time = round(time.time() - start_time, 3)
        total_applications = len(df)
        successful_predictions = approved_count + rejected_count
        approval_rate = round((approved_count / successful_predictions * 100), 2) if successful_predictions > 0 else 0
        
        # Get batch name from request or use filename
        batch_name = request.form.get('batch_name', file.filename)
        
        # Save batch summary
        batch_data = {
            'batch_name': batch_name,
            'filename': file.filename,
            'file_size_kb': file_size_kb,
            'total_applications': total_applications,
            'approved_applications': approved_count,
            'rejected_applications': rejected_count,
            'approval_rate': approval_rate,
            'processing_time_seconds': processing_time
        }
        batch_id = db.save_batch_prediction(current_user['id'], batch_data)
        
        # Save batch details
        if batch_id and batch_details:
            db.save_batch_prediction_details(batch_id, batch_details)
        
        print(f" Batch processed: {approved_count} approved, {rejected_count} rejected, {error_count} errors")
        
        return jsonify({
            'batch_id': batch_id,
            'results': results,
            'total_applications': total_applications,
            'approved_applications': approved_count,
            'rejected_applications': rejected_count,
            'error_count': error_count,
            'approval_rate': f"{approval_rate}%",
            'processing_time_seconds': processing_time,
            'file_size_kb': file_size_kb
        }), 200
        
    except Exception as e:
        print(f" Batch prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'detail': f'Batch processing failed: {str(e)}'}), 500


# ============= HISTORY ENDPOINTS =============
@app.route('/history/predictions', methods=['GET'])
@token_required
def get_prediction_history(current_user):
    """Get user's prediction history"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        limit = request.args.get('limit', 50, type=int)
        
        if limit < 1 or limit > 100:
            limit = 50
        
        predictions = db.get_user_predictions(current_user['id'], limit)
        
        # Convert datetime objects to strings and Decimal to float
        for pred in predictions:
            if 'created_at' in pred and pred['created_at']:
                pred['created_at'] = pred['created_at'].isoformat()
            
            # Convert Decimal to float
            for key in ['annual_income', 'debt_to_income_ratio', 'loan_amount', 
                       'interest_rate', 'probability', 'risk_score']:
                if key in pred and pred[key] is not None:
                    pred[key] = float(pred[key])
        
        return jsonify({
            'predictions': predictions,
            'total': len(predictions),
            'limit': limit
        }), 200
        
    except Exception as e:
        print(f" History error: {e}")
        return jsonify({'detail': f'Failed to fetch history: {str(e)}'}), 500


@app.route('/history/batch', methods=['GET'])
@token_required
def get_batch_history(current_user):
    """Get user's batch prediction history"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        limit = request.args.get('limit', 20, type=int)
        
        if limit < 1 or limit > 50:
            limit = 20
        
        batches = db.get_user_batch_predictions(current_user['id'], limit)
        
        # Convert datetime objects to strings and Decimal to float
        for batch in batches:
            if 'processed_at' in batch and batch['processed_at']:
                batch['processed_at'] = batch['processed_at'].isoformat()
            
            # Convert Decimal to float
            for key in ['approval_rate', 'processing_time_seconds', 'file_size_kb']:
                if key in batch and batch[key] is not None:
                    batch[key] = float(batch[key])
        
        return jsonify({
            'batches': batches,
            'total': len(batches),
            'limit': limit
        }), 200
        
    except Exception as e:
        print(f" Batch history error: {e}")
        return jsonify({'detail': f'Failed to fetch batch history: {str(e)}'}), 500


@app.route('/history/batch/<int:batch_id>', methods=['GET'])
@token_required
def get_batch_details(current_user, batch_id):
    """Get details of a specific batch prediction"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        # Get batch summary
        batch = db.get_batch_prediction_by_id(batch_id)
        
        if not batch:
            return jsonify({'detail': 'Batch not found'}), 404
        
        # Check ownership
        if batch['user_id'] != current_user['id']:
            return jsonify({'detail': 'Access denied'}), 403
        
        # Get batch details
        details = db.get_batch_prediction_details(batch_id)
        
        # Convert datetime and Decimal types
        if batch.get('processed_at'):
            batch['processed_at'] = batch['processed_at'].isoformat()
        
        for key in ['approval_rate', 'processing_time_seconds', 'file_size_kb']:
            if key in batch and batch[key] is not None:
                batch[key] = float(batch[key])
        
        for detail in details:
            for key in ['annual_income', 'loan_amount', 'interest_rate', 
                       'debt_to_income_ratio', 'probability', 'risk_score']:
                if key in detail and detail[key] is not None:
                    detail[key] = float(detail[key])
        
        return jsonify({
            'batch': batch,
            'details': details,
            'total_details': len(details)
        }), 200
        
    except Exception as e:
        print(f" Batch details error: {e}")
        return jsonify({'detail': f'Failed to fetch batch details: {str(e)}'}), 500


# ============= STATISTICS ENDPOINTS =============
@app.route('/statistics', methods=['GET'])
@token_required
def get_statistics(current_user):
    """Get user's prediction statistics"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        predictions = db.get_user_predictions(current_user['id'], 1000)
        batches = db.get_user_batch_predictions(current_user['id'], 100)
        
        total_predictions = len(predictions)
        approved = sum(1 for p in predictions if p['prediction'] == 1)
        rejected = total_predictions - approved
        
        total_batches = len(batches)
        total_batch_applications = sum(b['total_applications'] for b in batches)
        total_batch_approved = sum(b['approved_applications'] for b in batches)
        total_batch_rejected = sum(b['rejected_applications'] for b in batches)
        
        return jsonify({
            'single_predictions': {
                'total': total_predictions,
                'approved': approved,
                'rejected': rejected,
                'approval_rate': round((approved / total_predictions * 100), 2) if total_predictions > 0 else 0
            },
            'batch_predictions': {
                'total_batches': total_batches,
                'total_applications': total_batch_applications,
                'total_approved': total_batch_approved,
                'total_rejected': total_batch_rejected,
                'approval_rate': round((total_batch_approved / total_batch_applications * 100), 2) if total_batch_applications > 0 else 0
            },
            'overall': {
                'total_predictions': total_predictions + total_batch_applications,
                'total_approved': approved + total_batch_approved,
                'total_rejected': rejected + total_batch_rejected
            }
        }), 200
        
    except Exception as e:
        print(f" Statistics error: {e}")
        return jsonify({'detail': str(e)}), 500


@app.route('/statistics/user', methods=['GET'])
@token_required
def get_user_stats(current_user):
    """Get comprehensive user statistics from view"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        stats = db.get_user_statistics(current_user['id'])
        
        if not stats:
            return jsonify({'detail': 'Statistics not available'}), 404
        
        # Convert datetime and Decimal types
        if stats.get('created_at'):
            stats['created_at'] = stats['created_at'].isoformat()
        if stats.get('last_login'):
            stats['last_login'] = stats['last_login'].isoformat()
        
        for key in ['total_applications_processed', 'total_approved', 'total_rejected']:
            if key in stats and stats[key] is not None:
                stats[key] = int(stats[key])
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f" User stats error: {e}")
        return jsonify({'detail': str(e)}), 500


@app.route('/statistics/credit-score', methods=['GET'])
@token_required
def get_credit_score_analysis(current_user):
    """Get approval rates by credit score ranges"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        analysis = db.get_approval_by_credit_score()
        
        # Convert Decimal types to float
        for item in analysis:
            for key in ['total_applications', 'approved', 'rejected', 'approval_rate']:
                if key in item and item[key] is not None:
                    item[key] = float(item[key])
        
        return jsonify({
            'credit_score_analysis': analysis,
            'total_ranges': len(analysis)
        }), 200
        
    except Exception as e:
        print(f" Credit score analysis error: {e}")
        return jsonify({'detail': str(e)}), 500


@app.route('/statistics/recent', methods=['GET'])
@token_required
def get_recent_predictions(current_user):
    """Get recent predictions summary"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        limit = request.args.get('limit', 50, type=int)
        if limit < 1 or limit > 100:
            limit = 50
        
        recent = db.get_recent_predictions_summary(limit)
        
        # Convert datetime and Decimal types
        for item in recent:
            if item.get('prediction_date'):
                item['prediction_date'] = item['prediction_date'].isoformat()
            
            for key in ['loan_amount', 'probability']:
                if key in item and item[key] is not None:
                    item[key] = float(item[key])
        
        return jsonify({
            'recent_predictions': recent,
            'total': len(recent),
            'limit': limit
        }), 200
        
    except Exception as e:
        print(f" Recent predictions error: {e}")
        return jsonify({'detail': str(e)}), 500


# ============= ADMIN ENDPOINTS =============
@app.route('/admin/users', methods=['GET'])
@admin_required
def admin_get_users(current_user):
    """Get all users (admin only)"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        users = db.get_all_users(include_inactive)
        
        # Convert datetime types and remove sensitive data
        for user in users:
            user.pop('hashed_password', None)
            user.pop('reset_token', None)
            
            if user.get('created_at'):
                user['created_at'] = user['created_at'].isoformat()
            if user.get('updated_at'):
                user['updated_at'] = user['updated_at'].isoformat()
            if user.get('last_login'):
                user['last_login'] = user['last_login'].isoformat()
            if user.get('reset_token_expiry'):
                user['reset_token_expiry'] = user['reset_token_expiry'].isoformat()
        
        return jsonify({
            'users': users,
            'total': len(users)
        }), 200
        
    except Exception as e:
        print(f" Admin users error: {e}")
        return jsonify({'detail': str(e)}), 500


@app.route('/admin/users/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def admin_deactivate_user(current_user, user_id):
    """Deactivate a user (admin only)"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        # Prevent self-deactivation
        if user_id == current_user['id']:
            return jsonify({'detail': 'Cannot deactivate your own account'}), 400
        
        if db.deactivate_user(user_id):
            print(f" User {user_id} deactivated by admin {current_user['username']}")
            return jsonify({'message': 'User deactivated successfully'}), 200
        
        return jsonify({'detail': 'Failed to deactivate user'}), 500
        
    except Exception as e:
        print(f"Deactivate user error: {e}")
        return jsonify({'detail': str(e)}), 500


@app.route('/admin/users/<int:user_id>/activate', methods=['POST'])
@admin_required
def admin_activate_user(current_user, user_id):
    """Activate a user (admin only)"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        if db.activate_user(user_id):
            print(f" User {user_id} activated by admin {current_user['username']}")
            return jsonify({'message': 'User activated successfully'}), 200
        
        return jsonify({'detail': 'Failed to activate user'}), 500
        
    except Exception as e:
        print(f" Activate user error: {e}")
        return jsonify({'detail': str(e)}), 500


@app.route('/admin/statistics', methods=['GET'])
@admin_required
def admin_get_statistics(current_user):
    """Get statistics for all users (admin only)"""
    try:
        if not db.ensure_connection():
            return jsonify({'detail': 'Database connection failed'}), 500
        
        all_stats = db.get_all_users_statistics()
        
        # Convert datetime and Decimal types
        for stats in all_stats:
            if stats.get('created_at'):
                stats['created_at'] = stats['created_at'].isoformat()
            if stats.get('last_login'):
                stats['last_login'] = stats['last_login'].isoformat()
            
            for key in ['total_applications_processed', 'total_approved', 'total_rejected']:
                if key in stats and stats[key] is not None:
                    stats[key] = int(stats[key])
        
        return jsonify({
            'user_statistics': all_stats,
            'total_users': len(all_stats)
        }), 200
        
    except Exception as e:
        print(f" Admin statistics error: {e}")
        return jsonify({'detail': str(e)}), 500


# ============= ERROR HANDLERS =============
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'detail': 'Endpoint not found',
        'error': '404 Not Found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'detail': 'Internal server error',
        'error': '500 Internal Server Error'
    }), 500


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'detail': 'Method not allowed',
        'error': '405 Method Not Allowed'
    }), 405


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'detail': 'Bad request',
        'error': '400 Bad Request'
    }), 400


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'detail': 'Access forbidden',
        'error': '403 Forbidden'
    }), 403


# saved predictions

import csv
from datetime import datetime
import os

LOG_FILE = "logs/predictions.csv"
os.makedirs("logs", exist_ok=True)

def log_prediction(inputs, prediction):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "inputs", "prediction"])
        writer.writerow([datetime.now(), inputs, prediction])


if __name__ == '__main__':   
    print(" Starting Loan Payback Prediction API...")
    print(f" Server: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)