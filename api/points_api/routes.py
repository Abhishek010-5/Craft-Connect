from api.blueprints import points
from flask import jsonify, request
from datetime import datetime
from api.points_api.utils.points_util import execute_pin_validation, get_user_points,redeem_user_points, add_user_points
from api.login_api.utils.validate_utils import validate_email
from psycopg2 import DatabaseError
# @points.route('/')
# def home():
#     return jsonify({"message": "This is home page"}), 200

@points.route('/redeem_points', methods=["PUT"])
def redeem_points():
    try:
        if not request.is_json:
            return jsonify({"error": "JSON data required"}), 400

        data = request.get_json()
        email = data.get("email")
        points = data.get("points")
        
        if not points or not isinstance(points, (int)) or points <= 0:
            return jsonify({"message": "Valid positive points required"}), 400
        if not email:
            return jsonify({"message":"All fields required"}), 400
        email = email.strip()
        if not validate_email(email):
            return jsonify({"message":"Incorrect email format"}), 400
        
        user_points = get_user_points(email)
        
        if points > user_points:
            return jsonify({"message":"Insuficient points"}), 400

        response = redeem_user_points(email,points)
        if not response:
            return jsonify({"message":"Unable to redeem points"}), 400
        return jsonify({"message":"Points redeemed","remaining points":user_points - points,"points redeemed":points},), 200
    except DatabaseError as de:
        print(f"Error {str(e)}")
        return jsonify({"message":"Database error occured"}), 500
    except Exception as e:
        print(f"Error in :{str(e)}")
        return jsonify({"error":"Internal server error"}), 500

@points.route('/get_points', methods=["GET","POST"])
def get_points():
    try:
        if not request.is_json:
            return jsonify({"error": "JSON data required"}), 400

        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email required"}), 400
        if email:
            email = email.strip()
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        points = get_user_points(email)
        if not points:
            return jsonify({"message":"Unable to find points, please try later"}), 400
        return jsonify({"points": points}), 200
    except DatabaseError as de:
        print(f"Error: {str(de)}")
        return jsonify({"message":"Database error occured"}), 500

    except Exception as e:
        print(f"Error in {str(e)}")
        return jsonify({"error":"Internal server error"}), 500
    
@points.route('/validate_points',methods=["PUT"])
def validate_points():
    try:
        if not request.is_json:
            return jsonify({"error":"JSON data required"}), 400
        data = request.get_json()
        email = data.get("email")
        points = data.get("points")
        
        if not points or points == []:
            return jsonify({"message":"Points required"}), 400
        if not email:
            return jsonify({"message":"Emial required"}), 400
        
        email = email.strip()
        response = execute_pin_validation(points)
        
        if not response:
            return jsonify({"message":"Unable to process"}), 400
        total_points = response.get("total_points")
        
        if int(total_points) > 0:
            update_point = add_user_points(email, int(total_points))
            if not update_point:
                return jsonify({"message":"Not able to update point"}), 400
        return jsonify({"message":"Points updated","details":response}), 200
    except DatabaseError as de:
        print(f"Error in {str(de)}")
        return jsonify({"message":"Database error occured"}), 500
    except Exception as e:
        print(f"Error in {str(e)}")
        return jsonify({"message":"Internal server error"}), 500
        
