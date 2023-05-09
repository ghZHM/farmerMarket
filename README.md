# farmerMarket
Team software project at the University of Sheffield

# Overview

The following guideline would help you install the application's requirements and set up database.

# **Get Started**

**0. Install MySQL**

https://dev.mysql.com/downloads/installer/

**1. Enter the correct file path in command line, which should be like**
```
project
  -admin_page
  -farmers_page
  -home
  ...
  requirements.txt
 ```
 **2. Activate the virtual environment**

 Use a virtual environment to manage the dependencies for your project, both in development and in production.
 
 if you are using anaconda, you can use the following command to create and activate a new virtual environment in windows command line.
 ```
  conda create -n "nameOfEnvironment" python = 3.7
  # create a virtual environment called nameOfEnvironment
  
  conda activate "nameOfEnvironment"
  # activate the environment just created
 ```
 
 **Note: We recommend using the latest version of Python. Flask supports Python 3.7 and newer.**
 
  **3. Install the dependency in virtual environment**
  
   ```
  pip install -r requirements.txt
   ```
   
   **4. Initialize the database**
   
   ```
   type in the queries in ___.txt in command line to create a new database
   ```
   
   **5. Setup database in models.py**
   
   set the correct user_name, password and schema name in models.py
 
 
