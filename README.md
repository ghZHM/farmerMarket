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
 
 
 **2. Create and activate the virtual environment**

 Use a virtual environment to manage the dependencies for your project, both in development and in production.
 
 If you are using anaconda, you can use the following command to create and activate a new virtual environment in windows command line.
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
   
   Type in the queries in [create_table.txt](https://github.com/ghZHM/farmerMarket/blob/main/create_table.txt) in command line after activate MySQL to create a new schema.
   
   
   **5. Setup database in models.py**
   
   Set the correct ***user_name, password and schema name*** in [models.py](https://github.com/ghZHM/farmerMarket/blob/main/models.py#L6)
 
 
   **6. Run**
   
   To run the application, you just need to run the following command in virtual environment.
   ```
   flask --app farmersMarket run
   ```
   And you will reach the login page by type in the following url in browers.
   ```
   http://127.0.0.1:5000/home/login
   ```
