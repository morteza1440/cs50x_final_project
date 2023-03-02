# MTTCalc
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
1. index: asociated to "/" route, return index.html template. Users can enter the number of groups and number of repeats in this page.
2. mttcalc: associated to "/mttcalc" route. For get requests, return mttcalc.html template. In this page, the fields must be filled with absorbance values for groups and their blanks. For logged in users, the name of test should be entered. For post requests, absorbances read from post body with get_absorbances function and feed to the 
3. Plotting: This app can plot box plot and bar chart of the viabilities data. draw_barchart and draw_boxplot functions defined for these functionalities. the boxplot and swarmplot functions from seaborn module, and bar and errorbar functions from matplotlib module used for plotting the charts. The user should use --boxplot and --barchart switches for enabling these functionality of the app. set_ext function defined to set the extention of the chart files to png.
4. One-Way ANOVA: For checking one-way ANOVA assumptions, performing one-way ANOVA and finaly tukey test, Anova class is defined inside anova module.
### project_test.py
Inside this file five functions defined to test set_ext, draw_barchart, draw_boxplot, calc_viabilities, and get_new_col_names.
### anova.py
Inside this module, Anova class is defined for checking one-way ANOVA assumptions (check_assumptions), perform one-way ANOVA itself (test) and finaly perform tukey test (perform_tukey). Each of these functions saves its result inside the out.dat file. The bioinfokit, statsmodels and scipy modules used for performing statistical analysis.
### requirements.txt
Listed all the modules that must be installed before running MTTCalc app.
Required modules can be installed using pip3 comman:

`pip3 install -r requirements.txt`

## Usage
```
$ python project.py --help
usage: project.py [-h] [--barchart BARCHART_FILE_NAME] [-t TITLE] [-x XLABEL] [-y YLABEL] [-a ANGLE]
         [--boxplot BOXPLOT_FILE_NAME] [--check-assumptions] [--multiple-comparison] [-o OUT_DIR] path

Statistical analysis of MTT assay data using one-way ANOVA.

positional arguments:
  path                  path to the csv file containing absorbance reads

options:
  -h, --help            show this help message and exit
  --barchart BARCHART_FILE_NAME
                        draw bar chart of data.
  -t TITLE, --title TITLE
                        title of bar chart.
  -x XLABEL, --xlabel XLABEL
                        label of x axes for bar chart.
  -y YLABEL, --ylabel YLABEL
                        label of y axes for bar chart.
  -a ANGLE, --angle ANGLE
                        x ticks rotation in bar chart.
  --boxplot BOXPLOT_FILE_NAME
                        draw box plot of data.
  --check-assumptions   check normal distribution and homogeneity.
  --multiple-comparison
                        tukey pairwise multiple comparison.
  -o OUT_DIR, --out-dir OUT_DIR
                        output directory, default is current directory.
  ```
