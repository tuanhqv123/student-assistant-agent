from flask import Blueprint, request, jsonify
from ..services.ptit_auth_service import PTITAuthService
from ..utils.logger import Logger

auth_bp = Blueprint('auth', __name__)
logger = Logger()
ptit_auth_service = PTITAuthService()

@auth_bp.route('/verify-university-credentials', methods=['POST'])
def verify_university_credentials():
    data = request.json
    university_username = data.get('university_username')
    university_password = data.get('university_password')

    if not university_username or not university_password:
        return jsonify({
            'error': 'Missing username or password'
        }), 400

    try:
        # Log the verification attempt
        logger.log_with_timestamp(
            "AUTH REQUEST", 
            f"Verifying credentials for user: {university_username}"
        )

        # Authenticate with PTIT API
        success, error = ptit_auth_service.login(university_username, university_password)
        
        if success:
            # Get current semester information
            semester, semester_error = ptit_auth_service.get_current_semester()
            if semester:
                return jsonify({
                    'success': True,
                    'current_semester': semester
                })
            else:
                return jsonify({
                    'error': f'Failed to get semester data: {semester_error}'
                }), 500
        else:
            return jsonify({
                'error': error or 'Authentication failed'
            }), 401

    except Exception as e:
        error_message = str(e)
        logger.log_with_timestamp("AUTH ERROR", error_message)
        return jsonify({
            'error': 'Failed to verify university credentials'
        }), 500

@auth_bp.route('/ptit-login', methods=['POST'])
def ptit_login():
    data = request.json
    university_username = data.get('university_username')
    university_password = data.get('university_password')

    if not university_username or not university_password:
        return jsonify({
            'error': 'Missing username or password',
            'result': 'false'
        }), 400

    try:
        # Log the login attempt
        logger.log_with_timestamp(
            "PTIT LOGIN REQUEST", 
            f"Login attempt for user: {university_username}"
        )

        # Get the raw login response from PTIT
        login_success, login_result = ptit_auth_service.login_raw(university_username, university_password)
        
        if login_success:
            # Return the complete login response data
            return jsonify(login_result)
        else:
            # Return error
            return jsonify({
                'error': login_result or 'Authentication failed',
                'result': 'false'
            }), 401

    except Exception as e:
        error_message = str(e)
        logger.log_with_timestamp("PTIT LOGIN ERROR", error_message)
        return jsonify({
            'error': 'Failed to authenticate with PTIT',
            'result': 'false'
        }), 500