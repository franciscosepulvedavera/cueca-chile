Feature: Administración de creadores de contenido
  Como administrador del sitio
  Quiero gestionar el directorio de creadores de contenido
  Para mantener actualizada la sección de creadores cuequeros

  Background:
    Given que el administrador ha iniciado sesión en el panel

  Scenario: Ver lista de creadores en el panel admin
    When navega a la gestión de creadores
    Then ve la página de administración de creadores
    And ve el botón para agregar nuevo creador

  Scenario: Crear creador con URL principal
    When navega a la gestión de creadores
    And hace clic en nuevo creador
    And completa el formulario de creador con nombre y URL principal únicos
    And envía el formulario de creador
    Then ve un mensaje de éxito de creador guardado
    And el nuevo creador aparece en la lista

  Scenario: Crear creador sin URL pero con redes sociales
    When navega a la gestión de creadores
    And hace clic en nuevo creador
    And completa el formulario de creador con nombre único sin URL
    And agrega una red social de instagram al creador
    And envía el formulario de creador
    Then ve un mensaje de éxito de creador guardado
    And el nuevo creador aparece en la lista

  Scenario: El campo URL es opcional al crear creador
    When navega a la gestión de creadores
    And hace clic en nuevo creador
    Then el campo URL no tiene el marcador de obligatorio

  Scenario: Editar un creador existente
    Given que existe al menos un creador en el sistema
    When navega a la gestión de creadores
    And hace clic en editar el primer creador
    And modifica el nombre del creador
    And envía el formulario de creador
    Then ve un mensaje de éxito de creador actualizado

  Scenario: Eliminar un creador
    Given que existe un creador de prueba para eliminar
    When navega a la gestión de creadores
    And elimina el creador de prueba
    Then el creador eliminado ya no aparece en la lista
