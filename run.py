from app import create_app

app, celery = create_app()

if __name__ == "__main__":
    # Run the Flask development server
    app.run(debug=True, host='127.0.0.1', port=5000)
