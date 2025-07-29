import os
import datetime
import json
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from molieregen.config import load_config, update_config_field
import shlex

TEMPLATE_JSON = {
    "client_name": "",
    "currency": "€",
    "items": [
        {
            "description": "",
            "quantity": 1,
            "unit_price": 0,
            "details": []
        }
    ]
}

def get_invoice_number(type):
    moliere_config = load_config()
    invoice_number = moliere_config.get(f"{type}_number", 1)
    moliere_config[f"{type}_number"] = int(invoice_number) + 1
    update_config_field(f"{type}_number", moliere_config[f"{type}_number"])
    return invoice_number

def generate_template_json(out_path: str = None):
    if out_path is None:
        out_path = os.path.join(os.getcwd(), "molieregen.json")
    
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(TEMPLATE_JSON, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Template created: {out_path}")
    return out_path

def generate_invoice_from_json(json_path, type):
    # Upload JSON config
    moliere_config = load_config()
    
    raw_template_path = moliere_config["template_path"]
    # Fix any shell-escaped formatting (e.g., from Terminal copy-paste)
    template_path = os.path.abspath(os.path.expanduser(shlex.split(raw_template_path)[0]))
    # Then continue normally:
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    
    with open(json_path, 'r', encoding='utf-8') as f:
        invoice_data = json.load(f)

    # Upload template
    invoice_data.setdefault("currency", "€")
    invoice_data["date"] = datetime.date.today().strftime("%d/%m/%Y")
    invoice_data["total"] = sum(i["quantity"] * i["unit_price"] for i in invoice_data["items"])
    invoice_data["currency"] = invoice_data["currency"]

    # Get number and type of invoice
    invoice_id = get_invoice_number(type)
    if type == "invoice":
        type = "Facture" 
    if type == "quote":
        type = "Devis"
    invoice_data["type"] = type
    invoice_data["invoice_id"] = invoice_id

    # Create final file
    client_name = invoice_data["client_name"]
    # Expand and sanitize base_dir (e.g. if it came from config)
    raw_base_dir = moliere_config.get("base_dir")
    base_dir = os.path.abspath(os.path.expanduser(shlex.split(raw_base_dir)[0]))

    # Ensure client folder exists
    client_folder = os.path.join(base_dir, client_name)
    os.makedirs(client_folder, exist_ok=True)

    # Build the output filename and full path
    output_filename = f"{invoice_data['type']}_{client_name}_{invoice_id}.pdf"
    output_path = os.path.join(client_folder, output_filename)

    # Render HTML and write PDF
    html_out = template.render(invoice_data)
    HTML(string=html_out, base_url=template_dir).write_pdf(output_path)

    # Final confirmation
    print("✅ PDF completed:", output_path)
    return output_path