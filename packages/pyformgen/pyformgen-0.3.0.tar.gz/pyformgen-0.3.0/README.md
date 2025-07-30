# FormGen

`FormGen` is a Python tool that helps you quickly generate React form components from JSON schemas. It’s useful for frontend-backend integration workflows, rapid prototyping, or generating boilerplate form code in large projects.

---

## 📂 Project Structure

```
formgen/
├── package/
│   └── react_generator.py
├── test/
│   └── test_react.py
├── sample_schema.json
├── README.md
└── setup.py
```

---

## Installation

You can install this package locally using:

```bash
pip install .
```

Or, if uploading to PyPI:

```bash
pip install formgen
```

---

## How to Use

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

### 2. Write your Python script

Use the `generate_react_form` function to generate your form component.

**Example: `test/test_react.py`**
```python
import json
from package.react_generator import generate_react_form

with open("sample_schema.json") as f:
    schema = json.load(f)

output_path = "GeneratedForm.jsx"
generate_react_form(schema, output_path)
```

### 3. Run the script

```bash
python test/test_react.py
```

After running, you'll get a `GeneratedForm.jsx` file containing a full React form component.

---

## 🧪 Output

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
      ...
      <button type="submit">Submit</button>
    </form>
  );
}
```

---

##  Field Attributes Supported

Each field can have:

- `label`: The label shown beside the input
- `type`: Input type (text, email, password, etc.)
- `required`: Boolean to mark required fields
- `placeholder`: Placeholder text

---

## 🛠 Development

Clone the repository and install locally:

```bash
git clone https://github.com/yourusername/formgen.git
cd formgen
pip install -e .
```

You can add tests in the `test/` directory and schemas in JSON format to test new features.

---

## License

MIT License. See `LICENSE` file for more details.
