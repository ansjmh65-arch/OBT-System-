# -*- coding: utf-8 -*-
from quart import Blueprint, jsonify, render_template

dashboard_bp = Blueprint("dashboard", __name__)
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

@dashboard_bp.route("/")
async def dashboard_index() -> str:
    return await render_template("index.html")

@api_bp.route("/status", methods=["GET"])
async def api_status():
    return jsonify({
        "status": "operational",
        "system": "OBT Enterprise Core",
        "version": "3.0.0"
    })
  
