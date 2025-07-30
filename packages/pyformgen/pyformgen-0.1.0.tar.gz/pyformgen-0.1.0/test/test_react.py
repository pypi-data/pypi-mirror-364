import sys
import os

# Add the root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from package import generate_react_form

schema = {
    "title": "Contact Form",
    "fields": [
        {
            "name": "email",
            "label": "Email Address",
            "type": "email",
            "required": True,
            "placeholder": "you@example.com"
        },
        {
            "name": "message",
            "label": "Your Message",
            "type": "textarea",
            "required": True,
            "minLength": 10
        },
        {
            "name": "subscribe",
            "label": "Subscribe to newsletter",
            "type": "checkbox"
        }
    ]
}



# Output path
output_path = "example/GeneratedForm.jsx"
generate_react_form(schema, output_path)
