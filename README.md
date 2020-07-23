README
================

This code takes a dataset from IPUMS ATUS and sex variable to output a balance table (in LaTeX format) of hours spent on various daily activities for males/females with children 5 years old or younger and males/females without children.
Activities in the table include childcare, eating and drinking, housework, sleeping, television, and working, as defined by IPUMS.

The [ATUS](https://www.atusdata.org/atus/) is an ongoing time diary study funded by the U.S. Bureau of Labor Statistics (BLS) and fielded by the U.S. Census Bureau. 

To run the sample analysis, use the command below
```
python BalanceAnalysis.py -s 2 -i 'atus_00010.csv' -o 'balance-female.tex'
```
More generally,
```
python BalanceAnalysis.py -s <sex (1:male, 2:female)> -i <inputfile.csv> -o <output.tex>
```

**Contents:**

1.  README.md - the document you're currently reading!
2.  ATUSsample.py - code that creates the balance table for the specified sex and inputted data file
3.  BalanceAnalysis.py - code that parses the command-line options
4.  atus_00010.csv - sample data extract downloaded from IPUMS that includes survey years 2015 - 2018
5.  balance-female.tex - LaTeX balance table for time spent on activities comparing females with and without children

The input file must be a .csv, with each row as a recorded activity code for each unique household case ID.
The columns include: 
1.  YEAR	
2.  CASEID	
3.  PERNUM	
4.  LINENO	
5.  WT06
6.  AGE	
7.  SEX	
8.  MARST	
9.  EDUCYRS	
10. KIDUND18	
11. KIDUND1	
12. KID1TO2	
13. KID3TO5	
14. ACTIVITY	
15. DURATION

