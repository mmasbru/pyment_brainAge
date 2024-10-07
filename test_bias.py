import os
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.stats as stats
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan


def log_test_result(p_value, test_name, alpha, f):
    if p_value > alpha:
        f.write(f'Non-reject of the {test_name}, with p-val {str(np.round(p_value, 2))} \n')
    else:
        f.write(f'Non-reject of the {test_name}, with p-val {str(np.round(p_value, 2))} \n')

def main(df, wd, alpha, stds):
    """Checks for the adjustment of HCs to the expected age 1:1 line with 0 intercept.
    INPUTS: 
        - df: Dataframe path. Must be a csv file, with at least two columns, named 'Age' with biological age, and 
        'Predicted' age output from preprocess. Only healthy controls.
        - wd: working output directory. 
        - alpha: significance. Default: 0.05.
        - stds: number of standard deviations from which a point is considered an outlier. Default: 2.
    OUTPUTS: 
        - corr: Pearson correlation between biological and predicted ages.
        - mae: Mean Absolute Error. The authors of the original paper report +-3y mae."""
    
    df = pd.read_csv(df, header=0)
    
    if 'Age' not in df.columns or 'Predicted' not in df.columns:
        raise ValueError("Dataframe must contain 'Age' and 'Predicted' columns.")

    log = os.path.join(wd, "results.txt")
    f = open(log, 'a')

    #Test correlation.
    corr = np.corrcoef(df['Age'], df['Predicted'])[0,1]
    f.write(f'Correlation: {str(np.round(corr,2))} \n')
    
    # Mean absolute error.
    mae= np.mean(abs(df['Age']-df['Predicted']))
    f.write(f'MAE: {str(np.round(mae,2))} \n')

    #Test 1:1 with 0 intercept.
    test_name = 'linearity Test (1:1 slope, 0 Intercept)'
    X = df['Age']
    y = df['Predicted'] 
    X = sm.add_constant(X)
    model = sm.OLS(y, X.astype(float)).fit()
    slope = model.params.iloc[1] 
    std_err = model.bse.iloc[1]  
    t_stat = (slope - 1) / std_err
    df_model = model.df_resid  
    p_value = 2 * (1 - stats.t.cdf(np.abs(t_stat), df_model)) 
    log_test_result(p_value, test_name, alpha, f)


    # Test homeoscedasticity. 
    test_name = 'homoscedastic test'
    residuals = df['Age'] -  df['Predicted']
    _, _, _, f_pvalue = het_breuschpagan(residuals, X)
    log_test_result(f_pvalue, test_name, alpha, f)


    #Plot. 
    large_predicted = df['Predicted'][abs(residuals) > np.mean(residuals)+stds*np.std(residuals)]
    large_age =df['Age'][abs(residuals) > np.mean(residuals)+stds*np.std(residuals)]
    x=np.arange(6,20)
    sns.lmplot(x='Age', y='Predicted', data=df, ci=95)
    plt.plot(x,x,'k--', linewidth=3)
    plt.title('Pearson:{}, MAE:{}y, '.format(str(np.round(corr,2)), str(np.round(mae,2))))
    plt.scatter(large_age, large_predicted, c = 'red',marker='*', s = 30)
    plt.savefig(os.path.join(wd,'results.png'))

    #Return a decision on the need for fine-tuning.
    if p_value > alpha and f_pvalue > alpha: 
        f.write(f'Fine-tuning not required. Check results.png to ensure. \n')        
    else: 
        f.write(f'Fine-tuning required. \n')

    f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Checks for the adjustment of HCs to the expected age 1:1 line with 0 intercept.')
    
    parser.add_argument('-df', '--df', help="""Dataframe path. Must be a .csv file, with at least two columns, named 'Age' with biological age, and 
        'Predicted' age output from preprocess. Only healthy controls should be included.""", required=True)
    parser.add_argument('-o', '--o', help='Working directory.', required=True)
    parser.add_argument('-a', '--a', help='Significance level.', default=0.05)
    parser.add_argument('-s', '--s', help='# of standard deviations to detect outliers.', default=2)
    args = parser.parse_args()

    # Define cropping bounds
    main(args.df, args.o, args.a, args.s)