
To run the project on your local network ;

You can automatically install the necessary libraries from the requirements.txt with the help of pip.
```
pip install -r requirements.txt
```

Migrate the database by calling python in the project folder;
```
python manage.py makemigrations
python manage.py migrate
```

Create an administrator to be able to login to the system as admin;
```
python manage.py createsuperuser
```
Your system will be complete after these processes.
