import os

def main():
    if os.environ.get("SEED_DEV_MENU") == "1":
        try:
            import seed_cli_legacy_menu
            return seed_cli_legacy_menu.main()
        except Exception as error:
            print(f"Could not open legacy developer menu: {error}")
    from seed_companion_shell_v62 import companion_loop
    companion_loop()

if __name__ == "__main__":
    main()
