from inventory_api import create_app

app = create_app()

if __name__ == "__main__":
    # debug mode gives auto reload and readable tracebacks while developing
    app.run(debug=True)
