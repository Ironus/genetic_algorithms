#!/usr/bin/python3

'''
Modul implementujacy proces generowania ciagu
za pomoca algorytmow genetycznycnych
'''

from math import fabs
from random import choice, randint
from string import ascii_lowercase, ascii_uppercase
from time import clock


class Chromosome:
    ''' Podstawowa jednostka budujaca populacje '''

    # koszt zdania
    cost = 0
    # mozliwe znaki
    possible_chars = list(ascii_lowercase + ascii_uppercase)

    def __init__(self, sentence='', model_length=0):
        ''' Ustawienie wartosci zmiennych podanych w argumentach '''

        # zdanie, ktore przetrzymuje chromosom
        self.sentence = sentence
        # ustaw wymagana dlugosc zdania na dlugosc modelu
        self.length = model_length

        # jesli podane zdanie jest zbyt krotkie, to wylosuj dodatkowe znaki
        self.randomize()

    def randomize(self):
        ''' Randomizacja zdania '''

        # dopoki zdanie jest krotsze niz wymagane
        while len(self.sentence) < self.length:
            # wylosuj nowy znak
            new_letter = choice(self.possible_chars)
            # dodaj go do zdania
            self.sentence = self.sentence + new_letter

    def calculate_cost(self, model):
        ''' Obliczanie kosztu zdania'''

        # wyzeruj koszt
        self.cost = 0

        # dla kazdej litery w zdaniu
        for i in range(0, self.length):
            # oblicz jej koszt i dodaj do kosztu ogolnego
            self.cost = self.cost + fabs(ord(self.sentence[i]) -
                                         ord(model[i]))

    def mutate(self):
        ''' Mutowanie zdania (+/- znak), aby pchnac mutacje do przodu '''

        # wylosuj znak do zastapienia
        change_at = randint(0, len(self.sentence) - 1)

        # wydobadz indeks starego znaku z listy mozliwych znakow
        old_char_index = self.possible_chars.index(self.sentence[change_at])

        # wylosuj 0 lub 1, jesli 0
        if randint(0, 1) is 0:
            # to sprawdz czy indeks po odjeciu 1 nie bedzie ujemny
            if old_char_index - 1 < 0:
                # jesli tak, to ustaw go na koniec listy
                old_char_index = len(self.possible_chars)
            # odejmij jeden od znaku
            new_char = self.possible_chars[old_char_index - 1]
        else:
            # jesli nie, to sprawdz czy po dodaniu 1 nie wyjdzie za koniec
            if old_char_index + 1 is len(self.possible_chars):
                # jesli tak, to ustaw indeks na poczatek
                old_char_index = 0
            # dodaj jeden do znaku
            new_char = self.possible_chars[old_char_index + 1]

        # wstaw nowy znak
        sentence_list = list(self.sentence)
        sentence_list[change_at] = new_char
        self.sentence = str().join(sentence_list)

    def get_cost(self):
        ''' Zwrocenie kosztu '''

        return self.cost

    def get_sentence(self):
        ''' Zwrocenie zdania '''

        return self.sentence

    def display(self):
        ''' Wydruk parametrow '''

        print('{} [{}]'.format(self.sentence, int(self.cost)))


