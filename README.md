# Coding da Vinci 2017: Visualisierung jüdischen Lebens (jewish_berlin_open_data)
---

## Worum geht es?

Beim Coding da Vinci Hackathon 2017 in Berlin wurden zwei interessante Datensätze vorgestellt und verfügbar gemacht, die sich sehr gut kombinieren lassen.

Konkret geht es um das [jüdische Adressbuch von 1931](https://offenedaten.de/dataset/adressbuchdaten-des-judischen-adressbuchs-fur-grob-berlin-von-1931) und die [Kartei der Reichsvereinigung der Juden](https://codingdavinci.de/downloads/daten-2017/1230_BO_1_International-tracing-service.pdf).

Dieses Projekt will diese Daten verbinden und auf einer Berlin Karte visualisieren. So soll die soziale Struktur aufgezeigt werden, als auch der Einfluss der Deportationen.

----

## Die Datensätze

### Adressbucheinträge des Jüdischen Adressbuchs von Groß-Berlin von 1931

> Die  Zentral- und Landesbibliothek Berlin macht mit einem Digitalisat der Ausgabe 1931 des zuerst mit Ausg. 1929/30 (1929) erschienenen Adreßbuchs ein im Original nur in wenigen Bibliotheken erhaltenes Nachschlagewerk online zugänglich. Der Hauptteil verzeichnet alphabetisch mit Anschrift und Angabe des Berufes oder der Stellung ca. 71.000 Berliner Haushaltsvorstände jüdischer Konfession. Der redaktionelle Teil liefert einen Abriss zu Geschichte und Situation der jüdischen Gemeinde(n) und listet deren Organe, Synagogen und soziale Einrichtungen, jüdische Vereine, Presse sowie politische Verbände mit Namen und Adresse der jeweiligen Vorstände bzw. Ansprechpartner. 

Stand: Alle aufbereiteten Adressbucheinträge des CSVs mit Geodaten versehen. Korrektur und ergänzen der fehlenden Daten läuft.

### Kartei der Reichsvereinigung der Juden

> Ein großer Teil der Karten lässt sich einer der folgenden Teilkarteien zuordnen: Schülerkartei, Verstorbenenkartei, Emigrationskartei und Ausländerkartei. Während es sich bei den Karten der Schülerkartei i.d.R. um Registrierungen im Rahmen der Schulverwaltung handelt, sind die anderen Karten als Meldekarten zu charakterisieren, mit denen u.a. die Bezirksstellen die Zentrale der Reichsvereinigung in Berlin über Veränderungen in den Daten der Mitglieder informierte. Zusätzlich befinden sich in der Kartei vom ITS ausgestellte Karten. Es handelt sich dabei in der Mehrzahl um Querverweise auf Namen innerhalb der Kartei. Vereinzelt befinden sich darunter auch Karten, die auf entnommene Originalkarten verweisen.

Stand: Aufbereitung läuft und Planung wie am Besten eine Verknüpfung passiert.

## Optionale Datensätze

### Gedenkbuch des Bundesarchives

> [Das Gedenkbuch] enthält die Namen, persönlichen Daten und Schicksalswege der Personen, die zwischen 1933 und 1945 im Deutschen Reich lebten und aufgrund ihrer wirklichen oder vermeintlichen jüdischen Herkunft oder Religion Opfer der nationalsozialistischen Judenverfolgung wurden. Zu den Opfern werden im Gedenkbuch alle Personen gezählt, die eines verfolgungsbedingten Todes starben. Hierunter fallen v.a. Deportationsopfer, aber auch Personen die im Rahmen von Pogromen oder "Euthanasie" ermordet wurden sowie Personen, die durch Suizid starben. Derzeit enthält das Gedenkbuch mehr als 170.000 Namen

Status: Scraper wurde geschrieben um die Daten zu bekommen. Weitestgehend erfasst. Kann noch weiter aufbereitet werdenm da Inkonsistenzen.

### Melderegister von 1939

> The National Socialist government of Germany, in May of 1939, conducted a census of the nation's "non-Teutonic" peoples. Plans for this undertaking stemmed from a 1936 decision intended to identify those "ethnic subversives" who threatened Hitler's fascist state. Authority for this activity was vested with the Reichssippenamt, an historically respectable government department dating from Bismarckian times.

Status: Sraper wurde geschrieben um die Daten zu bekommen. Es gibt Lücken in den Daten, die in missing_census_data.csv enthalten ist.
Es gibt doppelte Einträge, wobei unklar ist, ob es sich um dieselbe Person handelt (und zwei Wohnungen/ Meldungen besitzt) oder zufällig eien Person mit dem selben Namen und Geburtstag ist (unwahrscheinlich).
Müsste noch besser aufbereitet werden.

### Stolpersteine

Dieser datensatz steht als CSV zur Verfügung. In Ergänzung kann so gezeigt werden, wer von den Deportierten bzw. vom Adressbuch denn schon einen Stolperstein haben.

Stand: Alle Einträge mit Geodaten versehen

----

## Die Datenbank

Die SqLite Datenbank ist zu groß um auf Github geladen zu werden. Sie kann [hier](https://cloud.urbanhistory.de/index.php/s/iCv9ebMDxf32lFu) heruntergeladen werden.
Wenn der Bokeh Directory Ansatz gewählt wird MUSS die Datenbank im data folder sein.

### Tabellen

#### adress31

Datensatz des jüdischen Adressbuches von 1931

#### census und census2

Datensatz des Minderheitencensus von 1939. Census2 hat einen index

#### census_merge

Datensatz Merge des Census mit dem Gedenkbuch

#### deportation42

Leere Tabelle (noch aus Planung)

#### its

Datensatz des ITS (Schülerkartei der Reichsvereinigung)

#### links
Links des Bundesarchivs die gescrapt werden sollten

#### memorial_book
Datensatz des Gedenkbuches

Hier ist bei der Tabelle zu beachten das Inhaftierung1, Inhaftierung2 usw (ähnlich bei Emigration oder Deportation) bedeutet das die Person zu einem anderen Ort gelangt ist (chronologisch).

#### merge census und merge_test

Test Tabellen

