// Definición de pines para el puente H
const int N1 = 10; // Pin 4
const int N2 = 5; // Pin 5
const int N3 = 6; // Pin 6
const int N4 = 11; // Pin 7

// Definición de pines para el sensor ultrasónico
const int TRIG_PIN = 9; 
const int ECHO_PIN = 3; 
// Constantes
const float VELOCIDAD_SONIDO = 0.034; // cm/μs

// Configuración inicial
void setup() {
  // Inicializar pines del puente H como salidas
  pinMode(N1, OUTPUT);
  pinMode(N2, OUTPUT);
  pinMode(N3, OUTPUT);
  pinMode(N4, OUTPUT);
  
  // Inicializar pines del sensor ultrasónico
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Iniciar comunicación serial a 9600 baudios
  Serial.begin(9600);
  Serial.println("Arduino listo y esperando comandos...");
  
  // Detener ambos motores al inicio para seguridad
  stopMotors();
}

// Bucle principal
void loop() {
  // Medir distancia
  float distance = medirDistancia();
  
  // Enviar distancia al notebook
  if (distance != INFINITY) {
    Serial.print("DIST:");
    Serial.println(distance);
  } else {
    Serial.println("DIST:INF");
  }
  
  // Verificar si hay comandos disponibles en el buffer serial
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Eliminar espacios en blanco y caracteres de nueva línea
    
    // Ejecutar comando
    if (command.equalsIgnoreCase("FORWARD")) {
      forward();
    }
    else if (command.equalsIgnoreCase("BACKWARD")) {
      backward();
    }
    else if (command.equalsIgnoreCase("TURN_LEFT")) {
      turnLeft();
    }
    else if (command.equalsIgnoreCase("TURN_RIGHT")) {
      turnRight();
    }
    else if (command.equalsIgnoreCase("STOP")) {
      stopMotors();
    }
    else {
      Serial.println("Comando desconocido: " + command);
    }
  }
  
  delay(100); // Pausa para evitar sobrecargar la CPU
}

// Función para medir la distancia usando el sensor ultrasónico
float medirDistancia() {
  // Asegurarse de que el TRIG esté en bajo
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // Enviar pulso ultrasónico de 10 microsegundos
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Medir el tiempo del pulso
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // Timeout de 30ms
  
  // Calcular la distancia en centímetros
  if (duration == 0) {
    return INFINITY; // Indicar que no se recibió eco
  }
  
  float dist = duration * VELOCIDAD_SONIDO / 2; // Dividir por 2 para ida y vuelta
  return dist;
}

// Funciones para controlar los motores
void forward() {
  // Ambos motores hacia adelante
  digitalWrite(N1, LOW);
  digitalWrite(N2, HIGH);
  digitalWrite(N3, LOW);
  digitalWrite(N4, HIGH);
  Serial.println("Comando recibido: FORWARD");
}

void backward() {
  // Ambos motores hacia atrás
  digitalWrite(N1, HIGH);
  digitalWrite(N2, LOW);
  digitalWrite(N3, HIGH);
  digitalWrite(N4, LOW);
  Serial.println("Comando recibido: BACKWARD");
}

void turnLeft() {
  // Motor Izquierdo hacia atrás, Motor Derecho hacia adelante
  digitalWrite(N1, HIGH);
  digitalWrite(N2, LOW);
  digitalWrite(N3, LOW);
  digitalWrite(N4, HIGH);
  Serial.println("Comando recibido: TURN_LEFT");
}

void turnRight() {
  // Motor Izquierdo hacia adelante, Motor Derecho hacia atrás
  digitalWrite(N1, LOW);
  digitalWrite(N2, HIGH);
  digitalWrite(N3, HIGH);
  digitalWrite(N4, LOW);
  Serial.println("Comando recibido: TURN_RIGHT");
}

void stopMotors() {
  // Ambos motores detenidos
  digitalWrite(N1, LOW);
  digitalWrite(N2, LOW);
  digitalWrite(N3, LOW);
  digitalWrite(N4, LOW);
  Serial.println("Comando recibido: STOP");
}