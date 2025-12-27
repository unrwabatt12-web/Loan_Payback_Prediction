import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import hashlib
import secrets

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "loan_payback"
        self.connection = None
        self.connect()
    
    def connect(self):
        """Create database connection"""
        try:
            if self.connection and self.connection.is_connected():
                return True
                
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False,
                pool_name="mypool",
                pool_size=5
            )
            
            if self.connection.is_connected():
                print("🟢 Database connected!")
                return True
        except Error as e:
            print(f"🔴 Error connecting to database: {e}")
            self.connection = None
            return False
    
    def ensure_connection(self):
        """Ensure database connection is active"""
        try:
            if not self.connection or not self.connection.is_connected():
                print("Database connection lost, reconnecting...")
                return self.connect()
            return True
        except:
            return self.connect()
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed!")
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    #  USER MANAGEMENT 
    
    def create_user(self, username, email, password, full_name=None):
        """Create new user"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor()
            hashed_password = self.hash_password(password)
            
            query = """
                INSERT INTO users (username, email, hashed_password, full_name)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (username, email, hashed_password, full_name))
            self.connection.commit()
            
            user_id = cursor.lastrowid
            cursor.close()
            return user_id
        except Error as e:
            self.connection.rollback()
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"Error fetching user: {e}")
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE email = %s AND is_active = TRUE"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"Error fetching user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE id = %s AND is_active = TRUE"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            print(f"Error fetching user: {e}")
            return None
    
    def verify_password(self, username, password):
        """Verify user password"""
        user = self.get_user_by_username(username)
        if user:
            hashed_password = self.hash_password(password)
            return user['hashed_password'] == hashed_password
        return False
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        if not self.ensure_connection():
            return False
            
        try:
            cursor = self.connection.cursor()
            query = "UPDATE users SET last_login = NOW() WHERE id = %s"
            cursor.execute(query, (user_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Error updating last login: {e}")
            return False
    
    def update_user_profile(self, user_id, full_name=None, email=None):
        """Update user profile information"""
        if not self.ensure_connection():
            return False
            
        try:
            cursor = self.connection.cursor()
            updates = []
            params = []
            
            if full_name is not None:
                updates.append("full_name = %s")
                params.append(full_name)
            
            if email is not None:
                updates.append("email = %s")
                params.append(email)
            
            if not updates:
                return False
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            
            cursor.execute(query, tuple(params))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Error updating user profile: {e}")
            return False
    
    #  PASSWORD RESET 
    
    def create_reset_token(self, user_id):
        """Create password reset token"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor()
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)
            
            query = """
                INSERT INTO password_reset_tokens (user_id, token, expires_at, is_used)
                VALUES (%s, %s, %s, 0)
            """
            cursor.execute(query, (user_id, token, expires_at))
            self.connection.commit()
            cursor.close()
            
            return token
        except Error as e:
            self.connection.rollback()
            print(f"Error creating reset token: {e}")
            return None
    
    def verify_reset_token(self, token):
        """Verify password reset token"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM password_reset_tokens 
                WHERE token = %s AND is_used = 0 AND expires_at > NOW()
            """
            cursor.execute(query, (token,))
            token_data = cursor.fetchone()
            cursor.close()
            return token_data
        except Error as e:
            print(f"Error verifying token: {e}")
            return None
    
    def use_reset_token(self, token):
        """Mark reset token as used"""
        if not self.ensure_connection():
            return False
            
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE password_reset_tokens 
                SET is_used = 1, used_at = NOW() 
                WHERE token = %s
            """
            cursor.execute(query, (token,))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Error using token: {e}")
            return False
    
    def update_password(self, user_id, new_password):
        """Update user password"""
        if not self.ensure_connection():
            return False
            
        try:
            cursor = self.connection.cursor()
            hashed_password = self.hash_password(new_password)
            query = "UPDATE users SET hashed_password = %s WHERE id = %s"
            cursor.execute(query, (hashed_password, user_id))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Error updating password: {e}")
            return False
    
    # ==================== SINGLE PREDICTIONS ====================
    
    def save_prediction(self, user_id, prediction_data):
        """Save single prediction"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO single_predictions (
                    user_id, applicant_name, annual_income, debt_to_income_ratio,
                    credit_score, loan_amount, interest_rate, gender, marital_status,
                    education_level, employment_status, loan_purpose, grade_subgrade,
                    prediction, probability, risk_score, rejection_reasons
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                user_id,
                prediction_data.get('applicant_name'),
                prediction_data.get('annual_income'),
                prediction_data.get('debt_to_income_ratio'),
                prediction_data.get('credit_score'),
                prediction_data.get('loan_amount'),
                prediction_data.get('interest_rate'),
                prediction_data.get('gender'),
                prediction_data.get('marital_status'),
                prediction_data.get('education_level'),
                prediction_data.get('employment_status'),
                prediction_data.get('loan_purpose'),
                prediction_data.get('grade_subgrade'),
                prediction_data.get('prediction'),
                prediction_data.get('probability'),
                prediction_data.get('risk_score'),
                prediction_data.get('rejection_reasons')
            ))
            self.connection.commit()
            
            prediction_id = cursor.lastrowid
            cursor.close()
            return prediction_id
        except Error as e:
            self.connection.rollback()
            print(f"Error saving prediction: {e}")
            return None
    
    def get_user_predictions(self, user_id, limit=50):
        """Get user's prediction history"""
        if not self.ensure_connection():
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM single_predictions 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            cursor.execute(query, (user_id, limit))
            predictions = cursor.fetchall()
            cursor.close()
            return predictions
        except Error as e:
            print(f"Error fetching predictions: {e}")
            return []
    
    def get_prediction_by_id(self, prediction_id):
        """Get single prediction by ID"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM single_predictions WHERE id = %s"
            cursor.execute(query, (prediction_id,))
            prediction = cursor.fetchone()
            cursor.close()
            return prediction
        except Error as e:
            print(f"Error fetching prediction: {e}")
            return None
    
    # ==================== BATCH PREDICTIONS ====================
    
    def save_batch_prediction(self, user_id, batch_data):
        """Save batch prediction summary"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor()
            
            query = """
                INSERT INTO batch_predictions (
                    user_id, batch_name, file_name, file_size_kb, total_applications, 
                    approved_applications, rejected_applications, approval_rate, 
                    processing_time_seconds
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                user_id,
                batch_data.get('batch_name'),
                batch_data.get('filename'),
                batch_data.get('file_size_kb'),
                batch_data.get('total_applications'),
                batch_data.get('approved_applications'),
                batch_data.get('rejected_applications'),
                batch_data.get('approval_rate'),
                batch_data.get('processing_time_seconds')
            ))
            self.connection.commit()
            batch_id = cursor.lastrowid
            cursor.close()
            return batch_id
        except Error as e:
            self.connection.rollback()
            print(f"Error saving batch prediction: {e}")
            return None
    
    def save_batch_prediction_details(self, batch_id, details):
        """Save batch prediction details"""
        if not self.ensure_connection():
            return False
            
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO batch_prediction_details (
                    batch_id, applicant_name, annual_income, loan_amount, interest_rate,
                    debt_to_income_ratio, credit_score, gender, marital_status,
                    education_level, employment_status, loan_purpose, grade_subgrade,
                    prediction, probability, risk_score, rejection_reasons, row_number
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for detail in details:
                cursor.execute(query, (
                    batch_id,
                    detail.get('applicant_name'),
                    detail.get('annual_income'),
                    detail.get('loan_amount'),
                    detail.get('interest_rate'),
                    detail.get('debt_to_income_ratio'),
                    detail.get('credit_score'),
                    detail.get('gender'),
                    detail.get('marital_status'),
                    detail.get('education_level'),
                    detail.get('employment_status'),
                    detail.get('loan_purpose'),
                    detail.get('grade_subgrade'),
                    detail.get('prediction'),
                    detail.get('probability'),
                    detail.get('risk_score'),
                    detail.get('rejection_reasons'),
                    detail.get('row_number')
                ))
            
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Error saving batch details: {e}")
            return False
    
    def get_user_batch_predictions(self, user_id, limit=20):
        """Get user's batch prediction history"""
        if not self.ensure_connection():
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM batch_predictions 
                WHERE user_id = %s 
                ORDER BY processed_at DESC 
                LIMIT %s
            """
            cursor.execute(query, (user_id, limit))
            batches = cursor.fetchall()
            cursor.close()
            return batches
        except Error as e:
            print(f"Error fetching batch predictions: {e}")
            return []
    
    def get_batch_prediction_details(self, batch_id):
        """Get details of a specific batch prediction"""
        if not self.ensure_connection():
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM batch_prediction_details 
                WHERE batch_id = %s 
                ORDER BY row_number ASC
            """
            cursor.execute(query, (batch_id,))
            details = cursor.fetchall()
            cursor.close()
            return details
        except Error as e:
            print(f"Error fetching batch details: {e}")
            return []
    
    def get_batch_prediction_by_id(self, batch_id):
        """Get batch prediction by ID"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM batch_predictions WHERE id = %s"
            cursor.execute(query, (batch_id,))
            batch = cursor.fetchone()
            cursor.close()
            return batch
        except Error as e:
            print(f"Error fetching batch: {e}")
            return None
    
    #  STATISTICS & ANALYTICS 
    
    def get_user_statistics(self, user_id):
        """Get comprehensive user statistics"""
        if not self.ensure_connection():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM user_statistics WHERE id = %s
            """
            cursor.execute(query, (user_id,))
            stats = cursor.fetchone()
            cursor.close()
            return stats
        except Error as e:
            print(f"Error fetching user statistics: {e}")
            return None
    
    def get_approval_by_credit_score(self):
        """Get approval rates grouped by credit score ranges"""
        if not self.ensure_connection():
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM approval_by_credit_score"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error fetching credit score analysis: {e}")
            return []
    
    def get_recent_predictions_summary(self, limit=50):
        """Get recent predictions summary from view"""
        if not self.ensure_connection():
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM recent_predictions_summary 
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error fetching recent predictions: {e}")
            return []
    
    def get_all_users_statistics(self):
        """Get statistics for all users"""
        if not self.ensure_connection():
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM user_statistics ORDER BY created_at DESC"
            cursor.execute(query)
            stats = cursor.fetchall()
            cursor.close()
            return stats
        except Error as e:
            print(f"Error fetching all user statistics: {e}")
            return []
    
    # ==================== ADMIN FUNCTIONS ====================
    
    def get_all_users(self, include_inactive=False):
        """Get all users (admin function)"""
        if not self.ensure_connection():
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            if include_inactive:
                query = "SELECT * FROM users ORDER BY created_at DESC"
            else:
                query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY created_at DESC"
            
            cursor.execute(query)
            users = cursor.fetchall()
            cursor.close()
            return users
        except Error as e:
            print(f"Error fetching all users: {e}")
            return []
    
    def deactivate_user(self, user_id):
        """Deactivate a user account"""
        if not self.ensure_connection():
            return False
            
        try:
            cursor = self.connection.cursor()
            query = "UPDATE users SET is_active = FALSE WHERE id = %s"
            cursor.execute(query, (user_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Error deactivating user: {e}")
            return False
    
    def activate_user(self, user_id):
        """Activate a user account"""
        if not self.ensure_connection():
            return False
            
        try:
            cursor = self.connection.cursor()
            query = "UPDATE users SET is_active = TRUE WHERE id = %s"
            cursor.execute(query, (user_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Error activating user: {e}")
            return False


if __name__ == "__main__":
    print("Testing database connection...")
    db = Database()
    
    if db.connection:
        print(" Database connected!")
        
        # Test getting statistics
        print("\n Testing statistics queries...")
        credit_stats = db.get_approval_by_credit_score()
        print(f"Credit score analysis: {len(credit_stats)} ranges")
        
        recent = db.get_recent_predictions_summary(limit=5)
        print(f"Recent predictions: {len(recent)} records")
        
    else:
        print(" Database connection failed!")