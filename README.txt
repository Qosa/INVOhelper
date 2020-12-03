ŚCIEŻKI DOSTĘPU

-----------========== PRZEDMIOTY:
Dwie kategorie - PRZEDMIOTY oraz WYSTĄPIENIA PRZEDMIOTÓW. Przykład: ławka szkolna jest typem przedmiotu(przedmiotem), natomiast wystąpienie przedmiotu jest jego konkretnym przykładem(np. ławka szkolna w klasie nr. 21) 

lista przedmiotow: https://invohelper.herokuapp.com/items/
szczegółowy opis przedmiotu: np. https://invohelper.herokuapp.com/items/1/details
opis wystąpienia przedmiotu: np. https://invohelper.herokuapp.com/items/occurence/1/details (póki co nie działa na heroku - do modyfikacji ścieżki dostępu do kodów kreskowych)
dodanie przedmiotu: https://invohelper.herokuapp.com/items/add
edycja przedmiotu: np. https://invohelper.herokuapp.com/items/1/edit/
dodanie wystąpienia przedmiotu: np. https://invohelper.herokuapp.com/items/1/occurrence/add
edycja wystąpienia przedmiotu: np. https://invohelper.herokuapp.com/items/occurrence/1/edit/

-----------========== INWENTARYZACJE:
dodanie inwentaryzacji: https://invohelper.herokuapp.com/invent/creator
lista inwentaryzacji: https://invohelper.herokuapp.com/invent/list
szczegóły inwentaryzacji: np. https://invohelper.herokuapp.com/invent/1/details
harmonogram inwentaryzacji: np. https://invohelper.herokuapp.com/invent/1/schedule?y=2020&m=11
dodanie zadania do harmonogramu: np. https://invohelper.herokuapp.com/invent/1/schedule/addtask/

-----------========== POZOSTAŁE LINKI:
github - https://github.com/Qosa/INVOhelper - tutaj macie na bieżąco uzupełniane repozytorium kodu aplikacji
schemat bazy danych - https://github.com/Qosa/INVOhelper/blob/master/app/models.py - obiektowa wersja bazy, wszystkie tablice, pola i relacje pomiędzy tablicami są ładnie widoczne

Istnieje możliwość podłączenia się do bazy przez np. pgAdmin :
host: ec2-52-31-94-195.eu-west-1.compute.amazonaws.com
nazwa bazy: d5tl0po5fk7fpd
użytkownik: rmuwodwxizvomv
port: 5432
hasło: 68d9a2ed7cb3bdf90df6e084fb709a4468597c1a875b7b91917c4f2560758fdb
URI: postgres://rmuwodwxizvomv:68d9a2ed7cb3bdf90df6e084fb709a4468597c1a875b7b91917c4f2560758fdb@ec2-52-31-94-195.eu-west-1.compute.amazonaws.com:5432/d5tl0po5fk7fpd

planer plac programistycznych (aktualizowany na bieżąco):
https://trello.com/b/CzUIUWbi/invohelper