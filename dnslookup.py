#!/usr/bin/env python3
import argparse
import sys
import tldextract
import whois
import dns.resolver
import socket
from typing import List, Tuple, Optional, Any

# Helper function to safely get WHOIS data
def get_whois_info(domain: str) -> Optional[Any]:
    """Performs a WHOIS lookup for the domain and handles common errors."""
    try:
        # timeout parameter might not be supported by all underlying whois libs/servers
        # The default whois library might follow redirects, which can be slow.
        return whois.whois(domain)
    except whois.exceptions.UnknownTld:
        print(f"Warning: WHOIS lookup failed for '{domain}'. Unknown TLD.")
        return None
    except whois.exceptions.WhoisCommandFailed as e:
        print(f"Warning: WHOIS command execution failed for '{domain}': {e}")
        return None
    except whois.exceptions.PywhoisError as e: # General catch-all for the library
        print(f"Warning: WHOIS lookup error for '{domain}': {e}")
        return None
    except socket.timeout:
        print(f"Warning: WHOIS lookup for '{domain}' timed out.")
        return None
    except Exception as e: # Catch any other unexpected errors
        print(f"Warning: An unexpected error occurred during WHOIS lookup for '{domain}': {e}")
        return None

# Helper function to get DNS records
def get_dns_records(domain: str, record_type: str) -> Tuple[List[str], Optional[str]]:
    """
    Performs a DNS lookup for the specified record type and handles common errors.
    Returns a list of record strings and an optional error message.
    """
    records = []
    error_msg = None
    try:
        resolver = dns.resolver.Resolver()
        # resolver.nameservers = ['8.8.8.8', '1.1.1.1']
        answer = resolver.resolve(domain, record_type, raise_on_no_answer=False) # Don't raise, check rrset

        if answer.rrset is None:
            # Handles CNAMEs implicitly for A/AAAA lookups
            # No answer means no explicit NS records found at this level
            if record_type == 'NS':
                 # Check if it's possibly a CNAME pointing elsewhere
                 try:
                     cname_answer = resolver.resolve(domain, 'CNAME')
                     if cname_answer.rrset:
                          cname_target = cname_answer.rrset[0].to_text().rstrip('.')
                          error_msg = f"No direct {record_type} records found, but found CNAME: {cname_target}"
                     else:
                          error_msg = f"No {record_type} records found."
                 except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                      error_msg = f"No {record_type} records found."
            else:
                error_msg = f"No {record_type} records found."
            return [], error_msg

        # Process the found records
        for rdata in answer:
            record_text = rdata.to_text().rstrip('.') # Clean trailing dot
            records.append(record_text)

    except dns.resolver.NXDOMAIN:
        error_msg = f"Domain '{domain}' does not exist (NXDOMAIN)."
    except dns.resolver.NoAnswer:
        # This is now handled by raise_on_no_answer=False and checking rrset,
        # but kept here as a safeguard or for other potential scenarios.
        error_msg = f"No {record_type} records found for '{domain}'."
    except dns.resolver.NoNameservers:
        error_msg = f"Could not contact nameservers for '{domain}'."
    except dns.resolver.Timeout:
        error_msg = f"DNS query for {record_type} records of '{domain}' timed out."
    except Exception as e:
        error_msg = f"An unexpected DNS error occurred for '{domain}' ({record_type}): {e}"

    if not records and not error_msg:
         error_msg = f"No {record_type} records found (or query failed silently)."

    return records, error_msg


# Helper function to extract primary value from WHOIS results
def get_primary_whois_value(data: Optional[Any]) -> str:
    """Gets the primary string value from WHOIS result (handles lists/None)."""
    if data is None:
        return "Not Found"
    if isinstance(data, list):
        # Often the first item is the primary one, filter empty strings
        filtered_list = [item for item in data if isinstance(item, str) and item.strip()]
        return filtered_list[0] if filtered_list else "Not Found"
    elif isinstance(data, str):
        return data.strip() if data.strip() else "Not Found"
    else:
        return str(data) # Fallback

