# Generador-automatico-de-AFD

Este proyecto implementa una aplicación gráfica capaz de:

*Validar expresiones regulares  
*Convertir ER → AFND (Construcción de Thompson)  
*Convertir AFND → AFD (Construcción por subconjuntos)  
*Minimizar un AFD (Algoritmo de particiones)  
*Ejecutar cada módulo desde un menú gráfico usando **Pygame**

Todos los procesos están basados en los fundamentos teóricos de Lenguajes Formales y Autómatas, y se integran en un sistema interactivo escrito en **Python 3**.

**Instalación**

Clona el repositorio:

```bash
git clone https://github.com/2330215/Generador-autom-tico-de-AFD.git
```

Instala las dependencias:
```bash
pip install -r requirements.txt
```

**Ejecución**

Ejecuta el menú principal dentro de la carpeta del proyecto despues de clonar el repositorio:

```bash
python inicio.py
```

Desde ahí podrás acceder a 3 botones:
El rpimero es para la conversión de ER → AFND → AFD
El segundo es para el manejo de Minimización de AFD
El tercero es un Parser de expresiones regulares

**Tecnologías utilizadas**

*Python 3
*Pygame – interfaz gráfica
*pyformlang – parser de expresiones regulares
*automata-lib – minimización de DFA

**Algoritmos utilizados**

Construcción de Thompson
Construcción por subconjuntos
Minimización (table filling / particiones)

**Repositorio utilizado como referencia**

https://github.com/OJP98/py-finite-automata
