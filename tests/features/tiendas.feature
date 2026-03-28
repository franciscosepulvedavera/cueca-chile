Feature: Directorio de tiendas de cueca
  Como visitante del sitio
  Quiero explorar las tiendas especializadas en cueca
  Para encontrar dónde comprar indumentaria y accesorios

  Scenario: Ver directorio de tiendas
    Given que un visitante anónimo accede al sitio
    When navega a la sección de tiendas
    Then ve la página del directorio de tiendas
    And ve el título de la sección tiendas

  Scenario: Ver tienda con sitio web
    Given que existe una tienda con sitio web registrado
    When el visitante navega a la sección de tiendas
    Then ve el enlace al sitio web de la tienda

  Scenario: Ver tienda con dirección física
    Given que existe una tienda con dirección física registrada
    When el visitante navega a la sección de tiendas
    Then ve la dirección física de la tienda en su tarjeta

  Scenario: Ver tienda con redes sociales
    Given que existe una tienda con redes sociales registradas
    When el visitante navega a la sección de tiendas
    Then ve los iconos de redes sociales en la tarjeta de la tienda

  Scenario: Tiendas inactivas no aparecen en el directorio público
    Given que existe una tienda marcada como inactiva
    When el visitante navega a la sección de tiendas
    Then esa tienda no aparece en el directorio público
