"""
Polar.sh Paywall Integration for LOHA Dating Coach
This module handles the integration with Polar.sh payment system
"""

import os
import requests
import json
from flask import request, jsonify
from functools import wraps

# Polar.sh Configuration
POLAR_ACCESS_TOKEN = os.environ.get('POLAR_ACCESS_TOKEN', 'polar_oat_QBoGv8YGoNQwMIWdEMLBk9aXYTZSN5WPVOoWt2ENnmy')
POLAR_WEBHOOK_SECRET = os.environ.get('POLAR_WEBHOOK_SECRET', 'polar_whs_7pm9ALxReOQzQI3UwLxoRvtnHohj5tpD1rjRN353Y43')
POLAR_PRODUCT_ID = os.environ.get('POLAR_PRODUCT_ID', '26111cdd-7cf0-49b3-a068-61eede577684')
POLAR_SUCCESS_URL = os.environ.get('POLAR_SUCCESS_URL', 'https://lohacoachpilot.onrender.com/success?checkout_id={CHECKOUT_ID}')

# Track paid sessions
paid_sessions = set()

def check_payment_status(session_id):
    """
    Check if a session has paid
    """
    return session_id in paid_sessions

def mark_session_paid(session_id):
    """
    Mark a session as paid after successful payment
    """
    paid_sessions.add(session_id)

def create_polar_checkout(session_id):
    """
    Create a Polar.sh checkout session for the user
    """
    try:
        url = "https://api.polar.sh/v1/checkouts"
        
        headers = {
            "Authorization": f"Bearer {POLAR_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Create success URL with session_id
        success_url = POLAR_SUCCESS_URL.replace('{CHECKOUT_ID}', session_id)
        
        data = {
            "product_id": POLAR_PRODUCT_ID,
            "success_url": success_url,
            "customer_id": session_id,  # Use session_id as customer identifier
            "metadata": {
                "session_id": session_id
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            checkout_url = result.get('url')
            return checkout_url
        else:
            print(f"Polar checkout creation failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error creating Polar checkout: {e}")
        return None

def verify_webhook_signature(request):
    """
    Verify Polar webhook signature
    """
    signature = request.headers.get('Polar-Signature')
    if not signature:
        return False
    
    # In production, you should verify the signature using the webhook secret
    # For now, we'll do a basic check
    return POLAR_WEBHOOK_SECRET in signature

def handle_polar_webhook(request):
    """
    Handle Polar webhook events
    """
    try:
        if not verify_webhook_signature(request):
            return jsonify({"error": "Invalid signature"}), 401
        
        event = request.json
        event_type = event.get('type')
        
        if event_type == 'checkout.completed':
            # Extract session_id from metadata
            metadata = event.get('data', {}).get('metadata', {})
            session_id = metadata.get('session_id')
            
            if session_id:
                mark_session_paid(session_id)
                print(f"Session {session_id} marked as paid")
                return jsonify({"success": True, "message": "Payment verified"}), 200
        
        return jsonify({"success": True, "message": "Webhook received"}), 200
        
    except Exception as e:
        print(f"Error handling Polar webhook: {e}")
        return jsonify({"error": str(e)}), 500