"""For now, this is just a place to create interfaces for things for which we're presently using TCOD.

In the future, this will allow us a single point of import from which to swap in other libraries."""

import tcod

Event = tcod.event.Event
EventDispatch = tcod.event.EventDispatch