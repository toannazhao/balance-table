## The following code constructs a balance table (in LaTeX format) that replicates the BALANCETABLE package in STATA 14.
## I use data from the IPUMS Time Use (ATUS) to examine the effects of being a parent on various daily activities.
## This is part of a larger project on the effects of family formation on crime desistance (Massenkoff and Rose).


#import relevant packages and data
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

df = pd.read_csv('../Berkeley/Maxim/Fa19/ipums-time-use/atus_00010.csv')

#filter for specified sex: 1 (male), 2 (female)
df = df.loc[df['SEX'] == 2]

# distinguish types of people
childless_index = np.array(df['KIDUND18'] == 0)
child_index = np.array(df['KIDUND1'] > 0) | (df['KID1TO2'] > 0) | (df['KID3TO5'] > 0)
df.loc[childless_index, 'CHILD'] = 0
df.loc[child_index, 'CHILD'] = 1 #have a child <=5 y/o
#those with children >5 y/o will not have 'child' dummy variable

# marital status dummy
df.loc[df['MARST'] > 2, 'MAR'] = 0
df.loc[df['MARST'] <= 2, 'MAR'] = 1

# code activity descriptions
df['ACTIVITY'] = df['ACTIVITY'].astype('str')
dict_five = {'101': 'Sleeping', '201': 'Housework', '5': 'Working',
'301': 'Childcare', '302': 'Childcare', '303': 'Childcare'} #matching first digits of activity codes
len_five = (df['ACTIVITY'].str.len() == 5)
for i in dict_five.keys():
    act_start = df['ACTIVITY'].str.startswith(i)
    df.loc[len_five & act_start, 'ACTIVITY_LONG'] = dict_five[i] #descriptors of the relevant codes in 'ACTIVITY_LONG'
len_six = (df['ACTIVITY'].str.len() == 6)
df.loc[(df['ACTIVITY'] == '120303') | (df['ACTIVITY'] == '120304'), 'ACTIVITY_LONG'] = 'Television'
df.loc[len_six & (df['ACTIVITY'].str.startswith('11')), 'ACTIVITY_LONG'] = 'Eating and drinking'

# for each caseid (showing person weight, age, child, marital status), get the total duration for each activity
dat = df.groupby(['CASEID', 'WT06', 'CHILD', 'ACTIVITY_LONG', 'AGE', 'MAR'])['DURATION'].sum().unstack('ACTIVITY_LONG').stack('ACTIVITY_LONG', dropna=False)
dat = dat.reset_index(name = 'DURATION')
dat['DURATION'].fillna(value = 0, inplace = True) #fill in 0 duration for cases without certain activities
dat['DURATION'] = dat['DURATION']/60 #change duration from minutes to hours
#regroup
dat = dat.groupby(['CASEID', 'WT06', 'CHILD', 'AGE', 'MAR', 'ACTIVITY_LONG'])['DURATION'].sum()
dat = dat.reset_index(name = 'DURATION')
# print(dat)

#sample size
n_childless = dat.loc[dat['CHILD'] == 0, 'CASEID'].nunique()
n_child = dat.loc[dat['CHILD'] == 1, 'CASEID'].nunique()

## obtain regression coefficients for each activity and group

def star_p(p, coeff):
    """ This is a function for adding pvalue stars next to significant coefficients.
    Inputs: p value, coefficient
    Returns: coefficient, with asterisks if it is significant"""
    if p < .01:
        coeff = coeff + "***"
    elif p < .05:
        coeff = coeff + "**"
    elif p < .1:
        coeff = coeff + "*"
    else:
        pass
    return coeff

mat = np.empty((2,))
children = []
controls = []
for i in dat['ACTIVITY_LONG'].unique():
    act = dat[dat['ACTIVITY_LONG'] == i] #filter data to that activity only
    y = np.mat(act['DURATION']).T
    x = sm.add_constant(np.array(act['CHILD']).T) #'child' is an indicator

    #weighted least squares with person weight and heteroskedasticity robust covariance, without controls
    reg = sm.WLS(y, x, weights = act['WT06']).fit(cov_type = 'HC3')
    results = np.array(["{0:.3f}".format(p) for p in reg.params], dtype = object) #array of coefficients
    results[1] = star_p(reg.pvalues[1], results[1])
    mat = np.vstack((mat, results, ["{0:.3f}".format(b) for b in reg.HC3_se])) #array of standard errors

    mean_child = reg.params[0] + reg.params[1] #mean hours with kids (constant + difference)
    se_child = np.sqrt(reg.HC3_se[1]**2 - reg.HC3_se[0]**2) #standard error calculation
    children.extend(("{0:.3f}".format(mean_child), "{0:.3f}".format(se_child))) #mean, SE of 'child' coeff

    #weighted least squares with person weight and heteroskedasticity robust covariance, with controls
    reg_2 = smf.wls('DURATION ~ CHILD + AGE + AGE^2 + AGE^3 + C(MAR)', data=act, weights = act['WT06']).fit(cov_type = 'HC3')
    results_2 = list(("{0:.3f}".format(reg_2.params['CHILD']), "{0:.3f}".format(reg_2.HC3_se['CHILD']))) #mean, SE of 'child' coeff
    results_2[0] = star_p(reg_2.pvalues['CHILD'], results_2[0])

    controls.extend(results_2)


# construct balance table
bal = pd.DataFrame(mat).drop(labels=0, axis=0)
bal.insert(loc = 1, column = 'Mean with kids', value = children)
bal.insert(loc = 3, column = 'Difference with controls', value = controls)
bal[1::2] = '(' + bal[1::2].astype(str) + ')' #format SE with parentheses
map_act = dict(zip([i for i in range(0,13) if i%2==1], dat['ACTIVITY_LONG'].unique())) #label activity of odd rows (means)
map_se = {k:'' for k in [k for k in range(0,13) if k%2==0]}
bal.rename(index=map_act, inplace=True)
bal.rename(index = map_se, inplace = True)
bal.rename(columns = {0: 'Mean without kids', 1: 'Difference (hours)'}, inplace=True)
bal.loc[13] = [n_childless, n_child, '-', '-'] #last row showing sample size
bal.rename(index = {13: 'N'}, inplace = True)
bal.to_latex('balance-female.tex')
print(bal)
