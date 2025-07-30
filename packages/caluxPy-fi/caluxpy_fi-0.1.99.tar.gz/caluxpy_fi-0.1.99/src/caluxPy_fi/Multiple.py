#import sys, os
#from pathlib import Path
#sys.path.append(str(Path(__file__).resolve().parent.parent))
import pandas as pd, time, logging
from caluxPy_fi.FixedIncome import FixedIncome
from caluxPy_fi.Support import Support

class Multiple:

    def __init__(self, data: pd.DataFrame, additional_ops: dict = {}, lang = 'eng'):

        desktop = Support.get_folder_path()
        logFormatter = logging.Formatter("%(asctime)s: [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        _logger = logging.getLogger()
        _logger.setLevel(logging.DEBUG)
        fileHandler = logging.FileHandler("{0}/{1}.log".format(desktop, 'cMult'), mode = 'w', encoding = 'utf-8')
        fileHandler.setFormatter(logFormatter)
        _logger.addHandler(fileHandler)
    
        self.start_time = time.perf_counter()
        self.data = data.to_dict('records')
        self.additional_ops = additional_ops
        self.mResults = []
        i = 0
        while i < len(self.data):
            #Normal Attributes
            for key, values in self.data[i].items():
                setattr(self, key[2:], values) # type: ignore
            #Additional Attributes passed through the class
            if len(additional_ops) >= 1:
                for op, attributes in additional_ops.items():
                    for attribute, value in attributes.items():
                        setattr(self, attribute, value)
            
            try:
                repos_margin = self.margin if lang == 'eng' else self.margen if lang == 'esp' else '' # type: ignore
            except Exception:
                repos_margin = None
            try:
                repo_rate = self.interestRate if lang == 'eng' else self.tasaInteres if lang == 'esp' else '' # type: ignore
            except Exception:
                repo_rate = None
            try:
                repo_tenure = self.repoTenure if lang == 'eng' else self.plazoRepos if lang == 'esp' else '' # type: ignore
            except Exception:
                repo_tenure = None

            try:
                rules = self.rules if lang == 'eng' else self.reglas if lang == 'esp' else '' # type: ignore
            except Exception:
                rules = {}

            try:
                ratio = self.ratio # type: ignore
            except Exception as e:
                ratio = ''
            
            settlement_date = self.settlementDate if lang == 'eng' else self.fechaLiquidacion if lang == 'esp' else '' # type: ignore
            issuance_date = self.issuanceDate if lang == 'eng' else self.fechaEmision if lang == 'esp' else '' # type: ignore
            maturity_date = self.maturityDate if lang == 'eng' else self.fechaVencimiento if lang == 'esp' else '' # type: ignore
            coupon = self.coupon if lang == 'eng' else self.cupon if lang == 'esp' else '' # type: ignore
            ytm = self.ytm if lang == 'eng' else self.rendimiento if lang == 'esp' else '' # type: ignore
            face_value = self.facialValue if lang == 'eng' else self.monto if lang == 'esp' else '' # type: ignore
            issuer = self.issuer if lang == 'eng' else self.emisor if lang == 'esp' else '' # type: ignore
            methodology = self.methodology if lang == 'eng' else self.metodologia if lang == 'esp' else '' # type: ignore
            periodicity = self.periodicity if lang == 'eng' else self.periodicidad if lang == 'esp' else '' # type: ignore
            repayment_type = self.repaymentType if lang == 'eng' else self.tipoPago if lang == 'esp' else '' # type: ignore
            coupon_type = self.couponType if lang == 'eng' else self.tipoCupones if lang == 'esp' else '' # type: ignore
            forward_date = self.forwardDate if lang == 'eng' else self.forwardDate if lang == 'esp' else '' # type: ignore
            amortization_start_date = self.amotizationDate if lang == 'eng' else self.fechaAmortizacion if lang == 'esp' else '' # type: ignore
            amortization_periods = self.amortizationTimes if lang == 'eng' else self.cantidadAmortizaciones if lang == 'esp' else '' # type: ignore
            amortization_periodicity = self.amortizationPeriodicity if lang == 'eng' else self.periodicidadAmortizaciones if lang == 'esp' else '' # type: ignore
            amortizable_percentage = self.amortizablePercentage if lang == 'eng' else self.porcentajeAmortizable if lang == 'esp' else '' # type: ignore
            
            fi_instance = FixedIncome(settlement_date = settlement_date, 
                                      issuance_date = issuance_date, 
                                      maturity_date = maturity_date, 
                                      coupon = coupon, 
                                      ytm = ytm, 
                                      face_value = face_value, 
                                      issuer = issuer, 
                                      methodology = methodology, 
                                      periodicity = periodicity, 
                                      repayment_type = repayment_type, 
                                      coupon_type = coupon_type, 
                                      forward_date = forward_date, 
                                      amortization_start_date = amortization_start_date, 
                                      amortization_periods = amortization_periods, 
                                      amortization_periodicity = amortization_periodicity, 
                                      amortizable_percentage = amortizable_percentage, 
                                      date_format = '%Y-%m-%d', 
                                      multiple = True,
                                      repo_margin = repos_margin,
                                      repo_rate = repo_rate,
                                      repo_tenure = repo_tenure,
                                      flr_rules = rules,
                                      flr_ratio = ratio,
                                      lang = lang)
            calculador_results = fi_instance.get_results()
            self.mResults.append(calculador_results)
            prompt = f'Calculated - {i + 1} of {len(data)}' if lang == 'eng' else f'Calculados - {i + 1} de {len(data)}'
            _logger.info(f'{prompt} : ({issuer} | {maturity_date})')
            i += 1

        self.df_resultados_multiples = pd.DataFrame(self.mResults)
        self.end_time = time.perf_counter()
        self.process_time = self.end_time - self.start_time
        _logger.info(f'{self.process_time} {'secs' if lang == 'eng' else 'segs'}')
        _logger.removeHandler(fileHandler)
        fileHandler.close()

    def get_results(self):

        return self.mResults

    def get_results_df(self):

        return self.df_resultados_multiples
    
    def processTime(self):

        return self.process_time