# FormGen

`FormGen` is a Python tool that helps you quickly generate React form components from JSON schemas. It’s useful for frontend-backend integration workflows, rapid prototyping, or generating boilerplate form code in large projects.

## Installation

You can install this package locally using:

```bash
pip install .
```

Or, if uploading to PyPI:

```bash
pip install formgen
```

## How to Use

The core functionality of `FormGen` is provided by the `generate_react_form` function, located within the `react_generator` module of the `formgen` package. This function takes a JSON schema and an output file path to generate a React form component.

### 1. Prepare a JSON schema

Create a JSON file that defines your form fields and their properties.

**Example: `sample_schema.json`**

```json
{
  "username": {
    "label": "Username",
    "type": "text",
    "required": true,
    "placeholder": "Enter your username"
  },
  "email": {
    "label": "Email Address",
    "type": "email",
    "required": true
  },
  "password": {
    "label": "Password",
    "type": "password",
    "required": true
  }
}
```

### 2. Generate your React form component

Use the `generate_react_form` function from `formgen.react_generator` in your Python script.

**Example Python Script:**

```python
import json
from formgen.react_generator import generate_react_form

# Load your JSON schema
with open("sample_schema.json") as f:
    schema = json.load(f)

# Define the output path for your React component
output_path = "GeneratedForm.jsx"

# Generate the React form component
generate_react_form(schema, output_path)

print(f"React form component generated at: {output_path}")
```

### 3. Run the script

```bash
python your_script_name.py
```

After running, you'll find a `GeneratedForm.jsx` file (or whatever you named it) containing a full React form component ready for use in your React application.

##    Output

The generated JSX form will look like this (simplified):

```jsx
import { useState } from 'react';

export default function Form() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log({ username, email, password });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Username</label>
        <input
          name="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          placeholder="Enter your username"
          type="text"
        />
      </div>
      <div>
        <label>Email Address</label>
        <input
          name="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          type="email"
        />
      </div>
      <div>
        <label>Password</label>
        <input
          name="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          type="password"
        />
      </div>
      <button type="submit">Submit</button>
    </form>
  );
}
```

## Field Attributes Supported

Each field in your JSON schema can have the following attributes:

- `label`: The label text displayed beside the input field.
- `type`: The HTML input type (e.g., `text`, `email`, `password`, `number`, `checkbox`, `radio`, `textarea`, `select`).
- `required`: A boolean value (`true` or `false`) to mark the field as required.
- `placeholder`: Placeholder text displayed inside the input field before user input.
- `options`: (For `select` or `radio` types) An array of objects, each with `value` and `label` properties.

```json
"role": {
  "label": "Role",
  "type": "select",
  "options": [
    {"value": "admin", "label": "Administrator"},
    {"value": "user", "label": "Regular User"}
  ]
}
```

## License

MIT License. See `LICENSE` file for more details.
