def main():
    if len(sys.argv) < 2:
        print("Usage: appligen <nom_de_l_app>")
        sys.exit(1)
    app_name = sys.argv[1]
    create_django_app(app_name)

if __name__ == "__main__":
    main()
