# 📦 Molière

**Generate elegant invoices and quotes from JSON and HTML templates – right from your terminal.**

Molière is a simple but powerful CLI tool for developers, freelancers, and small businesses to create beautiful PDF invoices and quotes from JSON files and customizable HTML/CSS templates.

---

## 🚀 Features

- Create invoices and quotes in PDF format  
- Fully customizable HTML/CSS templates  
- Simple JSON-based data structure  
- Easily configurable via CLI or config file  
- Shell completions support  
- Portable and script-friendly

---

## ⚙️ Installation

Install via PyPI:

```
pip install molieregen
```

---

## 📖 Usage

```
molieregen [OPTIONS] COMMAND [ARGS]...
```

### Global Options

| Option                 | Description                                               |
|------------------------|-----------------------------------------------------------|
| `--install-completion` | Install shell completion for the current shell            |
| `--show-completion`    | Show completion code for manual installation              |
| `--help`               | Show help message and exit                                |

---

## 🛠 Commands

### 🔧 `configure`

Interactively configure default paths and values.

```
molieregen configure
```

This creates or updates the config file at `~/.molieregen/config.json`.

---

### 🧾 `generate`

Generate a PDF invoice or quote from a JSON file.

```
molieregen generate ./invoice.json
```

The output will be saved to the configured `output_dir`.

---

### 📝 `json`

Generate a default JSON structure for an invoice or quote.

```
molieregen json invoice > invoice.json
molieregen json quote > quote.json
```

Use this as a starting point and customize the fields as needed.

---

### ⚙️ `set-config`

Update a single configuration value directly.

```
molieregen set-config template_dir ./my-templates
molieregen set-config output_dir ./exports
```

This modifies the `~/.molieregen/config.json` file.

---

## 📂 Example Workflow

1. Create a base invoice:
    ```
    molieregen json invoice > invoice.json
    ```

2. Edit `invoice.json` to reflect your client, services, pricing, etc.

3. Generate the PDF:
    ```
    molieregen generate invoice.json
    ```

4. Find the output in your configured output directory.

---

## 🎨 Custom Templates

Templates are standard HTML files with placeholders for data.

- Default templates are included with Molière  
- You can override by setting a custom template path:
    ```
    molieregen set-config template_path ./custom_template.html
    ```

Template files can use basic CSS and HTML along with variables like:
```
{{ invoice.number }}
{{ client.name }}
{{ items[0].description }}
```

---

## 🔒 Configuration

Molière stores user preferences in:

```
~/.molieregen/config.json
```

Example:
```
{
  "output_dir": "./exports",
  "template_path": "./templates/invoice.html",
  "author_name": "John Doe",
  "default_currency": "EUR"
}
```

---

## 🧪 Coming Soon

- Multi-language support  
- Emailing invoices directly from CLI  
- Convert CSV to invoice  
- Built-in template gallery

---

## 🤝 Contributing

Pull requests and feedback are welcome!

1. Fork the repo  
2. Create your feature branch (`git checkout -b feature/my-feature`)  
3. Commit your changes (`git commit -am 'Add some feature'`)  
4. Push to the branch (`git push origin feature/my-feature`)  
5. Open a pull request

---

## 🧑‍💻 Author

Made with 💡 by Caribbean Code
GitHub: [https://github.com/kenyhenry/moiliere.git](https://github.com/kenyhenry/moiliere)

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
