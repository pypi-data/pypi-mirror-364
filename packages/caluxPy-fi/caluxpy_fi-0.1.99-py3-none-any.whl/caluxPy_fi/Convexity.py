#from pathlib import Path
#import sys, os
#sys.path.append(str(Path(__file__).resolve().parent.parent))
import numpy as np, pandas as pd, matplotlib.pyplot as plt, logging
from caluxPy_fi.FixedIncome import FixedIncome
from caluxPy_fi.Support import Support

class Convexity(FixedIncome):

    def __init__(self, settlement_date, issuance_date, maturity_date, coupon, ytm, face_value, issuer, methodology, periodicity, repayment_type, coupon_type, 
                 forward_date, amortization_start_date, amortization_periods, amortization_periodicity, amortizable_percentage, date_format = '', multiple = False, bps = 100, lang = 'eng'):
        super().__init__(settlement_date, issuance_date, maturity_date, coupon, ytm, face_value, issuer, methodology, periodicity, repayment_type, coupon_type, 
                         forward_date, amortization_start_date, amortization_periods, amortization_periodicity, amortizable_percentage, date_format = '', multiple = False, lang = 'eng')

        desktop = Support.get_folder_path()
        logFormatter = logging.Formatter("%(asctime)s: [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)
        fileHandler = logging.FileHandler("{0}/{1}.log".format(desktop, 'convex'), mode = 'w', encoding = 'utf-8')
        fileHandler.setFormatter(logFormatter)
        self._logger.addHandler(fileHandler)

        self._lang = lang
        self.tipo_valoracion = 'convexity'
        self.bps = bps

        self.max_gain, self.max_loss, self.avg_gain, self.avg_loss, self.std_gain, self.std_loss = 0, 0, 0, 0, 0, 0
        self.chart_data = {}
        
        try:
            self.convexityValuationType(self.current_coupon, self._nper, self.w_coupon, self._discrepancy, self.coupon_type, self.maturity_date, self.expected_maturity, self.coupon_days, 
                                        self.ytm, self.periodicity, self.coupon_flow, self.repayment_type, self.issuer, self.notional_value, self.gained_coupon, bps)
            self._logger.info('SUCCESS: Calculation finished..')
        except Exception as e:
            self._logger.exception(e)

        self._logger.removeHandler(fileHandler)
        fileHandler.close()

    def convexityValuationType(self, current_coupon, nper, w_coupon, discrepancy, coupon_type, maturity_date, expected_maturity, coupon_days, ytm, periodicity, 
                                 coupon_flow, repayment_type, issuer, notional_value, gained_coupon, bps):
        
        listPBS, listDirtyPrice, listConvexity, listDuration = [], [], [], []

        y = -int(bps)
        while y <= int(bps):
            ytm2 = ytm + (y / 10000)
            resValuation = self.presentValue(current_coupon = current_coupon, 
                                             nper = nper, 
                                             w_coupon = w_coupon, 
                                             discrepancy = discrepancy, 
                                             coupon_type = coupon_type, 
                                             maturity_date = maturity_date, 
                                             expected_maturity = expected_maturity, 
                                             coupon_days = coupon_days, 
                                             ytm = ytm2, 
                                             periodicity = periodicity, 
                                             coupon_flow = coupon_flow, 
                                             repayment_type = repayment_type, 
                                             issuer = issuer, 
                                             notional_value = notional_value, 
                                             gained_coupon = gained_coupon)
            # Append results to lists
            listPBS.append(y) # List of basis points
            listDirtyPrice.append(resValuation[1] * 100) # List of dirty prices
            listDuration.append(resValuation[4]) # if y != 0 else 0)
            listConvexity.append(resValuation[7]) # if y != 0 else 0)
            y += 1 # Marginal increase
        
        # Conversion of lists into numpy arrays for ease of use
        listPBS = np.array(listPBS)
        listDirtyPrice = np.array(listDirtyPrice)
        listDuration = np.array(listDuration)
        listConvexity = np.array(listConvexity)
        
        # Creation of DataFrame
        self.df_convex = pd.DataFrame({
            'pbs': listPBS, 
            'Price': listDirtyPrice,
            'Duration': listDuration,
            'Convexity': listConvexity
        })
        
        # Process negative PBS values
        negatives = self.df_convex[self.df_convex['pbs'] <= 0].copy() # Copy the DataFrame for ease of use
        negatives.sort_values(by = 'pbs', ascending = False, inplace = True) # Sort descending
        negatives['dv01'] = negatives['Price'].diff().fillna(0) * 10000 # Calculate the difference and fill first with 0
        negatives['gains/losses'] = negatives['dv01'].cumsum() # Perform Cummulative Sum
        #negatives[['Duration', 'Convexity']] = negatives[['Duration', 'Convexity']].cumsum()
        negatives.sort_values(by = 'pbs', ascending = True, inplace = True) # Sort Ascending
        first_neg = negatives.iloc[-2]['dv01'] # Get the first negative (the one after 0)
        
        # Treatment of the positives in the df
        positives = self.df_convex[self.df_convex['pbs'] >= 0].copy() # Copy the DataFrame for ease of use
        positives.sort_values(by = 'pbs', ascending = True, inplace = True) # Sort Ascending
        positives['dv01'] = positives['Price'].diff().fillna(0) * -10000 # Calculate the difference and fill first with 0
        positives['gains/losses'] = positives['dv01'].cumsum() # Perform Cummulative Sum
        #positives[['Duration', 'Convexity']] = positives[['Duration', 'Convexity']].cumsum()
        first_pos = positives.iloc[1]['dv01'] # Get the first positive (the one after 0)
        
        # Calculate average dv01
        self.avg_dv01 = (first_neg + first_pos) / 2 # Get an averaged dv01 with the first occurrence of a marginal increase, because it can go both ways
        
        #Concatenating the dfs to form the complete one
        final = pd.concat([negatives, positives[1:]]) # Concatenate both results of gains and losses
        final.reset_index(drop = True, inplace = True) # Reset indexes so it can be incorporated into the original DataFrame
        self.df_convex[['dv01', 'gains/losses', 'Duration', 'Convexity']] = final[['dv01', 'gains/losses', 'Duration', 'Convexity']] # Incorporate gains and losses into the original DataFrame
        
        #Proceed over a copy so the original is not affected
        final_copy = final.copy()
        final_copy = final_copy[final_copy['pbs'] != 0] # Exclude 0 bps row, so no contamination of calculations
        final_copy['Negative'] = final_copy['pbs'] < 0 # Add a boolean column where True is if value of pbs is negative
        max_values_by_category = final_copy.groupby('Negative')['dv01'].max() # Group the data by the boolean column, having 2 groups (True and False) then getting max values of box, resulting into a list
        avg_values_by_category = final_copy.groupby('Negative')['dv01'].mean() # Get a list with the average means of both groups
        std_values_by_category = final_copy.groupby('Negative')['dv01'].std() # Get a list with the standard deviations of both groups

        # Assigning values to the usable variables
        self.max_gain = max_values_by_category[True] 
        self.max_loss = max_values_by_category[False]
        self.avg_gain = avg_values_by_category[True]
        self.avg_loss = avg_values_by_category[False]
        self.std_gain = std_values_by_category[True]
        self.std_loss = std_values_by_category[False]
       
    def showGraph(self):
        plt.figure(figsize=(10,6))
        plt.plot(self.chart_data['x_pbs'], self.chart_data['y1_dur'])
        plt.plot(self.chart_data['x_pbs'], self.chart_data['y2_cvx'], linestyle='--')
        title = 'Gráfico de Duración-Convexidad' if self._lang == 'esp' else 'Duration-Convexity Graph' if self._lang == 'eng' else ''
        basis_points = 'Puntos Básicos' if self._lang == 'esp' else 'Basis Points' if self._lang == 'eng' else ''
        values = 'Valores Duración y Convexidad' if self._lang == 'esp' else 'Duration and Convexity Values' if self._lang == 'eng' else ''
        plt.ylabel(values)
        plt.xlabel(basis_points)
        plt.title(title)
        
        return plt.show()

    def saveGraph(self, filename):
        plt.savefig(filename, bbox_inches = 'tight', dpi = 300)
        plt.close()
    
    def getResults(self):
        results = {'max_gain': self.max_gain,
                   'max_loss': self.max_loss, 
                   'avg_gain': self.avg_gain, 
                   'avg_loss': self.avg_loss, 
                   'sd_gain': self.std_gain, 
                   'sd_loss': self.std_loss,
                   'dv01': self.avg_dv01,
                   'df': self.df_convex,
                   #'chart_data': self.chart_data
                   }
        return results

    def __str__(self):
        return f'\
{'Max Gain' if self._lang == 'eng' else 'Max Ganancia'}: {self.max_gain} \n \
{'Max Loss' if self._lang == 'eng' else 'Max Perdida'}: {self.max_loss} \n \
{'Average Gain' if self._lang == 'eng' else 'Ganancia Promedio'}: {self.avg_gain} \n \
{'Average Loss' if self._lang == 'eng' else 'Perdida Promedio'}: {self.avg_loss} \n \
{'Deviations in Gains' if self._lang == 'eng' else 'Desviacion Ganancias'}: {self.std_gain} \n \
{'Deviations in Losses' if self._lang == 'eng' else 'Desviacion Perdidas'}: {self.std_loss}'



