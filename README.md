# Powerplant Coding Challenge

## Descripción 
Este desafío de programación resuelve el problema de cálculo del plan de producción de energía.

Hay que tener en cuenta varias variables para llevar a cabo el cálculo:
- Las centrales disponibles, con su combustible, eficiencia y valores de Pmin/Pmax.
- Los precios de cada combustible.
- La carga total.

Teniendo en cuenta todo, se debe devolver el número de MW que tiene que producir cada una de las centrales, buscando la combinación más barata.


## Instalación y Ejecución

Para poder ejecutar este proyecto, necesitas tener Python instalado (versión 3.8 o superior) y seguir los siguientes pasos:

- Primero, instala las librerías necesarias ejecutando este comando en la terminal:
   `pip install -r requirements.txt`

- Para arrancar la API, simplemente ejecuta:
   `python main.py`
   (Esto levanta la API en el puerto 8888 por defecto)

## Como probarlo

Puedes hacerle una petición POST una vez levantada la API enviando uno de los JSON de prueba. Desde PowerShell, el comando sería algo así (puede no adaptarse a tu caso):

`curl.exe -X POST http://127.0.0.1:8888/productionplan -H "Content-Type: application/json" -d "@example_payloads/payload1.json"`

## Lógica del Algoritmo

El código ha sido desarrollado sin usar herramientas existentes como indicaban los requerimientos. 
La lógica principal es la siguiente:
- Primero, creo una lista para alojar todos los datos de las plantas
- En el proceso creo dos listas, una para separar el nombre de las plantas por su combustible y otra para calcular el precio del MW por cada una.
- Tras esas listas empiezo a restar al load la capacidad que tenga el viento, siempre determinada por el % de este que haya.
- Después de restar el viento, junto las centrales de gas y keroseno, para ordenar manualmente cual es la que tiene menos precio por MW.
- Siguiendo con esa lista, empiezo a restar load por la central mas eficiente, respetando los pmin y pmax de estas.
- Si la carga no llegase a 0, empiezo entonces a restar parte del viento para poder sumarselo a alguna central y llegar a su pmin hasta dejar la carga a 0, si siguiera teniendo significa que no tenemos potencia suficiente para llegar a la cuota.
- Recogemos las producciones asignadas y lo devolvemos en el formato especificado.

## Tiempo invertido y Mejoras Futuras

He intentado ajustarme a la recomendación de no invertir más de 4 horas en la prueba, aún así habré utilizado unas 6h para poder resolver el problema. Aquí podéis ver un desglose del tiempo dedicado.

- 0-1h: Entender el problema y los requisitos, anotarlos y meterlos en una lista de objetivos.
- 1-2h: Una vez entendido el problema dedico tiempo para ordenar ideas y hacer flujos sencillos que me permitan dividir todo por partes mas digestibles.
- 2-5h: Codificar según el plan tomado en el paso anterior, si en esta fase encuentro problemas edito el diagrama hecho.
- 5-6h: Adición de logs, excepciones y comprobaciones posteriores. 


Mejoras futuras:
- El código, aunque procesa el payload3.json de la manera que se espera en response3.json es imperfecto, empezaría corrigiendo o corrigiendo los siguientes puntos:
 1. Cuando descontamos la producción del viento de los molinos y sigue quedando carga, esta se divide directamente entre las centrales térmicas restantes, pero cuando los pmin que quedan son superiores a la carga restante se asigna al turbojet de keroseno, lo cual no sería lo mas eficiente. Os adjunto en el pull-request el ejemplo con el que da error de cálculo llamado "payload4.json".

 2. Implementar una batería de pruebas para asegurar un correcto funcionamiento del código y detectar posibles errores.

 3. Un archivo Dockerfile para que se pueda ejecutar en cualquier máquina sin necesidad de instalar Python.

 4. Meter el coste de las emisiones de CO2 en la fórmula de las plantas de gas.
