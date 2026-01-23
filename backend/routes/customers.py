from flask import Blueprint, jsonify, render, Flask
from pydantic import ValidationError
from db import get_db_connection
from models.customer import CreateCustomer






