# FarmerMarket
Team software project at the University of Sheffield.

A web project that allows farmers to sell their goods and has data analysis capabilities.

# Overview

The following guideline would help you install the application's requirements and set up database.

# **Get Started**

**0. Install MySQL**

https://dev.mysql.com/downloads/installer/

**1. Initialize the database**
   
Type in the queries in [***create_table.txt***](https://github.com/ghZHM/farmerMarket/blob/main/create_table.txt) in command line after activate MySQL to create a new schema.
   
   
 **2. Create and activate the virtual environment**

 Use a virtual environment to manage the dependencies for your project, both in development and in production.
 
 If you are using anaconda, you can use the following command to create and activate a new virtual environment in windows command line.
 ```
  conda create -n "nameOfEnvironment" python = 3.7
  # create a virtual environment called nameOfEnvironment
  # and the python version is set as 3.7
  
  conda activate "nameOfEnvironment"
  # activate the environment just created
 ```
 
 Note: We recommend using the latest version of Python. 
 **Flask supports Python 3.7 and newer.**
 
 
**3. Go to the correct file path "/project" in virtual environment command line, which should be like**
```
project
  -admin_page
  -farmers_page
  -home
  ...
  farmerMarket.py
  requirements.txt
 ```


  **4. Install the dependency in virtual environment**
  
   ```
  pip install -r requirements.txt
  # run this command under 'project' file.
   ```
   
  
**5. Setup database in models.py**
   
   Set the correct ***user_name, password and schema name*** in [models.py](https://github.com/ghZHM/farmerMarket/blob/main/models.py#L6)
 
**6. PayPal key setup**

The key of PayPal was removed, you can add back [here](https://github.com/ghZHM/farmerMarket/blob/main/purchase_page/purchasePage.py#L11) 


**7. Run**
   
   To run the application, you just need to run the following command in virtual environment.
   ```
   flask --app farmersMarket run
   ```
   And you will reach the login page by type in the following url in browers.
   ```
   http://127.0.0.1:5000/home/login
   ```
