# tup-assist


**GITBASH FOR GITHUB**

1. git pull
2. git add .
3. git commit -m "Add Files"
4. git push


**PROJECT**

When there is changes in Model.py
- go to TupAssistApp/migratiuons Folder
-delete 0001_initial.py

-go to phpmyadmin
-drop all tables in database

-proceed in terminal
-- python manage.py makemirations
-- python manage.py runserver
-- python manage.py loaddata data.json
-- python manage.py runserver

-Next is Sign Up
-Then login






<!-- Data Tables NodeJs PACKAGES -->
SOURCE: https://datatables.net/manual/installation#Initialising-DataTables
npm install datatables.net    # Core library
npm install datatables.net-dt # Styling

npm install -g bower

Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser

bower install --save datatables.net
bower install --save datatables.net-dt