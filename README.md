# Reseptit
## Reseptikirjasovellukset vaatimattomat suunnitelmat:
- Sovelluksessa käyttäjät pystyvät jakamaan ruokareseptejään. Reseptissä lukee tarvittavat ainekset ja valmistusohje.
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään reseptejä ja muokkaamaan ja poistamaan niitä.
- Käyttäjä näkee sovellukseen lisätyt reseptit.
- Käyttäjä pystyy etsimään reseptejä hakusanalla.
- Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt ja listan käyttäjän lisäämistä resepteistä. (Toteuttamatta)
- Käyttäjä pystyy valitsemaan esimerkiksi seuraavia luokitteluja:
  - Ruoan tyyppi: alkuruoka, pääruoka tai jälkiruoka
  - Ruokavalio: laktoositon, gluteeniton tai vegaaninen
- Käyttäjä pystyy antamaan reseptille kommentin ja arvosanan. Reseptistä näytetään kommentit ja keskimääräinen arvosana.


## Kommentteja
- Python-versio: 3.14.0
- OS: Windows 11

## Sovelluksen toiminta
- Lataa tiedostot.
- Luo sovellukseen tietokanta.
  - Windows 11:ssa mene kansioon ja suorita: sqlite3 database.db ".read schema.sql"
- Käynnistä sovellus ja saatu linkki selaimeen, jonka jälkeen voit luoda käyttäjän, kirjautua, lisätä reseptejä, hakea resepetejä sekä poistaa niitä.
  - Kukin käyttäjä voi hallinoida vain omia reseptejään. Tällä hetkellä reseptit ovat kaikkien käyttäjien nähtävissä.