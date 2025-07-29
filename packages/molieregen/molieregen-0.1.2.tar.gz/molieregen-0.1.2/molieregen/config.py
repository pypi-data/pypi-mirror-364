import os
import json
import shlex

CONFIG_PATH = os.path.expanduser("~/.molieregen/config.json")


def prompt_initial_config():
    print("🔧 First-time configuration for Molière\n")

    base_dir = input(f"📁 Where should Molière store its data?")
    base_dir = os.path.join(os.path.expanduser(base_dir), "molieregen")
    os.makedirs(base_dir, exist_ok=True)

    template_path = input("📄 Full path to your HTML template file (e.g., https://github.com/kenyhenry/moiliere/tree/main/templates_exemple/caribbeancode.html): ").strip()
    template_path = os.path.expanduser(template_path)
    cleaned_path = shlex.split(template_path)[0]
    while not os.path.isfile(cleaned_path):
        print("⚠️ Invalid path. Please provide a valid HTML template path.")
        template_path = input("📄 HTML template file path: ").strip()
        template_path = os.path.expanduser(template_path)

    config = {
        "base_dir": base_dir,
        "template_path": os.path.abspath(template_path),
        "invoice_number": 1,
        "quote_number": 1,
    }

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Configuration saved to {CONFIG_PATH}")
    return config

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return prompt_initial_config()
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def change_config():
    print("⚙️ Reconfiguring Molière...\n")
    return prompt_initial_config()

def update_config_field(field: str, value):
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError("Config file not found. Please run `molieregen configure` first.")

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    config[field] = value

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Updated '{field}' to: {value}")