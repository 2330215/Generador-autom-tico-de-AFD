# Generador-automatico-de-AFD

Este proyecto implementa una aplicación gráfica capaz de:

- Validar expresiones regulares  
- Convertir ER → AFND (Construcción de Thompson)  
- Convertir AFND → AFD (Construcción por subconjuntos)  
- Minimizar un AFD (Algoritmo de particiones)  
- Ejecutar cada módulo desde un menú gráfico usando **Pygame**

Todos los procesos están basados en los fundamentos teóricos de Lenguajes Formales y Autómatas, y se integran en un sistema interactivo escrito en **Python 3**.

**Instalación**

Clona el repositorio:

git clone https://github.com/2330215/Generador-autom-tico-de-AFD.git
cd Proyecto-LyA

Instala las dependencias:

pip install -r requirements.txt


**Ejecución**
Ejecuta el menú principal:

python src/inicio.py

Desde ahí podrás acceder a:
ER → AFND → AFD
Minimización de AFD
Parser de expresiones regulares

Tecnologías utilizadas
*Python 3
*Pygame – interfaz gráfica
*pyformlang – parser de expresiones regulares
*automata-lib – minimización de DFA

**Algoritmos utilizados**

Construcción de Thompson
Construcción por subconjuntos
Minimización (table filling / particiones)
