# UniMeet
To install the requirements for this app go into the project directory and use the following commands:

            cd backend

            pip install -r requirements.txt


# Running the UniMeet App
To run the UniMeet App, split the terminal, on the first terminal:

            cd backend

            python manage.py runserver

On the second terminal:

            cd frontend

            npm run dev

# Unit Test Instructions
We use Django's built in test runner combined with Coverage.py to ensure our API is secrure and stable,
Run the following commands in the project directory:

Make sure you have coverage installed in your environment using the following line:

            pip install coverage

Make sure you are in UniMeet\backend using:

            cd backend

To run the tests use:

            coverage run manage.py test api

To show the test report use:

            coverage report