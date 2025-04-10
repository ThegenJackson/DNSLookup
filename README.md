# DNSLookup Tool

A command-line tool to quickly retrieve essential DNS and WHOIS information for a given domain using native Python libraries. Designed for MSPs and IT professionals needing to investigate domain configurations without relying on external command-line utilities like `dig` or `whois`.


## Features

*   **Platform Independent:** Runs anywhere Python runs
*   Retrieves **Domain Registrant** (Registered owner name/organization).
*   Retrieves **Domain Registrar** (The company managing the domain registration).
*   Lists **Authoritative Nameservers** (NS Records) for the domain.
*   Infers the **DNS Hosting Provider** by performing a WHOIS lookup on the *owner domain* of the primary nameserver.


## Prerequisites

Before installing, ensure you have the following installed on your system:

1.  **Python 3.7+**
2.  **pip** (The Python package installer, typically included with Python)
3.  **Git** (Required by `pip` to clone the repository during installation)

### Installing Git

Windows: `winget install --id Git.Git -e --source winget`

Linux (Debian based ditributions): `sudo apt install git-all`

Other Linux distributions: `sudo dnf install git-all`

MacOS: `git --version`


## Installation

1.  **Prerequisites:** Ensure you have Python 3.7+ and Git installed and available in your system's PATH.
2.  **Install via pip:** Open your terminal (Command Prompt, PowerShell, Bash, etc.) and run:

    ```bash
    pip install git+https://github.com/ThegenJackson/DNSLookup.git
    ```

> **Important Note for Windows Users (PATH Environment Variable):**
>
> After installation, you might see a **WARNING** message in your terminal similar to this:
> ```
> WARNING: The script dnslookup.exe is installed in 'C:\Users\YourUsername\AppData\Roaming\Python\Python312\Scripts' which is not on PATH.
> ```
> If you see this warning, the `dnslookup` command will **not** work immediately because Windows doesn't know where to find the executable.
>
> To resolve this **copy the exact directory path** shown in *your* warning message (e.g., `C:\Users\YourUsername\AppData\Roaming\Python\Python312\Scripts`) and **add this path** to your Windows **PATH Environment Variable**.

## Usage

Run the tool from your command line, providing the domain name you want to check as an argument:

`dnslookup <domain_name>`

Example usage: `dnslookup google.com`


## License

This project is licensed under the MIT License.


## Issues

Please report any bugs or feature requests through the GitHub Issues page for this repository.