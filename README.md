The Turn System

Each tick:
* Get lists of mobiles whose _action_cooldown are and aren't greater than zero
* For those who are, reduce it by 1
* For those who are not, randomize (random.sample()) the list order and prompt each entity for an action

Having a .tick() method on mobiles might be helpful

---

Create unique event managers for menus, main playfield.


---

Consider separating simulation and graphical ticks. This way, we can run animations while awaiting input.

Alo. & Rol. suggest making a global clock that decides what--including simulation and animations--needs to be ticked at every global tick.

---

Agenda:
* Implement animations on global tick
* Menus need to render a cursor on their selected elements
* Create an Interface class to juggle the playfield and menus and maybe also things rendered at the same level as the playfield


---