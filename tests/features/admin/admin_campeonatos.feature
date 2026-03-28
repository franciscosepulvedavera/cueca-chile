Feature: Administración de campeonatos
  Como administrador del sitio
  Quiero gestionar los campeonatos nacionales
  Para mantener actualizado el catálogo de competencias

  Background:
    Given que el administrador ha iniciado sesión en el panel

  Scenario: Ver lista de campeonatos en el panel admin
    When navega a la gestión de campeonatos
    Then ve la página de administración de campeonatos
    And ve el botón para agregar nuevo campeonato

  Scenario: Crear un campeonato nuevo exitosamente
    When navega a la gestión de campeonatos
    And hace clic en nuevo campeonato
    And completa el formulario con nombre de campeonato único
    And envía el formulario de campeonato
    Then ve un mensaje de éxito de campeonato creado
    And el nuevo campeonato aparece en la lista

  Scenario: Editar un campeonato existente
    Given que existe al menos un campeonato en el sistema
    When navega a la gestión de campeonatos
    And hace clic en editar el primer campeonato
    And modifica el nombre del campeonato
    And envía el formulario de campeonato
    Then ve un mensaje de éxito de campeonato actualizado

  Scenario: Eliminar un campeonato
    Given que existe un campeonato de prueba para eliminar
    When navega a la gestión de campeonatos
    And elimina el campeonato de prueba
    Then el campeonato eliminado ya no aparece en la lista

  Scenario: Acceso denegado a usuario no autenticado
    Given que el usuario no ha iniciado sesión
    When intenta acceder directamente al panel de campeonatos
    Then es redirigido a la página de login

  Scenario: Formulario de campeonato valida campos requeridos
    When navega a la gestión de campeonatos
    And hace clic en nuevo campeonato
    And envía el formulario de campeonato vacío
    Then ve errores de validación en el formulario
