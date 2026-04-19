import requests


def run_basic_recon(domain):
    print(f"Running recon on {domain}...")

    results = {
        "domain": domain,
        "dns": "placeholder",
        "email_provider": "unknown",
        "tech_stack": []
    }

    return results


if __name__ == "__main__":
    domain = input("Enter domain: ")
    print(run_basic_recon(domain))
