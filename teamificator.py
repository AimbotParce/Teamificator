import itertools
from typing import Callable, Generator, Iterable

import numpy as np
from tabulate import tabulate


class Blocker:
    def __init__(self, initial: bool = False) -> None:
        self.state = initial

    def block(self, state: bool) -> Callable:
        """
        Decorator to block changes. Only permits a function to be called if self.state equals to the argument state.
        """

        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                if self.state == state:
                    return func(*args, **kwargs)
                else:
                    raise RuntimeError("Function %s is blocked by now" % func.__name__)

            return wrapper

        return decorator


blocker = Blocker()


class People:
    def __init__(self, people: list[str] = []) -> None:
        self.people = set(people)
        self.pairs = set()
        self.avoids = set()

    @blocker.block(False)
    def add(self, person: str) -> None:
        self.people.add(person)

    @blocker.block(False)
    def remove(self, person: str) -> None:
        self.check(person)
        self.people.remove(person)
        for pair in self.pairs:
            if person in pair:
                self.pairs.remove(pair)
        for avoid in self.avoids:
            if person in avoid:
                self.avoids.remove(avoid)

    @blocker.block(False)
    def check(self, person: str) -> bool:
        if not isinstance(person, str):
            raise TypeError("Invalid type")
        if not person in self.people:
            raise ValueError("Person %s not found" % person)

    @blocker.block(False)
    def pair(self, a: str, b: str) -> None:
        self.check(a)
        self.check(b)
        if a == b:
            raise ValueError("Cannot pair %s with %s" % (a, b))
        for pair in self.pairs:
            if a in pair and b in pair:
                raise ValueError("Pair %s and %s already exists" % (a, b))
        for avoid in self.avoids:
            if a in avoid and b in avoid:
                raise ValueError("%s and %s are avoiding" % (a, b))
        self.pairs.add((a, b))

    @blocker.block(False)
    def separate(self, a: str, b: str) -> None:
        self.check(a)
        self.check(b)
        for pair in self.pairs:
            if a in pair and b in pair:
                self.pairs.remove(pair)
                return
        raise ValueError("Pair %s and %s not found" % (a, b))

    @blocker.block(False)
    def avoid(self, a: str, b: str) -> None:
        self.check(a)
        self.check(b)
        if a == b:
            raise ValueError("Cannot avoid %s and %s" % (a, b))
        for avoid in self.avoids:
            if a in avoid and b in avoid:
                raise ValueError("Avoid %s and %s already exists" % (a, b))
        for pair in self.pairs:
            if a in pair and b in pair:
                raise ValueError("%s and %s are a pair" % (a, b))
        self.avoids.add((a, b))

    @blocker.block(False)
    def unavoid(self, a: str, b: str) -> None:
        self.check(a)
        self.check(b)
        for avoid in self.avoids:
            if a in avoid and b in avoid:
                self.avoids.remove(avoid)
                return
        raise ValueError("Avoid %s and %s not found" % (a, b))

    @blocker.block(False)
    def commit(self) -> None:
        """
        Commit changes. No more changes can be made after this.
        """
        blocker.state = True
        self.people = list(self.people)
        self.pairs = self.__indexLinks(self.pairs)
        self.avoids = self.__indexLinks(self.avoids)

    @blocker.block(True)
    def __indexLinks(self, links: set[set[int]]) -> list[tuple[int]]:
        return [(self.people.index(a), self.people.index(b)) for a, b in links]

    @blocker.block(True)
    def person(self, id: int | list[int] | tuple[int]) -> str:
        if isinstance(id, int):
            return self.people[id]
        elif isinstance(id, list):
            return [self.person(i) for i in id]
        elif isinstance(id, tuple):
            return tuple(self.person(i) for i in id)
        else:
            raise TypeError("Invalid type")

    @blocker.block(True)
    def teamOptions(self, n: int) -> list[tuple[tuple[int]]]:
        """
        Get team options for n teams.
        """
        if n < 2:
            raise ValueError("n must be greater than 1")
        if n > len(self.people):
            raise ValueError("n must be less than the number of people")

        perTeam = len(self.people) // n

        def getOtherTeam(team: tuple[int]) -> tuple[int]:
            return tuple(set(range(len(self.people))) - set(team))

        def getBothTeams(team: tuple[int]) -> tuple[tuple[int]]:
            return (team, getOtherTeam(team))

        teamA = itertools.combinations(range(len(self.people)), perTeam)
        teamB = map(getBothTeams, teamA)
        return list(teamB)

    @blocker.block(True)
    def isTeamOk(self, team: list[int]) -> bool:
        for a, b in self.pairs:
            if a in team and b not in team:
                return False
            if a not in team and b in team:
                return False
        for a, b in self.avoids:
            if a in team and b in team:
                return False
        return True

    @blocker.block(True)
    def areTeamsOk(self, teams: Iterable[list[int]]) -> bool:
        return all(self.isTeamOk(team) for team in teams)

    @blocker.block(True)
    def getPossibleTeams(self, n: int = 2) -> list[tuple[str]]:
        """
        Teamificator algorithm:

        Separate the people in n groups of roughly the same size.

        Return all team options.
        """

        options: list[tuple[tuple[int]]] = self.teamOptions(n)
        options = list(filter(self.areTeamsOk, options))
        if len(options) == 0:
            raise ValueError("No possible teams found")
        return options


def tablifyOptions(options: list[tuple[tuple[str]]]) -> str:
    matrix = []
    teams = len(options[0])
    for i, option in enumerate(options):
        matrix.append([])
        for j in range(teams):
            txt = ", ".join(option[j])
            matrix[i].append(txt)
    return tabulate(matrix, headers=[f"Team {i+1}" for i in range(teams)])


if __name__ == "__main__":
    people = People()
    people.add("Marc")
    people.add("Arón")
    people.add("Ferran")
    people.add("Andrea")
    people.add("Jordi")
    people.add("Berta")
    people.add("Roger")
    people.add("Anna")
    people.add("Enrique")
    people.add("Jan")
    people.add("Iris")

    people.pair("Ferran", "Andrea")
    people.pair("Jordi", "Berta")

    people.avoid("Roger", "Ferran")
    people.avoid("Arón", "Jordi")

    people.commit()

    possible = people.getPossibleTeams(2)
    possible = people.person(possible)
    print("Options for 2 teams:")
    print(tablifyOptions(possible))
    print()
    option = np.random.randint(len(possible))
    print("Random option:")
    print(tablifyOptions([possible[option]]))
