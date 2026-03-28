Feature: Administración del cuadro de honor
  Como administrador del sitio
  Quiero gestionar las entradas del cuadro de honor de cada campeonato
  Para registrar los resultados históricos con precisión

  Background:
    Given que el administrador ha iniciado sesión en el panel
    And existe al menos un campeonato en el sistema

  Scenario: Agregar entrada de primer lugar al cuadro de honor
    When navega al detalle del primer campeonato
    And hace clic en agregar entrada al cuadro de honor
    And completa el formulario con año, categoría, pareja y primer lugar
    And selecciona una región
    And envía el formulario de honor
    Then ve un mensaje de éxito de entrada agregada
    And la nueva entrada aparece en el cuadro de honor

  Scenario: Agregar pareja más popular como reconocimiento especial
    When navega al detalle del primer campeonato
    And hace clic en agregar entrada al cuadro de honor
    And completa el formulario seleccionando pareja más popular
    And envía el formulario de honor
    Then ve un mensaje de éxito de entrada agregada
    And la entrada aparece con el ícono de estrella

  Scenario: Agregar entrada de cuarto lugar
    When navega al detalle del primer campeonato
    And hace clic en agregar entrada al cuadro de honor
    And completa el formulario seleccionando cuarto lugar
    And envía el formulario de honor
    Then ve un mensaje de éxito de entrada agregada

  Scenario: Agregar entrada con redes sociales de la pareja
    When navega al detalle del primer campeonato
    And hace clic en agregar entrada al cuadro de honor
    And completa el formulario básico de honor
    And agrega una red social de tipo instagram a la pareja
    And envía el formulario de honor
    Then la entrada aparece con ícono de red social

  Scenario: Agregar entrada con comuna
    When navega al detalle del primer campeonato
    And hace clic en agregar entrada al cuadro de honor
    And completa el formulario básico de honor
    And rellena el campo de comuna
    And envía el formulario de honor
    Then la entrada muestra la región y la comuna

  Scenario: Editar una entrada del cuadro de honor
    Given que existe una entrada en el cuadro de honor
    When hace clic en editar la primera entrada
    And modifica el nombre de la pareja
    And envía el formulario de honor
    Then ve un mensaje de éxito de entrada actualizada

  Scenario: Eliminar una entrada del cuadro de honor
    Given que existe una entrada en el cuadro de honor
    When hace clic en eliminar la primera entrada y confirma
    Then la entrada ya no aparece en el cuadro de honor
