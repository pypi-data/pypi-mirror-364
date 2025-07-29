# scripbox/cli.py

import argparse
from scripbox.auth import login
from scripbox.auth import logout
def main():
    parser = argparse.ArgumentParser(prog="scripbox", description="Scripbox CLI")
    subparsers = parser.add_subparsers(dest="command")

    # auth command
    auth_parser = subparsers.add_parser("auth", help="Authentication commands")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command")

    # auth login
    login_parser = auth_subparsers.add_parser("login", help="Login via mobile number")
    login_parser.add_argument("--mobile_number", required=True, help="Your mobile number")

    # auth logout
    logout_parser = auth_subparsers.add_parser("logout", help="logout and clear  token")

    args = parser.parse_args()

    if args.command == "auth" and args.auth_command == "login":
        login(args.mobile_number)
    elif args.auth_command == "logout":
        logout()
    else:
        parser.print_help()

