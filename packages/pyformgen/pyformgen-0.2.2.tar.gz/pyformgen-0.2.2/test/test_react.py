import sys
import os

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyformgen.react_generator import generate_react_form

schema = {
  "first_name": {
    "label": "First Name",
    "type": "text",
    "placeholder": "Enter your first name",
    "required": True
  },
  "age": {
    "label": "Age",
    "type": "number",
    "placeholder": "Enter your age",
    "required": True,
    "min": 0
  },
  "gender": {
    "label": "Gender",
    "type": "select",
    "required": True,
    "options": [
      { "value": "male", "label": "Male" },
      { "value": "female", "label": "Female" },
      { "value": "other", "label": "Other" }
    ]
  },
  "subscribe": {
    "label": "Subscribe to Newsletter",
    "type": "checkbox",
    "required": False
  }
}





# Output path
output_path = "example/GeneratedForm.jsx"
generate_react_form(schema, output_path)
