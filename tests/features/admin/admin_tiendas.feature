Feature: Administración de tiendas
  Como administrador del sitio
  Quiero gestionar el directorio de tiendas especializadas en cueca
  Para mantener actualizada la sección de tiendas

  Background:
    Given que el administrador ha iniciado sesión en el panel

  Scenario: Ver lista de tiendas en el panel admin
    When navega a la gestión de tiendas
    Then ve la página de administración de tiendas
    And ve el botón para agregar nueva tienda

  Scenario: Crear tienda con dirección física
    When navega a la gestión de tiendas
    And hace clic en nueva tienda
    And completa el formulario de tienda con nombre único y dirección física
    And envía el formulario de tienda
    Then ve un mensaje de éxito de tienda guardada
    And la nueva tienda aparece en la lista

  Scenario: Crear tienda con redes sociales
    When navega a la gestión de tiendas
    And hace clic en nueva tienda
    And completa el formulario de tienda con nombre único
    And agrega una red social de instagram a la tienda
    And envía el formulario de tienda
    Then ve un mensaje de éxito de tienda guardada

  Scenario: Crear tienda con número de contacto
    When navega a la gestión de tiendas
    And hace clic en nueva tienda
    And completa el formulario de tienda con nombre único
    And agrega un número de contacto WhatsApp
    And envía el formulario de tienda
    Then ve un mensaje de éxito de tienda guardada

  Scenario: Editar una tienda existente
    Given que existe al menos una tienda en el sistema
    When navega a la gestión de tiendas
    And hace clic en editar la primera tienda
    And modifica el nombre de la tienda
    And envía el formulario de tienda
    Then ve un mensaje de éxito de tienda actualizada

  Scenario: Eliminar una tienda
    Given que existe una tienda de prueba para eliminar
    When navega a la gestión de tiendas
    And elimina la tienda de prueba
    Then la tienda eliminada ya no aparece en la lista
