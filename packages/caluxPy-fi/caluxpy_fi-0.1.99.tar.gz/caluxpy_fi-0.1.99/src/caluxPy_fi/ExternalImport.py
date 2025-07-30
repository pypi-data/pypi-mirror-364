import pandas as pd, logging
from collections import Counter
from caluxPy_fi.Support import Support

class ExternalImport:
    
    def __init__(self, file = '', df = '', file_type = '', initial_row = 0, columns = '', column_type = {}):#, repos = False, repos_attributes = [], medida = False):
        self.file = file
        self.file_type = file_type
        self.initial_row = initial_row
        self.columns = columns
        self.df = None
        self.setup_logging()
        self.read_file()
        self.validate_data()

    def setup_logging(self):
        desktop = Support.get_folder_path()
        logFormatter = logging.Formatter("%(asctime)s: [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        fileHandler = logging.FileHandler(f"{desktop}/ei.log", mode='w', encoding='utf-8')
        fileHandler.setFormatter(logFormatter)
        self.logger.addHandler(fileHandler)

    def read_file(self):
        if self.file:
            try:
                if self.file_type == '.csv':
                    self.df = pd.read_csv(self.file, header=self.initial_row)
                elif self.file_type == '.xlsx':
                    self.df = pd.read_excel(self.file, header=self.initial_row)
                else:
                    self.logger.error(f'Unsupported file type: {self.file_type}')
                    raise ValueError(f'Unsupported file type: {self.file_type}')
            except Exception as e:
                self.logger.exception(f'Failed to read file: {self.file}. Error: {e}')
                raise

    def validate_data(self):
        # Splitting validation into different aspects
        self.validate_dates()
        self.validate_numbers()
        self.validate_percentages()
        self.cleanup_errors()
        
    def validate_dates(self):
        date_columns = [col for col in self.df.columns if col.startswith('d')] # type: ignore
        for col in date_columns:
            self.df[col] = pd.to_datetime(self.df[col], errors='coerce') # type: ignore
            # Further custom validation can be implemented here

    def validate_numbers(self):
        number_columns = [col for col in self.df.columns if col.startswith('n')] # type: ignore
        for col in number_columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce') # type: ignore
            # Add any specific number validation here

    def validate_percentages(self):
        percentage_columns = [col for col in self.df.columns if col.startswith('p')] # type: ignore
        for col in percentage_columns:
            self.df[col] = self.df[col].apply(self.convert_percentage) # type: ignore
            # Add any specific percentage validation here

    def convert_percentage(self, value):
        try:
            if isinstance(value, str) and '%' in value:
                return float(value.strip('%')) / 100
            return float(value)
        except ValueError:
            self.errors.append(f"Invalid percentage value: {value}") # type: ignore
            return pd.NA
    
    def cleanup_errors(self):
        # Example of removing rows based on certain validation criteria
        self.df.dropna(inplace=True)  # This is a placeholder for actual error handling logic # type: ignore

    def get_results(self):
        return self.df.to_dict('records')    # type: ignore
    
    def __del__(self):
        # Ensure the logging handlers are properly closed
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)         
        
    def getResults(self):

        return self.importedData # type: ignore

    def processTime(self):

        return self.tiempo_calculo # type: ignore

    def conteoErrores(self, my_dict):
        conteo = 0
        # Create a Counter object for each list in the dictionary
        counters = {key: Counter(values) for key, values in my_dict.items()}
        # Display the counts for each list in the dictionary
        for key, counter in counters.items():
            #print(f"Conteo para '{key}':")
            for element, count in counter.items():
            #    print(f"{element}: {count}")
                conteo += count
        return conteo