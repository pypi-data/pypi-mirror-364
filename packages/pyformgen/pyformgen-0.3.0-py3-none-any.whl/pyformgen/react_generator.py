def to_camel_case_setter(name):
    return "set" + name[0].upper() + name[1:]

def generate_react_form(schema, output_path):
    imports = "import { useState } from 'react';\n\n"
    state_hooks = ""
    inputs = ""

    for name in schema:
        props = schema[name] if isinstance(schema[name], dict) else {}
        label = props.get("label", name.capitalize())
        input_type = props.get('type', "text")

        dynamic_attrs = ""
        for key, value in props.items():
            if key == "label":
                continue
            if isinstance(value, bool):
                if value:
                    dynamic_attrs += f" {key}"
            else:
                dynamic_attrs += f' {key}="{value}"'

        setter = to_camel_case_setter(name)
        state_hooks += f"  const [{name}, {setter}] = useState(\"\");\n"

        inputs += f"""
      <div>
        <label>{label}</label>
        <input
          name="{name}"
          value={{ {name} }}
          onChange={{(e) => {setter}(e.target.value)}}
          {dynamic_attrs}
        />
      </div>"""

    state_names = ', '.join(schema.keys())

    jsx = f"""{imports}export default function Form() {{
{state_hooks}

  const handleSubmit = (e) => {{
    e.preventDefault();
    console.log({{{state_names}}});
  }};
                
  return (
    <form onSubmit={{handleSubmit}}>
      {inputs}
      <button type="submit">Submit</button>
    </form>
  );
}}"""

    if not output_path.endswith(".jsx"):
        output_path += ".jsx"

    with open(output_path, "w") as f:
        f.write(jsx)

    print(f" React form generated successfully at {output_path}")
