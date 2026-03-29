# features/admin/admin_musicos.feature
Feature: Administración de Músicos
  Como administrador
  Quiero gestionar músicos y agrupaciones
  Para que aparezcan en la sección pública de músicos

  Background:
    Given que el administrador está autenticado

  @admin
  Scenario: Ver lista de músicos en el panel
    When navego a la lista de músicos en admin
    Then veo la página de administración de músicos

  @admin
  Scenario: Crear un músico solo con nombre
    When navego a crear un nuevo músico
    And completo el nombre del músico con un valor único
    And guardo el formulario de músico
    Then veo el músico creado en la lista

  @admin
  Scenario: Crear músico con descripción
    When navego a crear un nuevo músico
    And completo el nombre del músico con un valor único
    And completo la descripción del músico
    And guardo el formulario de músico
    Then veo el músico creado en la lista

  @admin
  Scenario: Editar un músico existente
    Given que existe al menos un músico en el sistema
    When edito el primer músico de la lista
    And cambio el nombre del músico
    And guardo el formulario de músico
    Then veo el nombre actualizado en la lista

  @admin
  Scenario: Eliminar un músico
    Given que existe al menos un músico en el sistema
    When elimino el primer músico de la lista
    Then el músico ya no aparece en la lista

  @admin
  Scenario: Acceso denegado a no administradores
    Given que el usuario no está autenticado
    When intento acceder a la lista de músicos en admin
    Then soy redirigido al login
