from fastapi import FastAPI, HTTPException
import uvicorn
import logging

# curl.exe -X POST http://127.0.0.1:8888/productionplan -H "Content-Type: application/json" -d "@example_payloads/payload1.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
@app.post("/productionplan")


def calcular_plan_produccion(payload: dict):
    
    try:

        if "load" not in payload or payload["load"] < 0:
            raise KeyError("Faltan load en el JSON o es un valor negativo")
        if "fuels" not in payload:
            raise KeyError("Faltan campos en el JSON (fuels)")
        if "powerplants" not in payload:
            raise KeyError("Faltan campos  en el JSON (powerplants)")

        carga_total = payload["load"]
        precio_gas = payload["fuels"]["gas(euro/MWh)"]
        precio_keroseno = payload["fuels"]["kerosine(euro/MWh)"]
        #precio_co2 = payload["fuels"]["co2(euro/ton)"]
        porcentaje_viento = payload["fuels"]["wind(%)"]

        tamaño_lista = len(payload["powerplants"])
        plantas = {}
        id_viento = []
        id_gas = []
        id_keroseno = []
        orden_termicas = []

        for i in range(tamaño_lista):
            if "name" not in payload["powerplants"][i]:
                raise KeyError(f"Faltan campos en el JSON (name) en la planta {i}")
            nombre_planta = payload["powerplants"][i]["name"]
            
            if "type" not in payload["powerplants"][i]:
                raise KeyError(f"Faltan campos en el JSON (type) en la planta {i}")
            if "efficiency" not in payload["powerplants"][i]:
                raise KeyError(f"Faltan campos en el JSON (efficiency) en la planta {i}")
            if "pmin" not in payload["powerplants"][i]:
                raise KeyError(f"Faltan campos en el JSON (pmin) en la planta {i}")
            if "pmax" not in payload["powerplants"][i]:
                raise KeyError(f"Faltan campos en el JSON (pmax) en la planta {i}")
            if "type" in payload["powerplants"][i] and payload["powerplants"][i]["type"] not in ["windturbine", "gasfired", "turbojet"]:
                raise ValueError(f"Tipo de planta no reconocido en la planta {i}")
            
            plantas[nombre_planta] = [
                nombre_planta,
                payload["powerplants"][i]["type"],
                payload["powerplants"][i]["efficiency"],
                payload["powerplants"][i]["pmin"],
                payload["powerplants"][i]["pmax"], 
                0  #usado
            ]

            if payload["powerplants"][i]["type"] == "windturbine":
                id_viento.append(nombre_planta)
            elif payload["powerplants"][i]["type"] == "gasfired":
                id_gas.append(nombre_planta)
                if payload["powerplants"][i]["efficiency"] == 0:
                    raise ValueError(f"La eficiencia no puede ser 0 en la planta {i}")
                orden_termicas.append( round(precio_gas / payload["powerplants"][i]["efficiency"], 1))
            elif payload["powerplants"][i]["type"] == "turbojet":
                id_keroseno.append(nombre_planta)
                if payload["powerplants"][i]["efficiency"] == 0:
                    raise ValueError(f"La eficiencia no puede ser 0 en la planta {i}")
                orden_termicas.append( round(precio_keroseno / payload["powerplants"][i]["efficiency"], 1))

            
        #logger.info(id_viento)
        #logger.info(id_gas)
        #logger.info(id_keroseno)


        if carga_total > 0 and tamaño_lista > 0 :
            if len(id_viento) > 0:
                for id in id_viento:
                    plantas[id][4] = plantas[id][4] * porcentaje_viento / 100
                    while round(carga_total, 1) >= 0.1 and round(plantas[id][4], 1) >= 0.1:
                        carga_total = round(carga_total - 0.1, 1) 
                        plantas[id][4] = round(plantas[id][4] - 0.1, 1)
                        plantas[id][5] = round(plantas[id][5] + 0.1, 1)
            
            id_termicas = id_gas + id_keroseno

            definitiva_orden = []
            definitiva_termicas = []

            while len(orden_termicas) > 0:
        
                indice_elegido = 0
                
                for i in range(1, len(orden_termicas)):
                    if orden_termicas[i] < orden_termicas[indice_elegido]:
                        indice_elegido = i
                        
                definitiva_orden.append(orden_termicas[indice_elegido])
                definitiva_termicas.append(id_termicas[indice_elegido])
                
                del orden_termicas[indice_elegido]
                del id_termicas[indice_elegido]

            logger.info(definitiva_orden)
            logger.info(definitiva_termicas)
            logger.info(id_termicas)
            


            for id in definitiva_termicas:
                
                pmin = plantas[id][3]
                
                if round(carga_total, 1) >= pmin:
                    
                    while round(carga_total, 1) >= 0.1 and round(plantas[id][4], 1) >= 0.1:
                        carga_total = round(carga_total - 0.1, 1) 
                        plantas[id][4] = round(plantas[id][4] - 0.1, 1)
                        plantas[id][5] = round(plantas[id][5] + 0.1, 1) 
            
            logger.info(plantas)
            logger.info(carga_total)

            if round(carga_total, 1) >= 0.1:
                total_resta_viento = 0
                
                for id in definitiva_termicas:
                    pmin = plantas[id][3]
                    
                    if round(carga_total, 1) >= 0.1 and round(plantas[id][4], 1) >= 0.1:
                        while (round(carga_total, 1) >= 0.1 or round(plantas[id][5], 1) < pmin) and round(plantas[id][4], 1) >= 0.1:
                            if round(carga_total, 1) >= 0.1:
                                carga_total = round(carga_total - 0.1, 1) 
                            else:
                                total_resta_viento = round(total_resta_viento + 0.1, 1)
                            plantas[id][4] = round(plantas[id][4] - 0.1, 1)
                            plantas[id][5] = round(plantas[id][5] + 0.1, 1)
                for id in id_viento:
                    while total_resta_viento >= 0.1 and round(plantas[id][5], 1) >= 0.1:
                            total_resta_viento = round(total_resta_viento - 0.1, 1) 
                            plantas[id][4] = round(plantas[id][4] + 0.1, 1)
                            plantas[id][5] = round(plantas[id][5] - 0.1, 1)


            logger.info(plantas)
            logger.info(carga_total)    
            
            respuesta_final = []
            carga_total_comprobacion = payload["load"]
            for id in plantas:
        
                if round(plantas[id][5], 1) > 0:
                    carga_total_comprobacion = round(carga_total_comprobacion - plantas[id][5], 1)

            logger.info(carga_total_comprobacion)

            if round(carga_total_comprobacion, 1) == 0:
                for nombre in plantas:
                    produccion_asignada = plantas[nombre][5] 
                    
                    planta_json = {
                        "name": nombre,
                        "p": produccion_asignada
                    }
                    
                    respuesta_final.append(planta_json)
            else:
                logger.warning(f"No se pudo cubrir la carga. Faltan: {carga_total_comprobacion} MW. Revisar.")
                raise ValueError(f"Error crítico: No se pudo cubrir la carga. Faltan: {carga_total_comprobacion} MW. Revisar.")

    # Excepciones HTTP de -> https://raiolanetworks.com/ayuda/errores-http-explicados/
    except (KeyError, ValueError) as e:
        logger.error({e})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error({e})
        raise HTTPException(status_code=500, detail=str(e))        

    return respuesta_final

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
    