import sys
import os

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyformgen import generate_react_form

schema = {
    'first_name': {'label': 'First Name', 'type': 'text'},
    'age': {'label': 'Age', 'type': 'number'},
    'gender': {'label': 'Gender', 'type': 'select', 'options': ['Male', 'Female', 'Other']},
    'subscribe': {'label': 'Subscribe to Newsletter', 'type': 'checkbox'}
}




# Output path
output_path = "example/GeneratedForm.jsx"
generate_react_form(schema, output_path)