class Population:
    ''' Zbior stworzony z chromosomow '''

    # licznik generacji
    generation = 1

    def __init__(self, model='', members=None, population_size=10,
                 mutation_chance=50):
        ''' Ustawienie wartosci zmiennych podanych w argumentach '''

        # ustaw model
        self.model = model
        # ustaw liste chromosomow jesli zostala jakas podana
        if members is not None:
            self.members = members
        # jesli nie, to ustaw pusta liste
        else:
            self.members = []
        # ustaw wielkosc populacji
        self.population_size = population_size
        # ustaw szanse na mutacje
        self.mutation_chance = mutation_chance

        # jesli lista chromosomow podana w argumentach jest zbyt krotka
        if (self.members is None or
                len(self.members) is not self.population_size):
            # wywolaj tworzenie chromosomow
            self.create_chromosomes()

    def create_chromosomes(self):
        ''' Uzupelnianie listy czlonkow nowymi chromosomami'''

        # dopoki lista nie spelnia wymogu wielkosci
        while len(self.members) is not self.population_size:
            # stworz nowy chromosom
            new_member = Chromosome(model_length=len(self.model))
            # dodaj go do listy
            self.members.append(new_member)

    def sort_members(self):
        ''' Sortuje liste chromosomow w miejscu '''

        # sortowanie rosnaco po koszcie
        self.members.sort(key=lambda chromosome: chromosome.cost)

    def generate(self):
        ''' Generuje populacje najblizsza wzorcowi '''

        # dla kazdego z chromosomow
        for chromosome in self.members:
            # oblicz jego koszt w porownaniu do wzorca
            chromosome.calculate_cost(self.model)

        # posortuj liste
        self.sort_members()

        # skrzyzuj dwoch najlepszych kandydatow
        first_child, second_child = self.crossover(self.members[0],
                                                   self.members[1])

        # zastap najslabszych (ostatnich) kandydatow nowym potomstwem
        self.members[self.population_size - 2] = first_child
        self.members[self.population_size - 1] = second_child

        # oblicz koszt dla nowego potomstwa
        self.members[self.population_size - 2].calculate_cost(self.model)
        self.members[self.population_size - 1].calculate_cost(self.model)

        # dla kazdego chromosomu z listy
        for chromosome in self.members:
            # jesli wylosowano mutacje
            if randint(1, 100) < self.mutation_chance:
                # wywolaj mutacje
                chromosome.mutate()
                # oblicz nowy koszt
                chromosome.calculate_cost(self.model)

        # posortuj liste ponownie
        self.sort_members()

        # sprawdz czy dopasowano do wzorca
        print('Najlepiej dopasowany:', end='')
        self.members[0].display()

        if int(self.members[0].get_cost()) is 0:
            # jesli tak, to wyswietl
            return self.members[0]
        else:
            # jesli nie, to zwieksz licznik generacji i wywolaj ponownie
            self.generation = self.generation + 1
            return None

    def crossover(self, first_parent, second_parent):
        ''' Krzyzuje dwa podane chromosomy dajac dwojke potomstwa '''

        # pobierz dlugosc modelu
        model_length = len(self.model)

        # wylicz miejsce podzialu
        pivot = int(model_length / 2)

        # pobierz od rodzicow zdania
        first_parent_sentence = first_parent.get_sentence()
        second_parent_sentence = second_parent.get_sentence()

        # stworz pierwsze dziecko
        sentence = first_parent_sentence[:pivot] + \
            second_parent_sentence[pivot:]
        first_child = Chromosome(sentence=sentence,
                                 model_length=model_length)

        # stworz drugie dziecko
        sentence = first_parent_sentence[pivot:] + \
            second_parent_sentence[:pivot]
        second_child = Chromosome(sentence=sentence,
                                  model_length=model_length)

        return first_child, second_child

    def show(self):
        ''' Wydruk wszystkich chromosomow w populacji '''
        for chromosome in self.members:
            chromosome.display()

    def get_generation_number(self):
        ''' Zwrocenie numeru generacji '''
        return self.generation


def main():
    ''' Punkt startu '''

    # sprawdz zegar #1
    start = clock()

    # utworz populacje
    population = Population(model='HelloWorld',
                            mutation_chance=50,
                            population_size=10)
    # utworz chromosom do przechowania wyniku
    final_chromosome = None

    # dopoki nie zwroci poprawnego wyniku
    while final_chromosome is None:
        # wywoluj generowanie kolejnych populacji
        final_chromosome = population.generate()

    # sprawdz zegar #2
    end = clock()

    # wyswietl wynik
    print('Generacja: {}'.format(population.get_generation_number()))

    print('Czas dzialania: {} sekund'.format(end - start))

if __name__ == '__main__':
    main()
