## People Manager Class
The People class is a utility for managing a group of people and their relationships.

### Initialization
To create a new instance of the People class, you can pass in an optional list of people to include in the group:
```python
people = People(["Alice", "Bob", "Dave"])
```
If no list is provided, an empty group will be created:
```python
people = People()
```
### People managing methods
`add(person: str) -> None`
Adds a new person to the group.
```python
people.add("Charlie")
```

`remove(person: str) -> None`
Removes a person from the group.
```python
people.remove("Dave")
```

`pair(person1: str, person2: str) -> None`
Adds a pair of people who will be in the same team.
```python
people.pair("Alice", "Bob")
```

`separate(person1: str, person2: str) -> None`
Removes a pair of people who will no longer be in the same team.
```python
people.separate("Alice", "Bob")
```

`avoid(person1: str, person2: str) -> None`
Adds a pair of people who must not be in the same team.
```python
people.avoid("Alice", "Charlie")
```

`unavoid(person1: str, person2: str) -> None`
Removes a pair of people who no longer must not be in the same team.
```python
people.unavoid("Alice", "Charlie")
```

### Commiting

`commit() -> None`
Commits the current state of the group. No more people can be added or removed after this method is called, and no more pairs or avoids can be added or removed.
```python
people.commit()
```
After this method is called, all the persons in the group are given a unique id. Given an id, you can get the person's name with the [person]() method.

`person(id: int | list[int] | tuple[int]) -> str` Recursively gets the name of a person, list of persons or any structure involving person ids.
```python
people.person(1) # returns "Alice"
people.person([1, 2]) # returns ["Alice", "Bob"]
people.person((1, 2)) # returns ("Alice", "Bob")
people.person([1, [2, 3]]) # returns ["Alice", ["Bob", "Charlie"]]
```

### Team managing methods

After committing, the team managing methods become available:

`teamOptions(n:int) -> list[tuple[tuple[int]]]` Returns a list of all possible team options (creating n teams containing roughly the same people). Each team is represented by a tuple of tuples, where each tuple represents a team and each integer represents a person's id.
```python
people.teamOptions(2) # returns [((1, 2), (3, 4)), ((1, 3), (2, 4)), ((1, 4), (2, 3))]
```
Teams may be uneven if the number of people is not divisible by the number of teams. **Attention: Separating into more teams than two is not yet supported.**

`isTeamOk(team: tuple[int]) -> bool` Dictates whether a team is valid or not. A team is valid if for each person in the team, all their designated pairs are also in the team, and all their avoids are not in the team.
```python
people.isTeamOk((1, 2)) # returns True
people.isTeamOk((1, 3)) # returns False
```

`areTeamsOk(teams: tuple[tuple[int]]) -> bool` Dictates whether a configuration of teams is valid or not. Calls the `isTeamOk` method on each team.
```python
people.areTeamsOk(((1, 2), (3, 4))) # returns True
people.areTeamsOk(((1, 3), (2, 4))) # returns False
```

`getPossibleTeams(n:int) -> list[tuple[tuple[int]]]` Returns a list of all possible team configurations (creating n teams containing roughly the same people) that are valid. Calls the `teamOptions` and `areTeamsOk` methods.
```python
people.getPossibleTeams(2) # returns [((1, 2), (3, 4))]
```

## Other functions in the module

`block(state: bool) -> Callable` Decorator that blocks the execution of a method from a class that must have a `blocker_state` attribute. Only allows the execution of the method if the `blocker_state` attribute is set to `state`.
```python
class Example:
    def __init__(self):
        self.blocker_state = False

    @block(False)
    def first(self):
        print("Calling method first()")

    @block(True)
    def second(self):
        print("Calling method second()")

    def set_state(self, state):
        self.blocker_state = state

example = Example()
example.first() # prints "Calling method first()"
example.second() # raises a RuntimeError("Method second() is blocked")
example.set_state(True)
example.second() # prints "Calling method second()"
```

`tablifyOptions(options: list[tuple[tuple[str]]]) -> str` Returns a string representation of a list of options. The options are listed in a table, where each column corresponds to a team and each row corresponds to an option.
```python
people.tablifyOptions(people.teamOptions(2))
# Returns a string representation of the following table:
# Team 1                Team 2
# --------------------  --------------------
# Eve, Charlie, Dave    Bob, Alice, Frank
# Eve, Bob, Alice       Charlie, Frank, Dave
# Charlie, Frank, Dave  Eve, Bob, Alice
# Bob, Alice, Frank     Eve, Charlie, Dave
```

## Example Usage
Here's an example of how you might use the People class to generate two teams of people for a game:

```python
people = People(["Alice", "Bob", "Charlie", "Dave", "Eve", "Frank"])

people.add("Gina")
people.remove("Frank")

people.pair("Alice", "Bob")
people.pair("Eve", "Frank")

people.avoid("Alice", "Charlie")
people.avoid("Alice", "Dave")

people.commit() # We're done changing the group

possible = people.getPossibleTeams(2)
possible = people.person(possible) # Convert ids to names
print("Options for 2 teams:")
print(tablifyOptions(possible))
print()

# Let's pick a random option
option = np.random.randint(len(possible))
print("Random option:")
print(tablifyOptions([possible[option]]))
```