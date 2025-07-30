def to_camel_case_setter(name):
    return "set" + name[0].upper() + name[1:]

def generate_react_form(schema, output_path):
    imports = "import { useState } from 'react';\n\n"
    state_hooks = ""
    inputs = ""
    form_data_object = ""

    for name in schema:
        props = schema[name] if isinstance(schema[name], dict) else {}
        label = props.get("label", name.capitalize())
        input_type = props.get("type", "text")

        setter = to_camel_case_setter(name)
        state_hooks += f"  const [{name}, {setter}] = useState(\"\");\n"
        form_data_object += f"      {name},\n"

        dynamic_attrs = ""
        for key, value in props.items():
            if key in ["label", "options", "type"]:
                continue
            if isinstance(value, bool):
                if value:
                    dynamic_attrs += f" {key}"
            else:
                dynamic_attrs += f' {key}="{value}"'

        if input_type == "select":
            options = props.get("options", [])
            options_jsx = ""
            for opt in options:
                if isinstance(opt, dict):
                    val = opt.get("value", opt.get("label", ""))
                    label_val = opt.get("label", val)
                    options_jsx += f'            <option value="{val}">{label_val}</option>\n'
                else:
                    options_jsx += f'            <option value="{opt}">{opt}</option>\n'

            inputs += f"""
      <div>
        <label>{label}</label>
        <select
          name="{name}"
          value={{ {name} }}
          onChange={{(e) => {setter}(e.target.value)}}
          {dynamic_attrs}
        >
{options_jsx}        </select>
      </div>"""
        else:
            inputs += f"""
      <div>
        <label>{label}</label>
        <input
          name="{name}"
          value={{ {name} }}
          onChange={{(e) => {setter}(e.target.value)}}
          type="{input_type}"
          {dynamic_attrs}
        />
      </div>"""

    jsx = f"""{imports}
export default function GeneratedForm() {{
{state_hooks}
  const handleSubmit = (e) => {{
    e.preventDefault();
    const formData = {{
{form_data_object}    }};
    console.log("Submitted data:", formData);
  }};

  return (
    <form onSubmit={{handleSubmit}}>
{inputs}
      <button type="submit">Submit</button>
    </form>
  );
}}
"""

    if not output_path.endswith(".jsx"):
        output_path += ".jsx"

    with open(output_path, "w") as f:
        f.write(jsx)

    print(f" React form generated successfully at {output_path}")
