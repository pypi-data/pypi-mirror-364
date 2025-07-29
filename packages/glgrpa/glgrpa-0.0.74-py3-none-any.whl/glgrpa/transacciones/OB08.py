import os
from ..SAP import SAP
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

import pandas as pd

class OB08(SAP):
    titulo_pagina_inicio = 'Modificar vista "Tipos de cambio para la conversión": Resumen'
    
    def __init__(self, base_url: str, usuario: str, clave: str,  driver = None, dev: bool = False):
        super().__init__(
            base_url=base_url, 
            usuario=usuario,
            clave=clave,
            driver=driver, 
            dev=dev
        )
    
    def finalizar(self) -> None:
        """ Finaliza la transacción OB08. """
        self.mostrar("Finalizando transacción OB08")
        self.enviar_tecla_ventana('SHIFT', 'F3')
    
    def guardar(self) -> None:
        """ Guarda los cambios realizados en la transacción OB08. """
        self.mostrar("Guardando cambios en la transacción OB08")
        self.enviar_tecla_ventana('CTRL', 'S')
        self.demora()
        
    def entradas_nuevas(self) -> bool:
        """ Accede a la página de entradas nuevas y espera a que se cargue correctamente durante 3 segundos."""
        reintentos = 0
        if self.driver.title == self.titulo_pagina_inicio:
            
            self.enviar_tecla_ventana('F5')
            
            nuevo_titulo_pagina = 'Entradas nuevas: Resumen de entradas añadidas'
            titulo_actual_pagina = self.driver.title
            while titulo_actual_pagina != nuevo_titulo_pagina and reintentos < 3:
                self.demora(1)
                reintentos += 1
                titulo_actual_pagina = self.driver.title
                
            if reintentos >= 3:
                # Tomar screenshot para debugging
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_screenshot = f"error_entradas_nuevas_OB08_{timestamp}"
                self.tomar_screenshot(nombre_screenshot)
                
                self.mostrar("❌ No se pudo acceder a la página de entradas nuevas después de 3 segundos", True)
                self.mostrar(f"📸 Screenshot de debugging guardado: {nombre_screenshot}.png", True)
                self.mostrar(f"🔍 Título actual de página: '{titulo_actual_pagina}'", True)
                self.mostrar(f"🎯 Título esperado: '{nuevo_titulo_pagina}'", True)
                self.cerrar_navegador()
                return False
            
            self.mostrar("📃 Accediendo a la página de entradas nuevas")
            
        elif self.driver.title == 'Actualizar vista de tabla: Acceso':
            self.mostrar("❌ No se está en la página de entradas nuevas", True)
            raise ValueError("No se está en la página de entradas nuevas")
            
        return True
    
    def formato_fecha_cotizacion(self, formato: str = '%d/%m/%Y') -> str:
        """ Siempre es la fecha de ayer. Para el formato de entrada se debe usar '%d%m%Y' """
        fecha = datetime.now() - timedelta(days=1)
        return fecha.strftime(formato)
    
    def formato_divisa(self, valor_divisa: float|str) -> str:
        """ Formatea la divisa para que sea compatible con SAP. """
        if isinstance(valor_divisa, str):
            valor_divisa = valor_divisa.replace('.', '').replace(',', '.')
            valor_divisa = float(valor_divisa)
            
        return f"{valor_divisa:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def formato_tipo_cotizacion(self, tipo: str) -> str:
        """ Formatea el tipo de cotización para que sea compatible con SAP """
        if tipo.lower() == 'compra':
            return 'G'
        elif tipo.lower() == 'venta':
            return 'B'
        else:
            raise ValueError("Tipo de cotización no válido. Debe ser 'compra' o 'venta'.")
    
    def formato_moneda(self, moneda: str) -> str:
        """ Formatea la moneda para que sea compatible con SAP """
        mapeo = {
            'Dolar U.S.A': 'USD',
            'Euro': 'EUR',
            'Dolar Australia': 'AUD',
            'Dolar Canadá': 'CAD',
            'Dolar Nueva Zelanda': 'NZD',
            'Libra Esterlina': 'GBP',
            'YENES': 'JPY',
            'Real Brasileño': 'BRL',
            'Peso Chileno': 'CLP',
            'Yuan': 'CNY',
            # Agrega más monedas según sea necesario
        }
        return mapeo.get(moneda, moneda.upper())
    
    def ingresar_tipo_de_cambio(self, df_divisas: pd.DataFrame) -> bool:
        """ Ingresa una nueva cotización en la tabla especificada. """
        if not self.entradas_nuevas():
            raise ValueError("No se pudo acceder a la página de entradas nuevas")

        df_divisas = self.__armar_tabla_para_sap(df_divisas)
        tabla = self.__convertir_tabla_sap_a_string(df_divisas)
        
        self.copiar_al_portapapeles(tabla)
        self.pegar_portapapeles_en_ventana_activa()
        self.guardar()
        
        alerta = self._alerta_transaccion()
        if alerta == "Los datos han sido grabados":
            self.mostrar("✅ Tipo de cambio ingresado correctamente")
            self.finalizar()
            return True
        elif alerta == 'Ya existe una entrada con la misma clave':
            self.mostrar("😣 "+alerta, True)
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('SHIFT', 'TAB')
            self.enviar_tecla_ventana('ENTER')
            self.enviar_tecla_ventana('SHIFT', 'F3')
        else:
            self.mostrar("❌ "+alerta, True)
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('SHIFT', 'TAB')
            self.enviar_tecla_ventana('ENTER')
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('ESC')
            
        
        raise ValueError(f"No se pudo ingresar el tipo de cambio. {alerta}")

    def __armar_tabla_para_sap(self, df_divisas: pd.DataFrame) -> pd.DataFrame:
        """ 
        Convierte una tabla de divisas entregada por el BNA en una tabla de divisas permitida por SAP. 
        
        El DataFrame de entrada debe tener las columnas: ``fecha``  ``compra`` ``venta``
        y las filas deben contener los valores de las divisas a ingresar.
        
        Ejemplo:
        ----
        
        | 24-06-2025  | compra  | venta   |
        |-------------|---------|---------|
        | Dolar USA   | 100.00  | 105.00  |
        | Euro        | 101.00  | 106.00  |

        Salida:
        ----
        | T... | Válido de | Cotiz.ind. | X | Factor (de) | De | = | Cotiz.di. | X | Factor (a) | A |
        |-------------|-----------|-------------|---|-------------|----|---|-----------|---|-------------|---|
        | B | 24062025 |         |  |         | USD |  | 100,0000  |  |         | ARS |
        | G | 24062025 |         |  |         | USD |  | 105,0000  |  |         | ARS |
        | B | 24062025 |         |  |         | EUR |  | 101,0000  |  |         | ARS |
        | G | 24062025 |         |  |         | EUR |  | 106,0000  |  |         | ARS |
        
        
        En caso de que no se pueda acceder a la página de entradas nuevas, se lanza una excepción.
        """
        if not self.entradas_nuevas():
            raise ValueError("No se pudo acceder a la página de entradas nuevas")
        
        # Copia el DataFrame para evitar modificar el original
        df = df_divisas.copy()
        
        # Renombrar las columnas del DataFrame
        df = df.rename(
            columns={
            df.columns[0]: 'moneda', 
            df.columns[1]: 'compra', 
            df.columns[2]: 'venta'
            }
        )
        
        # Transformar el DataFrame a formato largo (melt)
        df_melt = df.melt(
            id_vars=['moneda'], 
            value_vars=['compra', 'venta'],
            var_name='TCot - Tipo de Cotización', 
            value_name='T/C Cotizado directamente'
        )
        df_melt['TCot - Tipo de Cotización'] = df_melt['TCot - Tipo de Cotización'].apply(self.formato_tipo_cotizacion)
        df_melt['T/C Cotizado directamente'] = df_melt['T/C Cotizado directamente'].apply(self.formato_divisa)
        
        # Agregar columnas adicionales
        df_melt['Válido de'] = self.formato_fecha_cotizacion('%d%m%Y')
        df_melt['Moneda procedencia'] = df_melt['moneda'].apply(self.formato_moneda)
        df_melt['Moneda de destino'] = 'ARS'
        # Columnas adicionales para SAP, no se usan
        df_melt['T/C cotizado indirectamente'] = None
        df_melt['X'] = None
        df_melt['Factor (de)'] = None
        df_melt['='] = None
        df_melt['XX'] = None
        df_melt['Factor (a)'] = None
        
        # Seleccionar columnas para SAP
        columnas_sap = [
            'TCot - Tipo de Cotización', 
            'Válido de', 
            'T/C cotizado indirectamente', 
            'X', 
            'Factor (de)', 
            'Moneda procedencia', 
            '=', 
            'T/C Cotizado directamente',
            'XX', 
            'Factor (a)',
            'Moneda de destino', 
        ]
        df_sap = df_melt[columnas_sap]

        # Duplicar filas donde el tipo de cotización es 'B' y cambiar a 'M'
        mask_b = df_sap['TCot - Tipo de Cotización'] == 'B'
        df_b = df_sap[mask_b].copy()
        df_b['TCot - Tipo de Cotización'] = 'M'
        
        # Concatenar el DataFrame original con los duplicados
        df_sap = pd.concat([df_sap, df_b], ignore_index=True)
        df_sap = df_sap.sort_values(by=['Moneda procedencia', 'TCot - Tipo de Cotización']).reset_index(drop=True)

        return df_sap
    
    def __convertir_tabla_sap_a_string(self, df_divisas: pd.DataFrame) -> str:
        """ 
        Convierte la tabla de SAP a un formato de texto plano. 
        
        El separador es tabulador y el terminador de línea es salto de línea.
        """
        self.mostrar("📄 Convirtiendo tabla SAP a string")
        tabla_str = df_divisas.to_csv(sep='\t', index=False, header=False, lineterminator='\n')
        return tabla_str

    def _alerta_transaccion(self) -> str:
        """ Obtiene el texto de la alerta de transacción """
        self.mostrar("🔍 Obteniendo alerta de transacción")
        span_alerta, texto_alerta = self.buscar_elemento_en_iframes(By.CLASS_NAME, 'lsMessageBar')
        
        if span_alerta and texto_alerta:
            self.mostrar(f"✅ Alerta encontrada")
            return texto_alerta.strip().split('\n')[0]
        
        self.mostrar("❌ No se encontró alerta de transacción", True)
        return ""
    
# TEST
""" 
if __name__ == "__main__":
    # Ejemplo de uso
    ob08 = OB08(
        base_url='https://saplgdqa.losgrobo.com:44302/sap/bc/ui5_ui5/ui2/ushell/shells/abap', 
        usuario='gabriel.bellome@losgrobo.com',
        clave='Junio2025',
        driver=None, 
        dev=False
        )
    
    # DataFrame de ejemplo
    data = {
        '24-06-2025': ['Dolar U.S.A', 'Euro'],
        'compra': [100.00, 101.00],
        'venta': [105.00, 106.00]
    }
    df_divisas = pd.DataFrame(data)
    
    ob08.navegar_inicio_SAP()
    ob08.ir_a_transaccion('OB08')
    ob08.entradas_nuevas()
    
    # Ingresar tipo de cambio
    ob08.ingresar_tipo_de_cambio(df_divisas) 
 """