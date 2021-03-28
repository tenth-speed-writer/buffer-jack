A cellulose is a class which upon instantiation generates for
itself an np array of boolean values, defaulting to False. These
values represent cells which should be passable to most entities.

A cellulose must have a .apply_to(x0, y0, field: np.ndarray)
method which will apply any cell marked as True to the specified
field matrix, using (x0, y0) as a top-left corner.

A cellulose must create a list of door points that it possesses.
For every 15 tiles of width or height, find the n passable tiles
closest to the center of that 15 tile stretch at the desired
edge, then select randomly among them.

Save this in a .door_points attribute.

The map generator, when drawing a room out from another room,
will connect it by the door point corresponding to the 9x9
block edge for the spawning chunk of room. 

---

A map generator holds a description of the map it's generating
in the form of a matrix of meta-tiles. Each meta-tile represents
15x15 passability bools.

A map generator has a ._generate() method run at the end of
instantiation. This method decides which edge cell on top or
left of the meta_field to first populate. It then selects a
number of meta_field cells with which the first room shares
edges, spawns rooms corresponding to those cells, and possibly
draws cells to any rooms that the new room also borders.

It continues to do so until it fails a certain number of times,
or has filled at least a certain proportion of the meta_field.

A map generator keeps track of its room celluloses in a list of
(cel, cells) tuples where cells is a tuple of (x, y) meta_field
positions.

It further has a list of .route_cels which are door celluloses
which are scaled to the size of the map (to allow swerving) but
only apply themselves to a few specific True cells.

A map generator must have a .render() method which will apply
its celluloses in appropriate order, convert passable tiles to
floors, convert impassable tiles which border passable ones into
walls, and maybe create door entities for the door points--then
return this all as a list of (x, y, Entity) tuples to be fed
into the PlayField class's `contents` attribute.  