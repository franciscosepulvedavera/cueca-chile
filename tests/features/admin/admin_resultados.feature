Feature: Gestión de resultados del cuadro de honor
  Como administrador del sitio
  Quiero gestionar todas las entradas del cuadro de honor desde una vista global
  Para corregir o eliminar resultados de cualquier campeonato rápidamente

  Background:
    Given que el administrador ha iniciado sesión en el panel

  Scenario: Ver la página de gestión de resultados
    When navega a la gestión de resultados
    Then ve la tabla global de entradas del cuadro de honor
    And ve el enlace a la tabla pública de resultados

  Scenario: Ver el badge correcto para pareja más popular
    Given que existe una entrada de pareja más popular en el sistema
    When navega a la gestión de resultados
    Then ve el badge de popular con ícono de estrella

  Scenario: Ver badge correcto para cuarto lugar
    Given que existe una entrada de cuarto lugar en el sistema
    When navega a la gestión de resultados
    Then ve el badge de cuarto lugar

  Scenario: Filtrar resultados por campeonato
    Given que existen entradas de al menos dos campeonatos distintos
    When navega a la gestión de resultados
    And selecciona un campeonato en el filtro
    Then solo ve las entradas de ese campeonato

  Scenario: Filtrar resultados por año
    Given que existen entradas de al menos dos años distintos
    When navega a la gestión de resultados
    And selecciona un año en el filtro
    Then solo ve las entradas de ese año

  Scenario: Limpiar filtros activos
    Given que hay filtros activos en la gestión de resultados
    When hace clic en limpiar filtros
    Then ve todos los resultados sin filtrar

  Scenario: Editar entrada desde gestión de resultados
    Given que existe al menos una entrada en el sistema
    When navega a la gestión de resultados
    And hace clic en editar la primera entrada
    Then ve el formulario de edición del cuadro de honor
    And el formulario tiene activado el parámetro de retorno a resultados

  Scenario: Eliminar entrada desde gestión de resultados
    Given que existe una entrada de prueba para eliminar desde resultados
    When navega a la gestión de resultados
    And elimina la entrada de prueba y confirma
    Then la entrada ya no aparece en la tabla de resultados
