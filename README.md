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

You can install the `DNSLookup` tool directly from GitHub using `pip`:

```bash
pip install git+https://github.com/ThegenJackson/DNSLookup.git
```


## Usage

Run the tool from your command line, providing the domain name you want to check as an argument:

`dnslookup <domain_name>`

Example usage: `dnslookup google.com`


## License

This project is licensed under the MIT License.


## Issues

Please report any bugs or feature requests through the GitHub Issues page for this repository.