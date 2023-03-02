# MTTCalc Website (CS50X Final Project)
#### Video Demo: https://youtu.be/7w8wQPUPJEo

## Introduction

Cells are units of life. Any cell has three phases in its life span: growth, plato and death phases.
In growth phase cells grow in size, In plato phase size remains constant and in death phase cells will die.

MTT assay is one of the technics used by scientists in labratories for estimating cell viability. This technic has many usages, for example measuring the effect of drugs on viability of cancerous cells. In this way the drugs that reduce cell viability (force cells to enter into the death phase) can be listed as potential cancer treatment. For additional information, [read this article](https://www.sigmaaldrich.com/US/en/technical-documents/protocol/cell-culture-and-cell-culture-analysis/cell-counting-and-health-analysis/cell-proliferation-kit-i-mtt).

The raw data of MTT assay must be processed. MTTCalc is a tool that automate this processing stage. The input of the app is the output of ELISA reader equipment (absorbance of each well in 550-600 nm) and the output is the cell viability of each well (% of control).

After processing raw data, the viablities data can be used for statistical analysis. One-Way ANOVA is the one of the methods that can be used to check if any significant diffrences exists between the mean of groups. If any significance diffrence exists, tukey test can be used  to find means that are significantly different from each other. In one-way ANOVA it is assumed that the data is heterogenous and normaly distributed.

## Components

### app.py
This is the main file that contains the views:
1. index: Asociated to "/" route, return index.html template. Users can enter the number of groups and number of repeats in this page.
2. mttcalc: Associated to "/mttcalc" route. For get requests, return mttcalc.html template. In this page, the fields must be filled with absorbance values for groups and their blanks. For logged in users, the name of test should be entered. For post requests, absorbances read from post body with get_absorbances function and save to a file. The file path feed to the calc_mtt function to generate output files. If the user was logged in, a record will be saved in the database. Finally, user will be redirected to the download page.
3. download: Associated to "/download" route. If file_name parameter doesn't exist in the download route, the download.html will be rendered. In the other hand, if file_name exists and has a value, the file will be send to the user.
4. register, login, and logout: Associated to "/register", "/login", and "/logout" routes respectivly. With this views, user can register, login and logout, respectively. session is used for saving user_id for logged in users.
5. history: This view is responsible fetching user saved records from database and rendering history.html to the user.
### helpers.py
The get_absorbances, calc_mtt, and login_required decorator have been defined in this file.
### anova.py
Inside this module, Anova class is defined for checking one-way ANOVA assumptions (check_assumptions), perform one-way ANOVA itself (test) and finaly perform tukey test (perform_tukey). Each of these functions saves its result inside the out.dat file. The bioinfokit, statsmodels and scipy modules used for performing statistical analysis.
### mttcalc.db
This is the sqlite3 database file and contains users and history tables.
### static folder
Contains image and css files.
### templates folder
Contains all the templates described in the app.py component.
### requirements.txt
Listed all the modules that must be installed before running flask run.
Required modules can be installed using pip3 comman:

`pip3 install -r requirements.txt`

## Usage
Inside the project directory, type this command:
`flask run`
