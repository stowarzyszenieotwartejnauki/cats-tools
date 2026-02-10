# ABSTRACTD
Kilka narzędzi ułatwiających administację konferencją w formacie CATS (i nie tylko!).

## Instalacja
```shell
pip install -e .
```

## Konfiguracja
* Zmień nazwę `config_template.toml` na `config.toml`.
* Uzupełnij/zmodyfikuj pola w `config.toml` zgodnie z komentarzami czy nazwami pól i zmiennych.
* Następujące kolumny muszą istnieć i mieć **dokładnie** takie nazwy: email, imię, nazwisko.

## Ocena abstraktów
### Przepływ pracy
* Przed odpaleniem apki trzeba pobrać z dysku Google excela z formularza zgłoszeniowego.
* Gdzieś na dysku Google istnieje folder, w którym są pliki .txt z abstraktami przyjętymi lub w poprawie.
* Istnieje człowiek, który zajmuje się sprawdzaniem mejla, oraz aktualizowaniem zawartości .txt jeśli abstrakt odesłany do poprawy zostanie poprawiony.
* Wniosek z tego płynie, że również ten folder trzeba od czasu do czasu pobrać i wsadzić do wskazanego w `config.toml` folderu lokalnego.
* Apkę odpalamy przez `python gui.py`.

Nie ma integracji z API Google, bo jego skonfigurowanie (po stronie serwera) zajmuje IMO więcej, niż okazjonalne ręczne pobranie i wgranie tych plików/folderów na dysk.

Nie ma automatycznego parsowania mejli, bo jest za duże ryzyko, że ludzie nie wypełnią instrukcji co do formatowania mejli. Naprawianie błędów trwa dłużej, niż ręczne uwzględnianie wyjątków.

### Jak to działa
* Po odpaleniu apki dane albo synchronizują się z lokalnie przechowywanym .csv z abstraktami i ich statusami, albo takie .csv się tworzy zapełnione zgłoszeniami z formsów (przy pierwszym odpaleniu).
* Lokalne .csv różni się od forms tym, że na pewno ma unikalne nazwy kolumn oraz ma jedną dodatkową: status zgłoszenia. Poza tym, zawiera wyłącznnie zgłoszenia uczestników aktywnych. Nowe (świeżo z formsów) zgłoszenia są rozpatrywane i dodawane do .csv.
* W apce wyświetlają się tylko abstrakty, które mają status do rozpatrzenia (taki też uzyskują te, które dotychczas w ogóle w .csv nie zaistniały) oraz w poprawie.
* Abstrakt możemy ocenić i wysłać mejla z decyzją do Autora, albo pominąć i wrócić do niego później, np. po konsultacji z ekspertem. Guzik wyślij wysyła mejla, ale nie pojawi się on w wysłanych na skrzynce, bo jestem leniwą łajzą.
* Można przełączać widok pomiędzy abstraktem z formsów (czyli wersją pierwszą), a abstraktem z folderu z .txt (czyli najświeższą wersją, zakładając, że minion odpowiedzialny za kopiowanie mejli na dysk Google robi swoją robotę).

## Wysyłka mejli do uczestników
* Można odpalić przez `python gui.py -m`
* Założenia są takie:
  * Gdzieś na dysku jest co najmniej ściągnięty excel z formsów (ten sam co do abstraktów)
  * W lepszym scenariuszu jest też excel, zawierający jako ostatnią kolumnę zawierającą info o tym, czy uczestnik zapłacił (zgodnie z `config.toml`)
  * .pdf z certyfikatami nazywają się imię_nazwisko.pdf (TODO to jeszcze nie istnieje)
* Domyślnie kopia wiadomości wysyła się na adres nadawcy, można odhaczyć (znów byłem zbyt leniwy, żeby wysłane pojawiały się w skrzynce wysłanych)
