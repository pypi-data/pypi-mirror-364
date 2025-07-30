import pandas as pd, numpy as np, time, math, logging, os
from scipy.optimize import minimize
from caluxPy_fi.Support import Support

class MPT:
    
    def __init__(self, data, yearBasis = None, numberAssets = None, maxWeight = None, riskAversion = None):
        
        desktop = Support.get_folder_path()
        logFormatter = logging.Formatter("%(asctime)s: [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        fileHandler = logging.FileHandler("{0}/{1}.log".format(desktop, 'mpt'), mode = 'w', encoding = 'utf-8')
        fileHandler.setFormatter(logFormatter)
        logger.addHandler(fileHandler)
        
        self.assetPrices = data
        self.numberAssets = numberAssets
        self.maxWeight = maxWeight
        if self.maxWeight is None or self.maxWeight == '': self.maxWeight = 1.0
        self.riskAversion = riskAversion
        if self.riskAversion is None or self.riskAversion == '': self.riskAversion = 1
        self.yearBasis = int(yearBasis) # type: ignore
        if self.yearBasis is None or self.yearBasis == '': self.yearBasis = 365
        self.totalTime = 0
        
        if self.numberAssets is None or self.numberAssets == '': self.numberAssets = len(self.assetPrices)

        self.stocks = list(self.assetPrices.columns.values)

        logger.info('ATTENTION: Calculating yields of assets..')
        self.assetYields, self.processingTime = self.calculate_yields(self.assetPrices) #not ln
        logger.info(f'ATTENTION: Yield of assets calculated.. - Time Elapsed: {self.processingTime} s \n')
        self.totalTime += self.processingTime

        self.averageYields = self.effectiveRate(self.assetYields.mean(),self.yearBasis)
        self.devYields = self.assetYields.std() * math.sqrt(self.yearBasis)
        self.sharpeRatios = self.averageYields / self.devYields

        logger.info('ATTENTION: Creating Correlation Matrix..')
        self.correlationMatrix, self.processingTime = self.calculate_correlation_matrix(self.assetYields, self.numberAssets)
        logger.info(f'ATTENTION: Correlation Matrix Created.. - Time Elapsed: {self.processingTime} s \n')
        self.totalTime += self.processingTime

        #self.covarianceMatrix = self.calculate_varCovar_matrix(self.correlationMatrix, self.devYields, self.numberAssets, self.stocks)
        logger.info('ATTENTION: Creating Covariance Matrix..')
        self.covarianceMatrix, self.processingTime = self.calculate_varCovar_matrix_2(self.correlationMatrix, self.devYields, self.numberAssets) #faster
        logger.info(f'ATTENTION: Covariance Matrix Created.. - Time Elapsed: {self.processingTime} s \n')
        self.totalTime += self.processingTime

        logger.info('ATTENTION: Generating Results..')
        self.optimalPortfolio, self.processingTime = self.optimize_portfolio(self.averageYields, self.covarianceMatrix, self.numberAssets, self.maxWeight, self.stocks)
        
        logger.info(f'ATTENTION: Results Generated.. - Time Elapsed: {self.processingTime} s \n')
        self.totalTime += self.processingTime

        logger.info(f'Process Completed! Total Time: {self.totalTime} s')
        
        logger.removeHandler(fileHandler)
        fileHandler.close()
        
    def calculate_yields(self, stock_prices):
        tiempo_inicio_calculo = time.perf_counter()
        # Calculate the percentage change for all stock columns
        #yields_df = stock_prices.drop('Date', axis=1).pct_change()
        yields_df = stock_prices.pct_change()
        # If you prefer to see the yields as percentages, multiply by 100
        #yields_df *= 100
    
        # Add the 'Date' column back to the DataFrame
        #yields_df.insert(0, 'Date', stock_prices['Date'])
    
        # Drop the first row (it will have NaN values due to the percentage change calculation)
        yields_df = yields_df.dropna()
        tiempo_final_calculo = time.perf_counter()
        processing_time = tiempo_final_calculo - tiempo_inicio_calculo
        return yields_df, processing_time

    def calculate_correlation_matrix(self, stock_yields, num_assets):
        tiempo_inicio_calculo = time.perf_counter()
        # Calculate yields
        #stock_prices.set_index('Date', inplace=True)
    
        # Select the yields of the specified stocks
        selected_yields = stock_yields.iloc[:,:num_assets]
    
        # Calculate the correlation matrix
        correlation_matrix = selected_yields.corr()
        tiempo_final_calculo = time.perf_counter()
        processing_time = tiempo_final_calculo - tiempo_inicio_calculo
        return correlation_matrix, processing_time

    def calculate_covariance_matrix(self,stock_yields, num_assets):
        # Calculate yields
        #stock_prices.set_index('Date', inplace=True)
        #stock_yields = calculate_yields(stock_prices)
    
        # Select the yields of the specified stocks
        selected_yields = stock_yields.iloc[:,:num_assets]
    
        # Calculate the covariance matrix
        covariance_matrix = selected_yields.cov()
    
        return covariance_matrix

    def calculate_varCovar_matrix(self, correlation_matrix, standard_deviations, num_assets, stock_names):
        tiempo_inicio_calculo = time.perf_counter()
        varCovar_matrix = []
        for y in range(num_assets):
            row = []
            for x in range(num_assets):
                row.append(correlation_matrix.iloc[y,x] * standard_deviations[y] * standard_deviations[x])
            varCovar_matrix.append(row)
        varCovar_matrix = pd.DataFrame(varCovar_matrix, columns=stock_names[:num_assets])
        tiempo_final_calculo = time.perf_counter()
        print(f'Processing Time: {tiempo_final_calculo - tiempo_inicio_calculo}')
        return varCovar_matrix

    def calculate_varCovar_matrix_2(self, correlation_matrix, standard_deviations, num_assets):
        tiempo_inicio_calculo = time.perf_counter()
        selected_stocks = standard_deviations[:num_assets]
        diagonal_matrix = np.diag(selected_stocks)
        varCovar_matrix = diagonal_matrix @ correlation_matrix @ diagonal_matrix.T #@ is same as dot for matrix multiplication
        tiempo_final_calculo = time.perf_counter()
        processing_time = tiempo_final_calculo - tiempo_inicio_calculo
        return varCovar_matrix, processing_time

    def effectiveRate(self, yields, basis):
        effectiveYields = (1 + yields) ** basis - 1
        return effectiveYields

    def optimize_portfolio(self, returns, cov_matrix, num_assets, max_weight, stocks):
        tiempo_inicio_calculo = time.perf_counter()
        results = pd.DataFrame()
        #Sequential Least Squares Programming (SLSQP)
        stocks = stocks[:num_assets]
        # Risk-free rate (e.g., 10-year Treasury yield)
        risk_free_rate = 0.03

        # Total number of assets
        returns = returns[:num_assets] 

        # Constraint: The sum of weights must equal max_weight
        constraint = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

        # Constraint: Weights should be between 0 and 1
        bound = (0.0, max_weight)
        bounds = [bound] * num_assets

        # Define the termination tolerance
        tolerance = 1e-10

        # Objective function to maximize (negative of the Sharpe Ratio)
        def neg_sharpe_ratio(weights):
            portfolio_return = np.sum(returns * weights)
            portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            #sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_stddev
            sharpe_ratio = (portfolio_return) / portfolio_stddev
            return -sharpe_ratio
        
        def expected_return(weights):
            return -np.sum(returns * weights)

        def standard_deviation(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        # Complete portfolio optimization function
        #def optimize_portfolio():
        initial_weights = np.ones(num_assets) / num_assets  # Initialize with equal weights

        #region Equal Weightings Region
        dfResult = []
        weights = initial_weights
        portfolio_return = np.sum(returns * weights)
        portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = portfolio_return / portfolio_stddev
        dfResult = pd.DataFrame(weights, index=stocks, columns=['Equal Weighting'])
        dfResult.loc['Return'] = portfolio_return
        dfResult.loc['StDev'] = portfolio_stddev
        dfResult.loc['Sharpe'] = sharpe
        dfResult.loc['Risk Aversion'] = self.riskAversion
        dfResult.loc['Investor Utility'] = portfolio_return - (0.5 * self.riskAversion * portfolio_stddev ** 2) # type: ignore
        dfResult.loc['A01'] = portfolio_return - (0.5 * self.riskAversion * portfolio_stddev ** 2) - (portfolio_return - (0.5* (self.riskAversion + 1) * portfolio_stddev ** 2)) # type: ignore
        results = dfResult
        #endregion

        #region Maximum Sharpe Ratio Region
        dfResult = []
        result = minimize(neg_sharpe_ratio, initial_weights, method='SLSQP', bounds=bounds, constraints=constraint, options={'ftol': tolerance})
        if result.success:
            weights = np.array(result.x)
            portfolio_return = np.sum(returns * weights)
            portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = -result.fun  # Convert back to positive value
            dfResult = pd.DataFrame(weights, index=stocks, columns=['Max Sharpe'])
            dfResult.loc['Return'] = portfolio_return
            dfResult.loc['StDev'] = portfolio_stddev
            dfResult.loc['Sharpe'] = sharpe
            dfResult.loc['Risk Aversion'] = self.riskAversion
            dfResult.loc['Investor Utility'] = portfolio_return - (0.5 * self.riskAversion * portfolio_stddev ** 2) # type: ignore
            dfResult.loc['A01'] = portfolio_return - (0.5 * self.riskAversion * portfolio_stddev ** 2) - (portfolio_return - (0.5* (self.riskAversion + 1) * portfolio_stddev ** 2)) # type: ignore
            results = pd.concat([results, dfResult], axis = 1)
        else:
            print('Unsuccessful!')
        #endregion

        #region Maximum Returns Region
        dfResult = []
        result = minimize(expected_return, initial_weights, method='SLSQP', bounds=bounds, constraints=constraint, options={'ftol': tolerance})
        if result.success:
            weights = np.array(result.x)
            portfolio_return = -result.fun  # Convert back to positive value
            portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = portfolio_return / portfolio_stddev
            dfResult = pd.DataFrame(weights, index=stocks, columns=['Max Return'])
            dfResult.loc['Return'] = portfolio_return
            dfResult.loc['StDev'] = portfolio_stddev
            dfResult.loc['Sharpe'] = sharpe
            dfResult.loc['Risk Aversion'] = self.riskAversion
            dfResult.loc['Investor Utility'] = portfolio_return - (0.5 * self.riskAversion * portfolio_stddev ** 2) # type: ignore
            dfResult.loc['A01'] = portfolio_return - (0.5 * self.riskAversion * portfolio_stddev ** 2) - (portfolio_return - (0.5* (self.riskAversion + 1) * portfolio_stddev ** 2)) # type: ignore
            results = pd.concat([results, dfResult], axis = 1)
        else:
            print('Unsuccessful!')
        #endregion

        #Minimum Risk Region
        #region
        result = minimize(standard_deviation, initial_weights, method='SLSQP', bounds=bounds, constraints=constraint, options={'ftol': tolerance})
        if result.success:
            weights = np.array(result.x)
            portfolio_return = np.sum(returns * weights)
            portfolio_stddev = result.fun  # Convert back to positive value
            sharpe = portfolio_return / portfolio_stddev
            dfResult = pd.DataFrame(weights, index=stocks, columns=['Min Risk'])
            dfResult.loc['Return'] = portfolio_return
            dfResult.loc['StDev'] = portfolio_stddev
            dfResult.loc['Sharpe'] = sharpe
            dfResult.loc['Risk Aversion'] = self.riskAversion
            dfResult.loc['Investor Utility'] = portfolio_return - (0.5 * self.riskAversion * portfolio_stddev ** 2) # type: ignore
            dfResult.loc['A01'] = portfolio_return - (0.5 * self.riskAversion * portfolio_stddev ** 2) - (portfolio_return - (0.5* (self.riskAversion + 1) * portfolio_stddev ** 2)) # type: ignore
            results = pd.concat([results, dfResult], axis = 1)
        else:
            print('Unsuccessful!')
        #endregion
        tiempo_final_calculo = time.perf_counter()
        processing_time = tiempo_final_calculo - tiempo_inicio_calculo
        return results, processing_time

    def showImportedData(self):
        return self.assetPrices

    def showYieldData(self):
        return self.assetYields

    def showCorrelationMatrix(self):
        return self.correlationMatrix

    def showCovarianceMatrix(self):
        return self.covarianceMatrix

    def showOptimalSolution(self):
        return self.optimalPortfolio