from api.blueprints import user
from flask import jsonify, request
from api.user_api.utils.users_util import get_user_details, get_user_with_most_points, get_users_, is_scheme_date_valid
from psycopg2 import DatabaseError


@user.route('/get_user_profile',methods=["GET"])
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
    

@user.route('/scheme_status')
def scheme_status():
    # this returns an statment if there no scheme else return the scheme details 
    pass
@user.route('/redeem_scheme')
def redeem_scheme():
    # this the route to apply for the scheme
    pass 

@user.route('/get_schemes')
def get_scheme():
    pass