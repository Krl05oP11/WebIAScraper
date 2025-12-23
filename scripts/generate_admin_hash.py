#!/usr/bin/env python3
"""
Generate admin password hash for migration
Usage: python3 scripts/generate_admin_hash.py [password]

This script generates a secure password hash using werkzeug's PBKDF2-HMAC-SHA256
algorithm, which is the same one used by Flask for password hashing.

The hash can be used in SQL migrations to create the initial admin user.
"""
import sys
from werkzeug.security import generate_password_hash


def main():
    """Generate password hash and print SQL INSERT statement"""
    # Get password from command line or use default
    password = sys.argv[1] if len(sys.argv) > 1 else 'changeme'

    # Generate hash using werkzeug (same as Flask uses)
    password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    # Print results
    print("\n" + "=" * 70)
    print("PASSWORD HASH GENERATOR FOR WEBIASCRAP")
    print("=" * 70)
    print(f"\nPassword: {password}")
    print(f"Hash: {password_hash}")
    print("\n" + "-" * 70)
    print("SQL INSERT statement for migration:")
    print("-" * 70)
    print(f"""
INSERT INTO users (username, password_hash, created_at)
VALUES (
    'admin',
    '{password_hash}',
    CURRENT_TIMESTAMP
)
ON CONFLICT (username) DO NOTHING;
""")
    print("=" * 70)
    print("\nCopy the hash above and paste it into your migration SQL file.")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
