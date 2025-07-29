import numpy as np
import pandas as pd
from fuzzywuzzy import process

class Consolidados:
    '''
    El documento .xlsx debe tener el formato "Subsidios 'Mes'.xlsx", ej: "Subsidios Enero.xlsx"
    mes: El mes que se está analizando, con formato "#. Mes", ej: "1. Enero" -> String
    Diccionario_Master: El diccionario que asocia municipios con negocios -> Diccionario
    nombre_columnas: Lista con el nombre de las columnas que deberían estar en el documeto leído -> Lista

    '''
    def __init__(self, mes, Diccionario_Master, nombre_columnas):
        self.mes=mes
        self.municipio_negocio=Diccionario_Master
        self.nombre_columnas=nombre_columnas
        #self.meses_dict = {
        #    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        #    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        #    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        #}

    def leer(self):
        self.subsidios = pd.read_excel("Subsidios {}.xlsx".format(self.mes.split(".")[1].strip()),sheet_name="Consolidado 5-433A")
    
    def match_producto(self, prod, choices, threshold=88):
        best_match, score = process.extractOne(prod, choices)
        if score >= threshold:
            return best_match
        return None
    
    def limpiar_municipios(self, municipio, diccionario):
        valor = self.match_producto(municipio, list(diccionario.keys()), 70)
        if valor == None:
            return "MEDELLIN"
        return valor
    
    def Limpieza_Transformacion(self, df_entrada):
        df=df_entrada.copy()
        df.columns = list(map(lambda x: self.match_producto(x, self.nombre_columnas, 88), df.columns))

        # Procesamiento de la fecha para extraer el mes
        nombre_mes = self.mes.split(".")[1].strip() if "." in self.mes else self.mes.strip()
        df["Mes Reporte"] = nombre_mes

        columnas_objetivo = [
        "CAN_SUBSIDIOS_ASIGNADOS",
        "Cédula", 
        "Nombres y Apellidos", 
        "Mes Reporte",
        "Municipio del Hogar", 
        "Valor SFV",
        "Descripción Modalidad de Vivienda"]

        columnas_unicas = []
        vistos = set()
        for i, col in enumerate(df.columns):
            if col in columnas_objetivo and col not in vistos:
                columnas_unicas.append(i)  # usamos índice, no nombre
                vistos.add(col)

        # Seleccionamos por índice, no por nombre, para evitar duplicados
        df_limpio = df.iloc[:, columnas_unicas]

        df_final = df_limpio.rename(columns={
        "CAN_SUBSIDIOS_ASIGNADOS": "Cuenta",
        "Cédula": "Cédula del beneficiario",
        "Nombres y Apellidos": "Nombre del beneficiario",
        "Municipio del Hogar": "Municipio",
        "Valor SFV": "Valor Subsidio",
        "Descripción Modalidad de Vivienda": "Tipo"})

        # Corrección de tildes en la columna "Tipo"
        #En la columna "DescripciOn Modalidad de Vivienda" todas las palabras agudas que terminan en "ón" están escritas como On.
        df_final["Tipo"] = df_final["Tipo"].str.replace(r'([a-zA-Z])On\b', r'\1ón', regex=True)

        # Convertir valores a millones y valor absoluto
        df_final["Valor Subsidio"] = (
            df_final["Valor Subsidio"]
            .abs()
            .apply(lambda x: x/1000000)
        )

        df_final["Municipio"] = df_final["Municipio"].apply(lambda x: self.limpiar_municipios(x, self.municipio_negocio))
        df_final["Negocio"] = df_final["Municipio"].map(self.municipio_negocio)

        # Reordenamos columnas según lo solicitado
        column_order = [
            "Cuenta",
            "Cédula del beneficiario",
            "Nombre del beneficiario",
            "Mes Reporte",
            "Municipio",
            "Valor Subsidio",
            "Tipo",
            "Negocio"
        ]
        df_final = df_final[column_order]

        df_final["Cuenta"] = pd.to_numeric(df_final["Cuenta"], errors='coerce').astype("Int64")
        df_final["Cédula del beneficiario"] = pd.to_numeric(df_final["Cédula del beneficiario"], errors='coerce').astype("Int64")

        return df_final
    
    def Asignados(self):
        self.leer()
        #Tabla asignados
        subsidios_asignados = self.subsidios[(self.subsidios["EST_SUBSIDIO_VIVIENDA (Tabla 80)"]=="Asignado")]

        # Comprobación de municipios vacíos
        if np.nan in subsidios_asignados["Municipio del Hogar"]:
            print("Hay municipios vacíos", "\n",
                  "Filas:", (subsidios_asignados[subsidios_asignados["Municipio del Hogar"].isna()].index+2).tolist())
        else:
            subsidios_asignados_final=self.Limpieza_Transformacion(subsidios_asignados)
        
        return subsidios_asignados_final
    
    def Reajuste(self):
        self.leer()
        #Tabla subsidios_Indexados -> Reajuste
        subsidios_Reajuste = self.subsidios[(self.subsidios["EST_SUBSIDIO_VIVIENDA (Tabla 80)"]=="Indexados")]

        # Comprobación de municipios vacíos
        if np.nan in subsidios_Reajuste["Municipio del Hogar"]:
            print("Hay municipios vacíos", "\n",
                  "Filas:", (subsidios_Reajuste[subsidios_Reajuste["Municipio del Hogar"].isna()].index+2).tolist())
        else:
            subsidios_Reajuste_final=self.Limpieza_Transformacion(subsidios_Reajuste)
        
        return subsidios_Reajuste_final
    
    def Pagados(self):
        self.leer()
        #Tabla aplicados (pagados)
        subsidios_aplicados = self.subsidios[self.subsidios["Tipo"].str.contains("giro",case=False,na=False)]

        # Comprobación de municipios vacíos
        if np.nan in subsidios_aplicados["Municipio del Hogar"]:
            print("Hay municipios vacíos", "\n",
                  "Filas:", (subsidios_aplicados[subsidios_aplicados["Municipio del Hogar"].isna()].index+2).tolist())

        else:
            subsidios_aplicados_final = subsidios_aplicados[~subsidios_aplicados["Descripción Estado Solicitud"].str.contains("anticip",case=False,na=False)].copy()
            subsidios_pagados_final = self.Limpieza_Transformacion(subsidios_aplicados_final)

        return subsidios_pagados_final
    
    def importar(self):
        nombre_importar="consolidado_{}.xlsx".format(self.mes.split(".")[1].strip())

        subsidios_asignados_final=self.Asignados()
        subsidios_Reajuste_final=self.Reajuste()
        subsidios_pagados_final=self.Pagados()

        with pd.ExcelWriter(nombre_importar, engine="openpyxl") as writer:
            subsidios_asignados_final.to_excel(writer, sheet_name="Subsidios_Asignados", index=False)
            subsidios_Reajuste_final.to_excel(writer, sheet_name="Subsidios_Reajuste", index=False)
            subsidios_pagados_final.to_excel(writer, sheet_name="Subsidios_Pagados", index=False)