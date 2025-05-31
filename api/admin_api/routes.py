from api.blueprints import admin  
from flask import jsonify, request  
from api.admin_api.utils.user_utils import*
from api.admin_api.utils.scheme_utils import*
from api.admin_api.utils.admin_utils import*
from api.decoraters import token_required
from datetime import date
from time import sleep
from api.login_api.utils.validate_utils import*
import jwt
import datetime
from api.config import JWT_ALGORITHM, JWT_EXPIRY_MINUTES,JWT_SECRET_KEY
from api.login_api.utils.otp_utlis import*
from api.points_api.utils.points_util import redeem_user_points
@admin.route('/')
def home():
    """ 
    Home route handler
    Returns a simple JSON response indicating the home page
    """
    try:
        return jsonify({"message": "This is home page"}), 200
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

@admin.route('/pending_signups', methods=['GET'])
def pending_signups():
    """ 
    Retrieve pending signups
    GET endpoint to fetch all users from pending signups
    Returns: JSON response with list of pending users or error message
    """
    try:
        data = get_user_from_pending_signups()
        if not data:
            return jsonify({"message": "No pending signups found"}), 404
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve pending signups", "message": str(e)}), 500

@admin.route('/approve_or_reject_pending_signups', methods=['POST'])  
def approve_or_reject():
    """
    Approve or reject pending signups
    POST endpoint to update the status of a pending signup
    Requires JSON payload with 'email' and 'status' fields
    Returns: JSON response indicating success or failure
    """
    try:
        # Check if request contains JSON data
        if not request.is_json:
            return jsonify({"message": "Request must contain JSON data"}), 400

        data = request.get_json()  # Safely get JSON data from request
        
        # Validate required fields
        email = data.get("email")
        status = data.get("status")
        
        if not all([email, status]):
            return jsonify({"message": "All fields (email, status) are required"}), 400

        # Update the signup status
        update_status = update_pending_signups_status(email, status)
        
        # need to implement that the user is present or not 
        if not update_status:
            return jsonify({"message": "Unable to update the status"}), 400
    
        res = insert_user_to_users(email)
        sleep(2)
        res_2 = insert_user_to_user_point(email)
        return jsonify({"message": "Status updated successfully"}), 200

    except ValueError as ve:
        return jsonify({"error": "Invalid input data", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred while processing the request", "message": str(e)}), 500
        
@admin.route('/delete_scheme',methods=['DELETE'])
def delete_scheme():
    try:
        if not request.is_json:
            return jsonify({"message": "Request must contain JSON data"}), 400
        data = request.get_json()
        id_ = data.get("id")
        
        if not data:
            return jsonify({"message":"JSON is cannot be empty"}), 400
        
        if not id_:
            return jsonify({"message":"Scheme id is required"}), 400
        response = remove_scheme(id_)
        if not isinstance(id_, int):
            return f"The scheme id should be of type int, but provided type is {type(id_).__name__}"
        if not response:
            return jsonify({"message":"Enter a valid Scheme Title"}), 400
        return jsonify({"message":"Scheme delete","scheme_id":id_}),200
    except Exception:
        return jsonify({"message":"Internal server error occured"}), 500
    
@admin.route('/add_scheme',methods=["POST"])
def add_schemes():
    try:
        if not request.is_json:
            return jsonify({"message": "Request must contain JSON data"}), 400
        data = request.get_json()
        
        if not data or data is None:
            return jsonify({"message":"JSON payload required"}), 400
        
        scheme_title = data.get("scheme_title")
        scheme_valid_from = data.get("scheme_valid_from")
        scheme_valid_to = data.get("scheme_valid_to")
        scheme_perks = data.get("scheme_perks")
        points = data.get("points")
        
        if not all([scheme_title,scheme_valid_from,scheme_valid_to, scheme_perks, points]):
            return jsonify({"message":"All fields required"}), 400
        if not all(isinstance(x, str) for x in [scheme_title, scheme_valid_from, scheme_valid_to, scheme_perks]):
            return jsonify({"message":"Type error to this scheme_title | scheme_valid_from | scheme_valid_to | scheme_perks"}), 400
        if not isinstance(points, int):
            return jsonify({"message":f"The points should be type of int, but provided {type(points).__name__}"}),400
        
        response = add_scheme(scheme_title,scheme_valid_from, scheme_valid_to, scheme_perks, points)
        if not response:
            return ({"message":"Unable to add scheme please try later"}), 400
        return jsonify({"message":"Scheme added","scheme_title":scheme_title}), 200
    except Exception as e:
        return jsonify({"message":f"Internal server error {str(e)}"}), 500
        
@admin.route('/update_scheme', methods=["PUT"])
def update_schemes():
    try:
        if not request.is_json:
            return jsonify({"message": "Request must contain JSON data"}), 400
        data = request.get_json()
        if not data or data is None:
            return jsonify({"message":"JSON payload required"})
        
        scheme_title = data.get("scheme_title")
        scheme_valid_from = data.get("scheme_valid_from")
        scheme_valid_to = data.get("scheme_valid_to")
        scheme_perks = data.get("scheme_perks")
        points = data.get("points")
        
        if not scheme_title:
            return jsonify({"message":"Scheme title required"}), 400
        if not any([scheme_valid_from, scheme_valid_to, scheme_perks, points]):
            return jsonify({"message": "At least one of the following fields is required: valid_from, valid_to, perks, points"}), 400
        if points:
            if not isinstance(points, int):
                return jsonify({"message":f"The type of point should be int, but provided {type(points).__name__}"}), 400
        response = update_scheme(scheme_title, scheme_valid_from, scheme_valid_to, scheme_perks, points)
        
        if not response:
            return jsonify({"message":"Unable update Scheme"}), 400
        return jsonify({"message":"Scheme Updated","Scheme title":scheme_title}), 200
    except Exception as e:
        return jsonify({"message":f"Internal server error {str(e)}"}), 500
    
@admin.route('/get_schemes',methods=["GET"])
def get_schemes():
    try:
        response = get_scheme()
        
        if not response or response is None:
            return jsonify({"message":"Unable to fetch scheme, Please try later"}), 400
        return jsonify({"message":response}), 200
    except Exception:
        return jsonify({"message":"Internal server error"})
    
@admin.route('/get_scheme_to_approve')
def get_scheme_to_approve():
    try:
        applied_schemes = get_schemes_to_approve()
        if not applied_schemes:
            return jsonify({"message":"No scheme found"}), 404
        return jsonify({"message":applied_schemes}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"message":"Internal server error"}), 500
    
@admin.route('/approve_scheme',methods=["POST"])
def approve_scheme():
    try:
        if not request.is_json:
            return jsonify({"message":"Request must contain JSON"}), 400
        data = request.get_json()
        
        if not data:
            return jsonify({"message":"JSON must contain data"}), 400
        scheme_id = data.get("id")
        email = data.get("email")
        
        if not scheme_id or not email:
            return jsonify({"message":"All fields required"}), 400
        response = enough_points_for_scheme(scheme_id, email) 
        if not  response[0]:
            return jsonify({"message":"Insuficient points"}), 400
        required_point = response[1]
        
        if not res:
            return jsonify({"message":"Not able to update point"}), 400
        res_2 = update_scheme_status(scheme_id, email)
        if not res_2:
            return jsonify({"message":"Unable to update the status, Please try later"}), 400
        res = redeem_user_points(email, required_point)
        return jsonify({"message":"Updated"}), 200
            
    except Exception as e:
        print("Internal server occred", e)
        return jsonify({"message":"Internal server error"})

@admin.route("/reject_scheme")
def reject_scheme():
    try:
        if not request.is_json:
            return jsonify({"message":"Request most contain JSON"}), 400
        data = request.get_json()
        
        if not data:
            return jsonify({"message":"JSON should not be empty"}), 400
        id_ = data.get("id")
        
        if not id_:
            return jsonify({"message":"JSON must contain the id field"}), 400
        if not isinstance(id_, int):
            return jsonify({"message":f"id' must be int (got {type(id_).__name__}: {id_})"}), 400
        response = reject_scheme(id_)
        
        if not response:
            return jsonify({"message":"Not able to update status"}), 400
        return jsonify({"message":"Updated"}), 200
    except Exception as e:
        print(f"Internal error {str(e)}")
        return jsonify({"message":"Internal server error"}), 500

@admin.route('/update_user_details',methods=["PUT"])
def update_user_details():
    try:
        if not request.is_json:
            return jsonify({"message":"Request must contain JSON"}), 400
        data = request.get_json()
        
        if not data or data == {}:
            return jsonify({"message":"JSON cannot be empty"}), 400
        
        email = data.get("email")
        points = data.get("points")
        name  = data.get("name")
        
        if not all([email, points, name]):
            return jsonify({"message":"All fields required"}), 400
        
        if not isinstance(points, int):
            print(f"Error: 'points' must be int (got {type(points).__name__}: {points})")
            return jsonify({"message":"Type error"}), 400
        
        response = update_user_details_(email, points, name)
        if not response:
            return jsonify({"message":"Unable to update the data check the data correctly"}), 400
        return jsonify({"message":"user details updated"}), 200
        
    except Exception as e:
        print(f"Internal server error {str(e)}")
        return jsonify({"message":"Internal server error"}), 500
    
@admin.route("/delete_user",methods=["DELETE"])
def delete_user():
    try:
        if not request.is_json:
            return jsonify({"message":"Reuest most contain JSON"}), 400
        data = request.get_json()
        if not data:
            return jsonify({"message":"JSON cannot be empty"}), 400
        email = data.get("email")
        if not email:
            return jsonify({"message":"Email is reuired"}), 400
        response = delete_user(email)
        
        if not response:
            return jsonify({"message":"Unable to delete user"}), 400
        return jsonify({"message":"User deleted"}),200
    except Exception as e:
        print(f"Internal server error {str(e)}")
        return jsonify({"message":"Internal server error"}),500
    
@admin.route('/send_otp',methods=["POST"])
def send_otp():
    try:
        if not request.is_json:
            return jsonify({"message":"Request must contain JSON payload"}), 400
        data = request.get_json()
        
        if not data:
            return jsonify({"message":"Payload cannot be empty"}), 400
        email = data.get("email")
        if not email:
            return jsonify({"message":"Email is required"}), 400
        email = email.strip()
        if not validate_email(email):
            return jsonify({"message":"Wrong email format"}), 400
        
        if not is_admin_present(email):
            return jsonify({"message":"Wring mail id"}), 400
        
        otp = generate_otp()
        response = send_otp(email, otp)
        if not response:
            return jsonify({"message":"Not able to send otp"}), 400
        res = send_otp_to_db(email, otp)
        
        return jsonify({"message":"OTP sent"}), 200
    except Exception as e:
        print(f"Internal server error {str(e)}")
        return jsonify({"message":"Internal server error"}), 500
        
@admin.route('/verify_otp',methods=["POST"])
def verify_otp():
    try:
        if not request.is_json:
            return jsonify({"message":"Request must contain JSON payload"}), 400
        data = request.get_json()
        
        if not data:
            return jsonify({"message":"Payload cannot be empty"}), 400
        email = data.get("email")
        otp = data.get("otp")
        
        if not otp or not email:
            return jsonify({"message":"All fiels required"}), 400
        otp_details = get_otp(email)
        
        if not otp_details:
            return jsonify({"message":"Unable to fetch otp"})
        
        db_otp = otp_details.get("otp")
        valid_till = otp_details.get("valid_till")
        curr_time = datetime.datetime.now()
        
        if valid_till < curr_time:
            return jsonify({"message":"Opt time out "}), 400
            
        if str(db_otp) != str(otp):
            return jsonify({"message":"Incorrect opt"}), 400
        return jsonify({"message":"Otp verified"}), 200
    except Exception as e:
        print(f"Internal server error {str(e)}")
        return jsonify({"message":"Internal server error"}), 500

@admin.route('/admin_login', methods=["POST"])
def admin_login():
    try:
        if not request.is_json:
            return jsonify({"message":"Request must contain JSON payload"}), 400
        data = request.get_json()
        
        if not data:
            return jsonify({"message":"Payload cannot be empty"}), 400
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"message":"All fields required"}), 400
        if not validate_email(email):
            return jsonify({"message":"Invalid email format"}), 400
        if not validate_password(password):
            return jsonify({"message":"Invalid password format or lenght"}), 400
        if not is_admin_present(email):
            return jsonify({"message":"Invalid email or password"}), 400
        if not validate_admin_password(email, password):
            return jsonify({"message":"Invalid email or password"}), 400
        payload = {
        'sub': email, 
        'iat': datetime.utcnow(),  # Issued at
        'exp': datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)  # Expiration
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        return jsonify({"message": "Login Successful", "token": token, "user": email}), 200
    except DatabaseError as dber:
        print(f"Database error: {str(dber)}")
        return jsonify({"Database error"}), 500
    except Exception as e:
        print(f"Internal server error {str(e)}"), 500