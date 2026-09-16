import os
import time
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = FastAPI(title="AutoCheck API", version="1.0")

# Permitir consultas desde cualquier origen (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def obtener_dni(cuit):
    limpio = "".join(filter(str.isdigit, str(cuit)))
    if len(limpio) == 11:
        prefijo = limpio[:2]
        if prefijo in ["20", "23", "24", "27", "25", "26"]:
            return str(int(limpio[2:10]))
        elif prefijo in ["30", "33", "34"]:
            return "Persona Jurídica (Empresa)"
    return "No identificable"

@app.get("/")
def home():
    return {"status": "ok", "message": "AutoCheck API activa"}

@app.get("/consultar")
def consultar_dominio(dominio: str = Query(..., min_length=6, max_length=10)):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.style_sheet_settings": 2
    }
    options.add_experimental_option("prefs", prefs)

    # Detectar entorno: Linux/Render o Windows Local
    if os.path.exists("/usr/bin/chromium"):
        options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "https://tributariomuni.cordoba.gob.ar/automotor"
    resultado_datos = {}
    
    try:
        driver.get("about:blank")
        driver.delete_all_cookies()

        driver.get(url)
        wait = WebDriverWait(driver, 10)

        campo_dominio = wait.until(EC.presence_of_element_located((By.ID, "search")))
        campo_dominio.clear()
        campo_dominio.send_keys(dominio.upper())

        btn_buscar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(text(), 'Buscar')]")))
        btn_buscar.click()

        try:
            tab_info = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Información')]")))
            driver.execute_script("arguments[0].click();", tab_info)
            time.sleep(2.5)
        except Exception:
            pass

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        resultado_datos['Dominio'] = dominio.upper()

        texto_limpio = soup.get_text(separator="\n", strip=True)
        lineas = [l.strip() for l in texto_limpio.split("\n") if l.strip()]

        for i, linea in enumerate(lineas):
            if "Titular" in linea and 'Titular' not in resultado_datos:
                resultado_datos['Titular'] = lineas[i+1] if i+1 < len(lineas) else linea
            elif ("CUIT" in linea.upper() or "CUIL" in linea.upper()) and 'DNI' not in resultado_datos:
                cuit_encontrado = lineas[i+1] if i+1 < len(lineas) else linea
                resultado_datos['DNI'] = obtener_dni(cuit_encontrado)
            elif "Marca" in linea and 'Marca' not in resultado_datos:
                resultado_datos['Marca'] = lineas[i+1] if i+1 < len(lineas) else linea
            elif "Modelo" in linea and 'Modelo' not in resultado_datos:
                resultado_datos['Modelo'] = lineas[i+1] if i+1 < len(lineas) else linea

        if 'Titular' not in resultado_datos:
            return {"error": "No se hallaron datos para el dominio ingresado."}

        return {"status": "ok", "datos": resultado_datos}

    except Exception as e:
        return {"error": f"Error en la consulta: {str(e)}"}
    finally:
        driver.quit()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("autocheck:app", host="0.0.0.0", port=port)
