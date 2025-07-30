import re
import math
from scipy.optimize import minimize
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import logging
import os
import pathlib

class Support ():

    @staticmethod
    def setup_logger():
        desktop = Support.get_folder_path()
        _logFormatter = logging.Formatter("%(asctime)s: [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        _fileHandler = logging.FileHandler(f"{desktop}/support.log", mode='w', encoding='utf-8')
        _fileHandler.setFormatter(_logFormatter)
        logger.addHandler(_fileHandler)
        return logger, _fileHandler
    
    @staticmethod
    def rateConversion(rate):
        if type(rate) == str and re.search('%',rate)!=None:
            return float(rate.replace('%',''))/100
        elif float(rate) > 1:
            return float(rate) / 100
        else:
            return float(rate)
    
    @staticmethod
    def periodicityConversion(per, mode):
        modes = {
            'normal': {
                'anual': 1, 
                'vencimiento': 1,
                'semestral': 2,
                'cuatrimestral': 3,
                'trimestral': 4, 
                'bimensual': 6,
                'mensual': 12
                },
            'amortization': {
                'anual': 12, 
                'vencimiento': 12, 
                'semestral': 6,
                'cuatrimestral': 4, 
                'trimestral': 3, 
                'bimensual': 2,
                'mensual': 1
                }
        }
        return modes[mode].get(per, 1)
    
    @staticmethod
    def monthSelection(mes):
        months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return months[mes-1] if 1 <= mes <= 12 else None
    
    @staticmethod
    def years(issuance_date, maturity_date):

        '''def is_leap_year(year):
            """Check if a year is a leap year."""
            return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        
        def days_in_year(year):
            """Return the number of days in a year, considering leap years."""
            return 366 if is_leap_year(year) else 365
        
        # Calculate the initial year difference
        year_difference = maturity_date.year - issuance_date.year

        # Adjust the start date by the year difference to see if we've gone too far
        adjusted_date = issuance_date.replace(year=issuance_date.year + year_difference)
        
        # If we've gone too far, decrease the year difference
        if adjusted_date > maturity_date:
            year_difference -= 1
            adjusted_date = issuance_date.replace(year=issuance_date.year + year_difference)
        
        # Calculate the remaining days after the last full year
        remaining_days = (maturity_date - adjusted_date).days
        
        # Calculate the fraction of the year for the remaining days
        # This requires knowing if the last part of the period is a leap year
        final_year_days = days_in_year(adjusted_date.year)
        year_fraction = remaining_days / final_year_days
        
        # Calculate the precise year difference
        precise_year_difference = year_difference + year_fraction
    
        return precise_year_difference'''

        # Define the dates
        start_date = issuance_date
        end_date = maturity_date

        # Calculate the number of complete years
        years = end_date.year - start_date.year
        if (end_date.month, end_date.day) < (start_date.month, start_date.day):
            years -= 1

        # Calculate the number of complete months within the partial year
        months = end_date.month - start_date.month
        if end_date.day < start_date.day:
            months -= 1
        if months < 0:
            months += 12

        # Calculate the remaining days within the partial month
        if end_date.day >= start_date.day:
            days = end_date.day - start_date.day
        else:
            previous_month_end_date = end_date.replace(day=1) - timedelta(days=1)
            days = (previous_month_end_date.day - start_date.day) + end_date.day

        # Calculate the total difference in fractional years
        total_years = years + (months / 12)

        # Check if the end year is a leap year to adjust the days difference
        is_leap_year = lambda year: (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        days_in_year = 366 if is_leap_year(end_date.year) else 365
        total_years += days / days_in_year

        return total_years
    
    @staticmethod
    def get_date_years_ago(end_date, year_difference):
        def is_leap_year(year):
            """Check if a year is a leap year."""
            return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        # Calculate the start year by subtracting the truncated year difference from the end year
        start_year = end_date.year - math.trunc(year_difference)
        
        # Handle the case where subtracting the years results in a date before February 29 in a leap year
        if end_date.month == 2 and end_date.day == 29 and not is_leap_year(start_year):
            # Adjust the start date to February 28 if the start year is not a leap year
            start_date = datetime(start_year, end_date.month, 28)
        else:
            # Ensure the new date does not exceed the month's day limit
            try:
                start_date = datetime(start_year, end_date.month, end_date.day)
            except ValueError:
                # Adjust for cases like April 31st; set to the last day of the month
                start_date = datetime(start_year, end_date.month + 1, 1) - timedelta(days=1)
        return start_date.date()
    
    @staticmethod
    def ln_nper(issuance, maturity, fper, type):
              
        rel_nper = (relativedelta(maturity, issuance).years * 12 / (12 / fper)) + (relativedelta(maturity, issuance).months / (12 / fper))
        if (rel_nper - math.trunc(rel_nper)) > 0 and type == 'fw2': 
            rel_nper += 1

        return rel_nper

    @staticmethod
    def days360(start_date,end_date,method_eu=False):
        start_day = start_date.day
        start_month = start_date.month
        start_year = start_date.year
        end_day = end_date.day
        end_month = end_date.month
        end_year = end_date.year
    
        if start_day == 31 or (not method_eu and start_month == 2 and (start_day == 29 or (start_day == 28 and not Support.is_leap_year(start_year)))): # type: ignore
            start_day = 30
    
        if end_day == 31:
            if not method_eu and start_day != 30:
                end_day = 1
                end_month += 1 if end_month != 12 else 1
                end_year += 1 if end_month == 1 else 0
            else:
                end_day = 30
        
        return end_day + end_month * 30 + end_year * 360 - start_day - start_month * 30 - start_year * 360

    @staticmethod
    def solver(v1, v2, v3, v4):
        solution = {}
        objetivo = v4
        
        # Define the objective function
        def objective (x):
            x1, x2, x3, x4 = x
            return (x1 * x2) / x3 

        # Define the constraint function(s)
        def constraint1 (x):
            return ((x[0] * x[1]) / x[2]) - x[3]
        
        # Define the initial guess for the variables
        x0 = [v1, v2, v3, v4]

        # Bounds for the decision variables
        bnds = [(0, None), (v2, v2), (v3, v3), (v4, v4)]
        
        # Constraints: Defines the equality constraint
        cons = [{'type': 'eq', 'fun': constraint1}]
        
        # Tolerance: Sets the termination tolerance for the optimization.
        tolerance = 1e-8

        # Optimization Process: Uses the SLSQP method for constrained optimization.
        sol = minimize(objective, x0, method = 'SLSQP', bounds = bnds, constraints = cons, tol = tolerance)

        # Checking Solution: Verifies if the solution meets the required tolerance and constraints.
        if abs(sol.fun - objetivo) <= tolerance and sol.success and sol.fun > 0:
            t1 = sol.x[0]
            t2 = sol.x[1]
            t3 = sol.x[2]
            test = (t1 * t2) / t3
            solution = {
                'result': t1,
                'test': test,
                'message': f'Solution found within the desired tolerance range with a residual of {test - v4}'
            }
        else:
            solution = {
                'result': 0,
                'test': 0,
                'message': 'No solution found within the desired tolerance range.'
            }
        
        return solution
    
    @staticmethod
    def closestDate(fechas, buscada):
        return min((fecha for fecha in fechas if fecha >= buscada), default=None)
    
    @staticmethod
    def get_folder_path():
        home = pathlib.Path.home()
        desktop = home / "Desktop"
        
        if not desktop.exists():
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        
        folder_path = os.path.join(desktop if os.path.exists(desktop) else home, 'cxfiLogs')
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
                
        return folder_path
