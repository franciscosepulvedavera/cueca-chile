# features/musicos.feature
Feature: Vista pública de Músicos
  Como visitante del sitio
  Quiero ver el directorio de músicos
  Para conocer músicos y agrupaciones de cueca

  @publico
  Scenario: Ver la página de músicos
    Given que soy un visitante anónimo
    When navego a la sección de músicos
    Then veo la página de músicos con el título correcto

  @publico
  Scenario: Ver músico en el directorio
    Given que existe al menos un músico activo
    When navego a la sección de músicos
    Then veo al menos un músico en la página
