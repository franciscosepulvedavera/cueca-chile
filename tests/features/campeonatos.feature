Feature: Campeonatos nacionales de cueca
  Como visitante del sitio
  Quiero explorar los campeonatos y sus cuadros de honor
  Para conocer los resultados históricos de la cueca chilena

  Scenario: Ver lista de campeonatos activos
    Given que un visitante anónimo accede al sitio
    When navega a la sección de campeonatos
    Then ve la página de campeonatos
    And ve el título de la sección campeonatos

  Scenario: Ver detalle de un campeonato con cuadro de honor
    Given que existe al menos un campeonato con entradas en el cuadro de honor
    When el visitante accede al detalle del campeonato
    Then ve el nombre del campeonato
    And ve la sección del cuadro de honor
    And ve los badges de posición de los ganadores

  Scenario: Filtrar cuadro de honor por año
    Given que existe al menos un campeonato con entradas en el cuadro de honor
    When el visitante accede al detalle del campeonato
    And hace clic en un año disponible en el selector de año
    Then la URL contiene el parámetro del año seleccionado
    And ve las entradas correspondientes a ese año

  Scenario: Ver íconos de redes sociales de ganadores
    Given que existe un campeonato con ganadores que tienen redes sociales
    When el visitante accede al detalle del campeonato
    Then ve los íconos de redes sociales en las filas del cuadro de honor

  Scenario: Ver región y comuna de un ganador
    Given que existe un campeonato con ganadores que tienen comuna registrada
    When el visitante accede al detalle del campeonato
    Then ve la región y comuna del ganador en la fila correspondiente

  Scenario: Ver posición especial pareja más popular
    Given que existe un campeonato con una entrada de pareja más popular
    When el visitante accede al detalle del campeonato
    Then ve el ícono de estrella para la pareja más popular