# Extracts Registrable Domain using tldextract
def get_registrable_domain(fqdn: str) -> Optional[str]:
    """
    Extracts the registrable domain (e.g., example.com, example.co.uk)
    from a fully qualified domain name (e.g., ns1.example.com) using tldextract.
    """
    if not fqdn:
        return None
    try:
        ext = tldextract.extract(fqdn, include_psl_private_domains=True)
        if ext.registered_domain:
             return ext.registered_domain
        else:
            print(f"Warning: Could not extract registrable domain from '{fqdn}'")
            return None
    except Exception as e:
        print(f"Error using tldextract on {fqdn}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="""
Get DNS and WHOIS info for a domain using Python libraries.

Outputs the Registrant, Registrar, Nameservers, and inferred
DNS Hosting Provider (Registrar of the nameserver's owner domain).

Definitions:
  - Registrant: The person or organisation who registered the domain.
  - Registrar: The company managing the domain's registration.
  - Nameservers: The Authoritative DNS Servers listed for the domain.
  - DNS Hosting Provider: The platform inferred to host the DNS Records
    (determined by WHOIS lookup on the nameserver's owner domain).
""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("domain", help="The domain name to check (e.g., example.com)")
    args = parser.parse_args()
    domain_to_check = args.domain.lower().strip() # Normalize domain

    print(f"--- Checking Domain: {domain_to_check} ---\n")

    # Get Domain Registrant & Registrar via WHOIS
    domain_whois = get_whois_info(domain_to_check)

    registrant = "Not Found"
    registrar = "Not Found"

    if domain_whois:
        # Try common attributes for registrant name/org
        registrant_name = get_primary_whois_value(domain_whois.get('name') or domain_whois.get('registrant_name'))
        registrant_org = get_primary_whois_value(domain_whois.get('org') or domain_whois.get('registrant_organization'))

        if registrant_name != "Not Found":
            registrant = registrant_name
        elif registrant_org != "Not Found":
             registrant = registrant_org # Use Org if name not found
        else:
             registrant = "Not Found" # Explicitly state if neither found

        # Registrar is usually more consistent
        registrar = get_primary_whois_value(domain_whois.get('registrar'))
        # Fallback
        if registrar == "Not Found":
            url = get_primary_whois_value(domain_whois.get('registrar_url'))
            if url != "Not Found":
                registrar = f"URL: {url}"

    else:
        registrant = "WHOIS Lookup Failed"
        registrar = "WHOIS Lookup Failed"

    print(f"Domain Registrant: {registrant}")
    print(f"Domain Registrar: {registrar}")

    # Get Nameservers (NS Records) via DNS
    nameservers, ns_error_msg = get_dns_records(domain_to_check, 'NS')

    first_nameserver = None
    if ns_error_msg:
        print(f"Error: {ns_error_msg}")
    elif nameservers:
        print(f"Nameservers: {', '.join(nameservers)}")
        first_nameserver = nameservers[0]
    else:
        # Should be covered by error msg, but just in case
        print("No nameservers identified.")


    # Get Registrar of the Nameserver's Owner Domain via WHOIS
    # This helps identify the hosting provider (often the registrar of the NS domain)
    ns_registrar_info = "Not Found" # Initialize

    if first_nameserver:
        ns_owner_domain = get_registrable_domain(first_nameserver)

        if ns_owner_domain:
            ns_domain_whois = get_whois_info(ns_owner_domain)

            if ns_domain_whois:
                ns_registrar_info = get_primary_whois_value(ns_domain_whois.get('registrar'))
                if ns_registrar_info == "Not Found":
                     org = get_primary_whois_value(ns_domain_whois.get('org'))
                     if org != "Not Found":
                          ns_registrar_info = f"Owner Org: {org} (Registrar Not Found)"
            else:
                ns_registrar_info = f"WHOIS Lookup Failed for {ns_owner_domain}"
        else:
            ns_registrar_info = f"Could not determine owner domain from '{first_nameserver}'."
    else:
        ns_registrar_info = "Skipped (No nameserver found)."

    print(f"Inferred DNS Hosting Provider: {ns_registrar_info}")


    print(f"\n--- Check Complete for: {domain_to_check} ---")

if __name__ == "__main__":
    main()