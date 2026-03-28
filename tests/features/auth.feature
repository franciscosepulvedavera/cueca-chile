Feature: Autenticación de usuarios
  Como visitante del sitio
  Quiero poder registrarme e iniciar sesión
  Para acceder a las funcionalidades según mi rol

  # ── Login ────────────────────────────────────────────────────────────────────

  Scenario: Login exitoso como administrador
    Given que el usuario navega a la página de login
    When ingresa credenciales de administrador válidas
    Then es redirigido a la página principal
    And ve el menú de administrador en la barra de navegación

  Scenario: Login fallido con contraseña incorrecta
    Given que el usuario navega a la página de login
    When ingresa el email del admin con una contraseña incorrecta
    Then permanece en la página de login
    And ve un mensaje de error de autenticación

  Scenario: Login fallido con email inexistente
    Given que el usuario navega a la página de login
    When ingresa un email que no existe en el sistema
    Then permanece en la página de login
    And ve un mensaje de error de autenticación

  # ── Registro ─────────────────────────────────────────────────────────────────

  Scenario: Registro exitoso de nuevo usuario
    Given que el usuario navega a la página de registro
    When completa el formulario de registro con datos válidos y email único
    Then es redirigido a la página principal tras el registro
    And ve el nombre del usuario en la barra de navegación

  Scenario: Registro fallido con email ya registrado
    Given que el usuario navega a la página de registro
    When intenta registrarse con el email del administrador ya existente
    Then permanece en la página de registro
    And ve un mensaje de error de email duplicado

  # ── Logout ───────────────────────────────────────────────────────────────────

  Scenario: Logout exitoso
    Given que el administrador ya ha iniciado sesión
    When hace clic en cerrar sesión
    Then es redirigido a la página de login o inicio
    And no ve el menú de administrador
