## Robot Recolector de Basura con IoT y Vision Artificial

Este repositorio contiene el código fuente de un proyecto de IoT que implementa un automóvil autónomo diseñado para recolectar basura (específicamente plásticos) utilizando visión por computador y control de hardware. El sistema está basado en **Raspberry Pi 4** y **Arduino**, e integra dos motores para el movimiento y una cámara para la detección de basura.

### Características principales
- **Detección de basura**: Implementa un modelo entrenado con **YOLO** (You Only Look Once) para identificar residuos plásticos en tiempo real.
- **Movimiento inteligente**: El automóvil se mueve hacia los residuos detectados, utilizando dos motores controlados por un código en Python y Arduino.
- **Integración de hardware**: 
  - La **Raspberry Pi 4** gestiona la visión artificial, el procesamiento del modelo YOLO y envía instrucciones al Arduino.
  - El **Arduino** controla los motores y otros componentes a través de un código en **C++**.
- **Control de colisiones**: Uso de sensores ultrasónicos para evitar obstáculos mientras el automóvil se desplaza.

### Tecnologías utilizadas
- **Python**: Para el desarrollo del modelo de detección de objetos, el control del movimiento y la comunicación con el Arduino.
- **YOLO**: Para el entrenamiento y la detección de residuos plásticos.
- **C++**: Para la programación del Arduino, que ejecuta las instrucciones enviadas por la Raspberry Pi.
- **Hardware**:
  - **Raspberry Pi 4**: Procesamiento principal y control de visión.
  - **Arduino**: Gestión de motores y comunicación con la Raspberry Pi.
  - **Motores**: Dos motores para el movimiento del automóvil.
  - **Cámara**: Detección de basura en tiempo real.
  - **Sensor ultrasónico**: Prevención de colisiones.

### Uso del repositorio
Este repositorio incluye:
- Código en Python para la detección de objetos y control del automóvil.
- Código en C++ para el manejo de motores y la comunicación con el hardware.
- Instrucciones para entrenar el modelo YOLO y configurar el sistema.

### Aplicaciones
El proyecto puede ser extendido para:
- Recolección automatizada de residuos en áreas específicas.
- Implementación en sistemas de limpieza inteligentes.
- Aprendizaje práctico de IoT, visión artificial y control de hardware.

### Integrantes
- Bastián Rojas
- Cristian Soto
