from api.blueprints import user
from flask import jsonify, request
from api.user_api.utils.users_util import*
from psycopg2 import DatabaseError
from api.points_api.utils.points_util import get_user_points
@user.route('/get_user_profile',methods=["POST"])
def get_user_profile():
    try:
        if not request.is_json:
            return jsonify({"message":"It should contain JSON"}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({"message":"JSON cannot be empty"}), 400
        email = data.get("email")
        
        if not email or not email.strip():
            return jsonify({"message":"Email is required"}), 400
        
        response = get_user_details(email)
        
        if not response or response == {}:
            return jsonify({"message":"No such user exists"}), 400
        
        return jsonify({"message":response}), 200
    except DatabaseError as de:
        print(f"Database error : {str(de)}")
        return jsonify({"message":"Database error"}), 500
    except Exception as e:
        print(f"error: {str(e)}")
        return jsonify({"message":"Internal server error"}), 500
        
@user.route('/redeem_scheme',methods=["POST"])
def redeem_scheme():
    pass

@user.route('/top_users',methods=["GET"])
def top_user():
    try:
        if not request.is_json:
            return jsonify({"message": "Request must contain JSON"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"message": "JSON payload cannot be empty"}), 400

        limit = data.get("limit")
        if not limit:
            return jsonify({"message": "Limit is required"}), 400

        if not isinstance(limit, int):
            return jsonify({"message": f"Limit must be an integer, got {type(limit).__name__}"}), 400

        if limit <= 0:
            return jsonify({"message": "Limit must be a positive integer"}), 400
        
        if not response or response == []:
            return jsonify({"message":"Unable to fetch users, Please try later"}), 400
        
        response = get_user_with_most_points(limit)
        
        if not response:
            return jsonify({"message":"Unable to fetch top user, Please try later"}), 400
        return jsonify({"message":response}),200
    except DatabaseError as de:
        print(f"Database error: {str(de)}")
        return jsonify({"message":"Database error"}), 500
    except Exception as e:
        return jsonify({"message":f"Internal server error {str(e)}"}), 500
    
    
@user.route("get_users", methods=["GET"])
def get_users():
    try:
        limit = 0
        if request.is_json:
            data = request.get_json()
            if data:
                limit = data.get("limit")
        
        if limit and not isinstance(limit, int):
            return jsonify({"message":f"Limit should be tpye of int, but provided {type(limit).__name__}"}), 400

        res_limit = limit if limit else 10
        response = get_users_(res_limit)
        if not response:
            return jsonify({"message":"Unable to fetch user, Please try later"}), 400
        return response
    except DatabaseError as de:
        print(f"Database error {str(de)}")
        return jsonify({"message":"Database error"}), 500
    except Exception as e:
        print(f"errror:{str(e)}")
        return jsonify({"message":"Internal server error"}), 500
    
@user.route('/scheme_status',methods=["POST"])
def scheme_status():
    try:
        if not request.is_json:
            return jsonify({"message":"JSON paylaod required"}), 400
        data = request.get("email")
        if not data:
            return jsonify({"message":"JSON cannot be empty"}), 400
        email = data.get("email").strip()
        
        status = scheme_status(email)
        
        if not status:
            return jsonify({"message":"No scheme found"}), 404
        return jsonify({"response":status}), 200
    except DatabaseError as dber:
        print(f" Database error {str(dber)}")
        return jsonify({"message":"Database error"}), 500
    except Exception as e:
        print(f"Internal server error {str(e)}")
        return jsonify({"message":"Internal server error"}), 500
        
# need to be added to main api
@user.route('/get_schemes_for_user',methods=["GET"])
def get_scheme():
    try:
        schemes = get_schemes_()
        
        if not schemes:
            return jsonify({"message":"No scheme found"}), 404
        return jsonify({"response":schemes}), 200
    except DatabaseError as dber:
        print(f"Database error occured {str(dber)}")
        return jsonify({"message":"Database error"}), 500
    except Exception as e:
        print(f"Internal server error")
        return jsonify({"message":"Internal server error"}), 500

@user.route('/redeem_scheme',methods=["POST"])
def redeem_scheme():
    try:
        if not request.is_json:
            return jsonify({"message":"Request should contain JSON"}), 400
        data = request.get_json()
        if not data:
            return jsonify({"message":"JSON cannot be empty"}), 400
        email = data.get("email")
        scheme_id = data.get("scheme_id")
        if not email or not scheme_id:
            return jsonify({"message":"Email and Scheme_id required"}), 400
        email = email.strip()
        
    # need check if user have applied before or not
        if scheme_already_applied(email):
            return jsonify({"message":"Scheme alredy applied"}),400
        if not is_scheme_date_valid(scheme_id):
            return jsonify({"message":"Scheme expired"}), 400
    # need to check if user have enough point to apply scheme
        required_points = get_points_required_for_scheme(int(scheme_id))
        user_points = get_user_points()
        if user_points < required_points:
            return jsonify({"message":"Insufficient points"}), 400
        user_details = get_user_details(email)
        name = user_details.get("name")
        insert_scheme(name, email, scheme_id)
    
        return jsonify({"message":"Applied for scheme"}), 200
    except DatabaseError as dber:
        print(str(dber))
        return jsonify({"Database error"}), 500
    except Exception as e:
        print(str(e))
        return jsonify({"message":"Internal server error"}), 500
    
    
    
