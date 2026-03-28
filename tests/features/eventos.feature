Feature: Gestión de eventos de cueca
  Como usuario del sitio
  Quiero ver y crear eventos de cueca
  Para mantenerme informado sobre la actividad cuequera

  Scenario: Ver la página de eventos sin iniciar sesión
    Given que un visitante anónimo accede al sitio
    When navega a la sección de eventos
    Then ve la lista de eventos aprobados
    And ve el título de la sección de eventos

  Scenario: Acceder al formulario de nuevo evento requiere login
    Given que un visitante anónimo accede al sitio
    When intenta acceder directamente al formulario de nuevo evento
    Then es redirigido a la página de login
    And no puede crear el evento sin autenticarse

  Scenario: Ver formulario de nuevo evento autenticado
    Given que el administrador ya ha iniciado sesión
    When navega al formulario de nuevo evento
    Then ve el formulario con los campos requeridos
    And ve los campos título, tipo, fecha, región y descripción

  Scenario: Crear evento como administrador se publica directamente
    Given que el administrador ya ha iniciado sesión
    When crea un nuevo evento con todos los datos válidos
    Then el evento es creado exitosamente
    And ve un mensaje de confirmación de publicación

  Scenario: Ver detalle de un evento aprobado
    Given que un visitante anónimo accede al sitio
    When navega a la sección de eventos
    Then puede hacer clic en el primer evento disponible
    And ve la página de detalle con la información del evento
