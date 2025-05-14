from api.blueprints import auth
from flask import jsonify, request, url_for
from api.login_api.utils.validate_utils import validate_email, validate_password
from api.login_api.utils.user_utils import user_exists, verify_user_password, user_exists_in_pending_signups, insert_user_to_pending, update_user_email_status, user_mail_verified, reset_user_password
import datetime
from api.config import JWT_ALGORITHM, JWT_EXPIRY_MINUTES, JWT_SECRET_KEY
import jwt
from api.decoraters import token_required
from cachetools import TTLCache
from api.login_api.utils.otp_utlis import*

@auth.route('/login', methods=["GET", "POST"])
def login():
    """
    Handle login requests via GET and POST methods.
    GET returns a message indicating this is the login page.
    POST attempts to log in a user by validating email and password formats.
    """
    if request.method == "GET":
        # Handle GET request: Return a simple message indicating this is the login page
        return jsonify({"message": "This is Login Page"})
    
    try:
        # Check if the request content type is JSON; if not, reject it
        if not request.is_json:
            return jsonify({"message": "JSON Payload required"}), 400
        
        # Retrieve JSON data from the request body
        data = request.get_json()
        
        # Ensure data was successfully parsed; if not, return an error
        if data is None:
            return jsonify({"message": "Payload required"}), 400
            
        # Extract email and password from the JSON data using get() for safety
        email = data.get("email")
        password = data.get("password")

        # Check if both email and password are provided (not None or empty)
        if not all([email, password]):
            return jsonify({"message": "All fields required"}), 400
        
        if any(c in '<>;' for c in email + password):
            return jsonify({"message": "Invalid characters in input"}), 400
        
        # Validate the email format using the validate_email function
        if not validate_email(email):
            return jsonify({"message": "Invalid email format"}), 400
            
        # Validate the password format using the validate_password function
        if not validate_password(password):
            return jsonify({"message": "Invalid password format"}), 400
        
        if not user_exists(email):
            return jsonify({"message": "Incorrect email or password"}), 400
        
        if not verify_user_password(email,password):
            return jsonify({"message": "Incorrect email or password"}), 400
        
        payload = {
            'sub': email, 
            'iat': datetime.utcnow(),  # Issued at
            'exp': datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)  # Expiration
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        return jsonify({"message": "Login Successful", "token": token, "user": email}), 200
        
    except Exception as e:
        return jsonify({"error": f"Internal error {str(e)}"}), 500

@auth.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return jsonify({"message": "This is Signup Page"}), 200
    
    try:
        if not request.is_json:
            return jsonify({"message": "JSON payload required"}), 400
        
        data = request.get_json()
        
        if data is None:
            return jsonify({"message": "Payload required"}), 400
        
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        
        if not all([name, email, password]):
            return jsonify({"message": "All fields required"}), 400
            
        # More comprehensive input validation
        invalid_chars = set('<>;&')
        if any(char in invalid_chars for char in email + password):
            return jsonify({"message": "Invalid characters in input"}), 400
            
        if not validate_email(email):
            return jsonify({"message": "Invalid email format"}), 400
            
        if not validate_password(password):
            return jsonify({"message": "Invalid password format or length"}), 400
            
        if user_exists(email):
            return jsonify({"message": "User already registered"}), 400
        
        user_in_pending_signups = user_exists_in_pending_signups(email)
        if user_in_pending_signups:
            if user_mail_verified(email):
                otp = generate_otp()
                res = send_otp(email, otp)
                send_otp_to_db(email, otp)
                if not res:
                    return jsonify({"message":"failed to send opt"}), 400
                return jsonify({"message": "Signup successful", "user":email, "email":"unverified"}), 201
            else:
                return jsonify({"message": f"User status {user_in_pending_signups[0][0]}"}), 400
        
        try:
            insert_user_to_pending(name, email, password)
            otp = generate_otp()
            res = send_otp(email, otp)
            send_otp_to_db(email, otp)
            if not res:
                return jsonify({"message":"failed to send opt"}), 400
            return jsonify({"message": "Signup successful", "user":email,"email":"unverified"}), 201
            
        except Exception as db_error:
            return jsonify({"message": "Database error occurred"}), 500
            
    except ValueError as ve:
        return jsonify({"message": str(ve)}), 400
    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500

cache = TTLCache(maxsize=100,ttl=300)

@auth.route('/forgot_password', methods=["GET","PUT"])
def forgot_password():
    try:
        if not request.is_json:
            return jsonify({"message": "JSON Payload required"}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({"message":"JSON payload required"}), 400
        email = data.get("email")
        password = data.get("password")
        
        if not all([email, password]):
            return jsonify({"message":"all fields required"}), 400
        if not validate_email(email):
            return jsonify({"message":"Invalid email format"}), 400
        if not validate_password(password):
            return jsonify({"message":"Invalid password format"}), 400
        if not user_exists(email):
            return jsonify({"message":"Please enter a valid email"}), 400
        # session['email'] = email
        # session['password'] = password
        cache[email] = password
        otp = generate_otp()
        res = send_otp(email, otp)
        res_2 = send_otp_to_db(email, otp)
        if not res:
            return jsonify({"message":"failed to send opt"}), 400
        return jsonify({"message":"password submited verify the otp", "user":email}),200
    
    except Exception as e:
        return jsonify({"message":"Internal server error"}), 500

@auth.route('/logout', methods=["POST"])
@token_required
def logout():
    """
    Handle logout requests via GET and POST methods.
    POST processes the logout action and invalidates the token.
    """
    try:
        # For JWT, we don't have a session to clear, but we can return success
        # The token_required decorator already verified the token
        return jsonify({"message": "Logout Successful"}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal error"}), 500

@auth.route('/refresh', methods=["POST"])
@token_required
def refresh_token():
    """
    Refresh the JWT token if it's close to expiration.
    """
    current_user = request.user
    payload = {
        'sub': current_user,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)
    }
    new_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return jsonify({"message": "Token refreshed", "new_token": new_token}), 200

@auth.route('/verify_email/<email>/<field>', methods=["POST"])
def verify_email(email, field):
    try:
        # Get JSON payload
        if not request.is_json:
            return jsonify({"message":"JSON payload required"})
        data = request.get_json()
        if data is None:
            return jsonify({"message": "JSON payload required"}), 400

        # Extract and validate OTP from payload
        user_otp = data.get("otp")
        if not user_otp:  # Check if OTP is missing or empty
            return jsonify({"message": "OTP is required"}), 400

        otp_details = get_otp()
        if not otp_details:
            return jsonify({"message":"Unable to fetch otp"})
        otp = otp_details.get("otp")
        valid_till = otp_details.get("valid_till")
        curr_time = datetime.datetime.now()
        if valid_till < curr_time:
            jsonify({"message":"Opt time out "}), 400

        # Check if OTP matches
        if str(user_otp) == str(otp):
            if field == "signup":
                success = update_user_email_status(email)
                if not success:
                    print(f"Failed to verify email for {email}")
                    return jsonify({"message": "Failed to verify email"}), 500
            elif field == "forgot":
                # password = session.get("password")
                # password = "Abhi@12345"
                password = cache.get(email)
                success_2 = reset_user_password(email, password)
                if not success_2:
                    return jsonify({"message":"Failed to reset password"}), 500
            res = delete_otp(email)
            return jsonify({"message": "Otp verified successfully"}), 200

        return jsonify({"message": "Invalid OTP"}), 401

    except ValueError as ve:
        print(f"Validation error: {str(ve)}")
        return jsonify({"message": "Invalid input data"}), 400
    except Exception as e:
        print(f"Unexpected error processing request for email {email}: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500
        