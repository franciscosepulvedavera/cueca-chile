Feature: Tabla de resultados por región
  Como visitante del sitio
  Quiero ver el conteo de lugares obtenidos por región
  Para conocer el desempeño histórico de cada región de Chile

  Scenario: Ver la tabla de resultados completa
    Given que un visitante anónimo accede al sitio
    When navega a la sección de resultados
    Then ve la tabla de resultados
    And la tabla contiene exactamente 16 filas de regiones

  Scenario: La tabla tiene todas las columnas de posición
    Given que un visitante anónimo accede al sitio
    When navega a la sección de resultados
    Then ve la columna de primer lugar
    And ve la columna de segundo lugar
    And ve la columna de tercer lugar
    And ve la columna de cuarto lugar

  Scenario: Ver las 16 regiones de Chile en orden norte-sur
    Given que un visitante anónimo accede al sitio
    When navega a la sección de resultados
    Then la primera fila corresponde a Arica y Parinacota
    And la última fila corresponde a Magallanes

  Scenario: Regiones sin resultados muestran guión
    Given que un visitante anónimo accede al sitio
    When navega a la sección de resultados
    Then las celdas sin resultados muestran el símbolo guión

  Scenario: Ver totales por región
    Given que un visitante anónimo accede al sitio
    When navega a la sección de resultados
    Then ve la columna de total en la tabla
    And los totales son consistentes con los conteos individuales
