import pandas as pd, datetime, sys, time, logging, numpy as np
from collections import Counter
from caluxPy_fi.Support import Support

class ExternalImport:
    
    def __init__(self, file = '', df = '', file_type = '', initial_row = 0, columns = ''):#, repos = False, repos_attributes = [], medida = False):
        self.file = file
        self.df = df
        self.file_type = file_type
        self.initial_row = initial_row
        self.columns = columns
        
        #self.repos = repos
        #self.repos_attributes = repos_attributes
        #self.medida = medida
        self.tiempo_inicio_calculo = time.perf_counter()

        desktop = Support.get_folder_path()

        logFormatter = logging.Formatter("%(asctime)s: [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        fileHandler = logging.FileHandler("{0}/{1}.log".format(desktop, 'ei'), mode = 'w', encoding = 'utf-8')
        fileHandler.setFormatter(logFormatter)
        logger.addHandler(fileHandler)

        if self.file != '':
            try:
                if self.file_type == '.csv':
                    self.df = pd.read_csv(self.file, index_col = None, header = self.initial_row)
                else:
                    self.df = pd.read_excel(self.file, index_col = None, header = self.initial_row) #index col makes column its index, none creates one
            except Exception:
                logger.exception(f'ERROR: Archivo - {file} - no existe! Saliendo..\n')
                logger.removeHandler(fileHandler)
                fileHandler.close()
                sys.exit()

        logger.info(f'AVISO: Se iniciará el procedimiento de validación de las informaciones - líneas: {len(self.df)} columnas: {len(self.df.columns)}\n') # type: ignore
        columna = list(self.df.columns.values) # type: ignore
        dicErrores = {}
        #Procedimiento de Validación
        for i in range(len(self.df.columns)): # type: ignore
            counter = 0
            errores = []
            #caso para las fechas:
            #1 - Se convierten todos los datos a formato datetime.date, si hay valores vacíos se pondrá NaT 
            #2 - Se itera por cada una de las celdas de la columna
            #3 - Si al convertir el valor es NaT se procede
            #4 - Valida si la columna es Fecha de liquidación fwd o inicio de amortizaciones
            #4.1 - Si es Fecha de Liquidación, se sustituye el NaT por la fecha del día de hoy
            #4.2 - Si es Fecha Fwd, se procede
            #4.2.1 - Se valida si el tipo de pago de cupón es fw3, debido a que este tipo necesita una fecha, los otros se calculan automáticos
            #4.2.1 - Si es fw3 se agrega a errores, si no es, se quita el NaT y se deja en blanco
            #4.3 - Si es fecha de inicio de amortización primero se verifica si el tipo de pago es bullet, y 
            #4.3.1 - Si es bullet se sustituye por blanco ya que bullet no tiene estas fechas, sino se lleva a errores
            #4.4 - Cualquier otra columna si tiene error, se lleva a errores

            if columna[i][0] == 'd': #--> Dates
                logger.info(f'Trabajando Columna {columna[i]}')
                self.df[columna[i]] = pd.to_datetime(self.df[columna[i]], format='%Y-%m-%d', errors='coerce').dt.date # 1 # type: ignore
                for cell in self.df[columna[i]]: # 2
                    if str(cell) == 'NaT': # 3
                        if columna[i] in ['d_settlementDate', 'd_forwardDate', 'd_amotizationDate']: # 4
                            if columna[i] == 'd_settlementDate': # 4.1
                                self.df.iloc[counter,i] = pd.to_datetime(datetime.date.today()) # type: ignore
                            elif columna[i] == 'd_forwardDate': # 4.2
                                if self.df['s_couponType'][counter] == 'fw3': # 4.2.1 # type: ignore
                                    logger.info(f'TypeError: -línea {counter}- en -{columna[i]}- no es una fecha - Registro se sacará de la data.\n')
                                    errores.append(counter)
                                else:
                                    self.df.iloc[counter, i] = pd.NaT # type: ignore
                            elif columna[i] == 'd_amotizationDate': # 4.3
                                if self.df['t_repaymentType'][counter] == 'bullet': # 4.3.1 # type: ignore
                                    self.df.iloc[counter, i] = pd.NaT # type: ignore
                                else: #4.4
                                    logger.info(f'TypeError: -línea {counter}- en -{columna[i]}- no es una fecha - Registro se sacará de la data.\n')
                                    errores.append(counter) 
                        else:
                            logger.info(f'TypeError: -línea {counter}- en -{columna[i]}- no es una fecha - Registro se sacará de la data.\n')
                            errores.append(counter)
                    counter += 1
            #caso para montos
            #1 - Primero se convierte todo a float, si hay errores se convierten a NaM
            elif columna[i][0] == 'n': #--> Numbers
                self.df[columna[i]] = pd.to_numeric(self.df[columna[i]], errors = 'coerce') # 1 # type: ignore
                for cell in self.df[columna[i]]:
                    if str(cell) == 'nan':
                        if columna[i] == 'n_amortizationTimes':
                            if self.df['t_repaymentType'][counter] == 'bullet': # type: ignore
                                self.df.iloc[counter, i] = np.nan # type: ignore
                            else:
                                logger.info(f'TypeError: -línea {counter}- en -{columna[i]}- no es un valor aceptado - Registro se sacará de la data.\n')
                                errores.append(counter)
                        else:
                            logger.info(f'TypeError: -línea {counter}- en -{columna[i]}- no es un valor aceptado - Registro se sacará de la data.\n')
                            errores.append(counter)
                    elif cell < 0: # type: ignore
                        logger.info(f'ValueError: -línea {counter}- en -{columna[i]}- es menor que 0 - Registro se convertirá a positivo.\n')
                        self.df.iloc[counter, i] = -cell # type: ignore
                    counter += 1
            #caso para tasas
            elif columna[i][0] == 'p': #--> Percentages
                dato = ''
                for cell in self.df[columna[i]]:
                    if cell == '':
                        if columna[i] == 'p_coupon' or columna[i] == 'p_ytm':
                            logger.info(f'MissingValue: -línea {counter}- en -{columna[i]}- no hay tasa especificada - Registro se sacará de la data.\n')
                            errores.append(counter)
                        else: 
                            if columna[i] == 'p_porcentaje_amortizable' and self.df['t_repaymentType'][counter] != 'bullet': # type: ignore
                                logger.info(f'MissingValue: -línea {counter}- en -{columna[i]}- no hay tasa especificada - Registro se sacará de la data.\n')
                                errores.append(counter)
                    else: 
                        if type(cell) != float and type(cell) != int:
                            dato = str(cell)
                            if '%' in dato:
                                logger.info(f'TypeError: -línea {counter}- en -{columna[i]}- es tipo {type(cell)} - Registro se convertirá a número.\n')
                                self.df.iloc[counter, i] = float(dato.strip('%')) / 100 # type: ignore
                            else:
                                logger.info(f'TypeError: -línea {counter}- en -{columna[i]}- no es un número - Registro se sacará de la data.\n')
                                errores.append(counter)
                        else:
                            if cell < 0:
                                logger.info(f'ValueError: -línea {counter}- en -{columna[i]}- es menor que 0 - Registro se convertirá a positivo.\n')
                                self.df.replace(self.df[columna[i]][counter], -cell, inplace = True) # type: ignore
                            elif cell > 1:
                                logger.info(f'ValueError: -línea {counter}- en -{columna[i]}- es mayor que 1 - Registro se dividirá por 100.\n')
                                self.df.replace(df[columna[i]][counter], cell / 100, inplace = True) # type: ignore
                    counter += 1
            elif columna[i] == 't_repaymentType':
                for cell in self.df[columna[i]]:
                    if cell == 'bullet':
                        self.df.iloc[counter, i + 4 : i + 4 + 3] = np.nan # type: ignore
                    counter += 1
            elif columna[i] == 's_couponType':
                if cell == 'normal': # type: ignore
                    self.df.replace(self.df.iloc[counter, i + 1], '', inplace = True) # type: ignore
            
            dicErrores[columna[i]] = errores

        conteo_errores = self.conteoErrores(dicErrores)
        if conteo_errores > 0:
            logger.info(f'AVISO: Validado con {conteo_errores} {"errores" if conteo_errores > 1 else "error"}\n')
        else:
            logger.info('Validado sin errores!\n')

        #Lista de líneas a eliminar
        lineas = []           
        for key, values in dicErrores.items():
            dicErrores = {key: values for key, values in dicErrores.items()}
            if len(values) > 0:
                for i in range(len(values)):
                    lineas.append(values[i])

        logger.info(f'AVISO: Se procederá a eliminar las líneas {lineas} de la data - Se importarán {len(self.df) - len(lineas)} líneas.')
        #self.df = self.df.dropna().reset_index(drop = True)
        self.tiempo_final_calculo = time.perf_counter()
        self.tiempo_calculo = self.tiempo_final_calculo - self.tiempo_inicio_calculo
        
        logger.removeHandler(fileHandler)
        fileHandler.close()

    def getResults(self):

        return self.df

    def processTime(self):

        return self.tiempo_calculo

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