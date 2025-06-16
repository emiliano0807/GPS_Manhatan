from flask import Flask, render_template, request, jsonify
import math
import random

app = Flask(__name__)

# Coordenadas de las ciudades
coord = {
    'Aguascalientes': [21.87641043660486, -102.26438663286967],
    'BajaCalifornia': [32.5027, -117.00371],
    'BajaCaliforniaSur': [24.14437, -110.3005],
    'Campeche': [19.8301, -90.53491],
    'Chiapas': [16.75, -93.1167],
    'Chihuahua': [28.6353, -106.0889],
    'CDMX': [19.432713075976878, -99.13318344772986],
    'Coahuila': [25.4260, -101.0053],
    'Colima': [19.2452, -103.725],
    'Durango': [24.0277, -104.6532],
    'Guanajuato': [21.0190, -101.2574],
    'Guerrero': [17.5506, -99.5024],
    'Hidalgo': [20.1011, -98.7624],
    'Jalisco': [20.6767, -103.3475],
    'Mexico': [19.285, -99.5496],
    'Michoacan': [19.701400113725654, -101.20829680213464],
    'Morelos': [18.6813, -99.1013],
    'Nayarit': [21.5085, -104.895],
    'NuevoLeon': [25.6714, -100.309],
    'Oaxaca': [17.0732, -96.7266],
    'Puebla': [19.0414, -98.2063],
    'Queretaro': [20.5972, -100.387],
    'QuintanaRoo': [21.1631, -86.8023],
    'SanLuisPotosi': [22.1565, -100.9855],
    'Sinaloa': [24.8091, -107.394],
    'Sonora': [29.0729, -110.9559],
    'Tabasco': [17.9892, -92.9475],
    'Tamaulipas': [25.4348, -99.134],
    'Tlaxcala': [19.3181, -98.2375],
    'Veracruz': [19.1738, -96.1342],
    'Yucatan': [20.967, -89.6237],
    'Zacatecas': [22.7709, -102.5833],
    'Daxthi': [20.09734637749006, -99.5268997387667],
    'Daxthi2': [20.0980488171483, -99.52525374100031]
}

# Distancia Manhattan
def calcular_distancia(coord1, coord2):
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

# Grafo para Dijkstra
grafo = {ciudad: {} for ciudad in coord}
for ciudad1 in coord:
    for ciudad2 in coord:
        if ciudad1 != ciudad2:
            distancia = calcular_distancia(coord[ciudad1], coord[ciudad2])
            grafo[ciudad1][ciudad2] = distancia

# Algoritmo de Dijkstra
def dijkstra(grafo, origen, destino):
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[origen] = 0
    predecesores = {nodo: None for nodo in grafo}
    nodos_no_visitados = set(grafo)

    while nodos_no_visitados:
        nodo_actual = min(nodos_no_visitados, key=lambda nodo: distancias[nodo])

        if distancias[nodo_actual] == float('inf'):
            break

        for vecino, peso in grafo[nodo_actual].items():
            nueva_distancia = distancias[nodo_actual] + peso
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                predecesores[vecino] = nodo_actual

        nodos_no_visitados.remove(nodo_actual)

    camino = []
    paso_actual = destino
    while paso_actual is not None:
        camino.insert(0, paso_actual)
        paso_actual = predecesores[paso_actual]

    if distancias[destino] == float('inf'):
        return "No hay camino disponible", []

    return camino, distancias[destino]

# Funciones TSP con Tabu Search
def generar_vecino(ruta):
    i, j = random.sample(range(len(ruta)), 2)
    vecino = ruta[:]
    vecino[i], vecino[j] = vecino[j], vecino[i]
    return vecino

def costo_total(ruta, coord):
    return sum(calcular_distancia(coord[ruta[i]], coord[ruta[i + 1]]) for i in range(len(ruta) - 1)) + calcular_distancia(coord[ruta[-1]], coord[ruta[0]])

def tsp_tabu_search(ciudades, coord, iteraciones=100, tamaño_tabu=50):
    ruta_actual = ciudades[:]
    random.shuffle(ruta_actual)
    mejor_ruta = ruta_actual[:]
    mejor_costo = costo_total(mejor_ruta, coord)
    lista_tabu = []

    for _ in range(iteraciones):
        vecinos = [generar_vecino(ruta_actual) for _ in range(100)]
        vecinos = [v for v in vecinos if v not in lista_tabu]

        if not vecinos:
            continue

        vecino_elegido = min(vecinos, key=lambda ruta: costo_total(ruta, coord))
        costo_vecino = costo_total(vecino_elegido, coord)

        if costo_vecino < mejor_costo:
            mejor_ruta = vecino_elegido[:]
            mejor_costo = costo_vecino

        ruta_actual = vecino_elegido
        lista_tabu.append(vecino_elegido)
        if len(lista_tabu) > tamaño_tabu:
            lista_tabu.pop(0)

    return mejor_ruta, mejor_costo

# Rutas Flask
@app.route('/')
def index():
    return render_template('index.html', ciudades=coord.keys())

@app.route('/get_routes', methods=['POST'])
def get_routes():
    data = request.get_json()
    origen = data.get('origen')
    destino = data.get('destino')

    if not origen or not destino:
        return jsonify({'error': 'Faltan coordenadas'}), 400

    origen_coord = tuple(origen)  # [lat, lng]
    destino_coord = tuple(destino)

    # Aquí usas Dijkstra o simplemente calculas distancia Manhattan
    distancia = calcular_distancia(origen_coord, destino_coord)
    coordenadas_ruta = [origen_coord, destino_coord]

    return jsonify({
        'camino': "Punto A -> Punto B",
        'coordenadas_ruta': coordenadas_ruta,
        'nodos_intermedios_encontrados': [],
        'distancia': distancia
    })


@app.route('/tsp_tabu', methods=['POST'])
def tsp_tabu():
    data = request.get_json()
    ciudades = data.get('ciudades', list(coord.keys()))

    if not ciudades or len(ciudades) < 3:
        return jsonify({'error': 'Se necesitan al menos 3 ciudades para TSP.'}), 400

    for ciudad in ciudades:
        if ciudad not in coord:
            return jsonify({'error': f'Ciudad no válida: {ciudad}'}), 400

    ruta, costo = tsp_tabu_search(ciudades, coord)
    coordenadas_ruta = [coord[ciudad] for ciudad in ruta]

    return jsonify({
        'ruta': " -> ".join(ruta),
        'coordenadas_ruta': coordenadas_ruta,
        'distancia_total': costo
    })

if __name__ == '__main__':
    app.run(debug=True)
