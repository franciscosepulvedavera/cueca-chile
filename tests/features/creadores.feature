Feature: Directorio de creadores de contenido
  Como visitante del sitio
  Quiero explorar los creadores de contenido de cueca
  Para encontrar canales y cuentas que difunden la cueca chilena

  Scenario: Ver directorio de creadores
    Given que un visitante anónimo accede al sitio
    When navega a la sección de creadores
    Then ve la página del directorio de creadores
    And ve el título de la sección creadores

  Scenario: Ver tarjeta de creador con URL principal
    Given que existe un creador con URL principal registrada
    When el visitante navega a la sección de creadores
    Then ve el botón visitar en la tarjeta del creador con URL

  Scenario: Ver tarjeta de creador con redes sociales sin URL principal
    Given que existe un creador sin URL pero con redes sociales
    When el visitante navega a la sección de creadores
    Then ve los botones de redes sociales en la tarjeta del creador

  Scenario: Ver nombre y descripción de un creador
    Given que existe al menos un creador activo
    When el visitante navega a la sección de creadores
    Then ve el nombre del creador en su tarjeta
    And ve la descripción del creador si tiene una

  Scenario: Creadores inactivos no aparecen en el directorio público
    Given que existe un creador marcado como inactivo
    When el visitante navega a la sección de creadores
    Then ese creador no aparece en el directorio público
