# socialrating
A Django app which allows groups of people to define and rate things (like places, movies, food). 


## Model Diagram

    +----------+         +-------------+
    |          |         |             |
    |          |         |             |
    |   Fact   |  +----->+    Team     |
    |          |  |      |             |
    |          |  |      |             |
    +----------+  |      +-------------+
         |        |
         v        |
    +--------------+     +-------------+
    |              |     |             |
    |              |     |             |
    |   Category   +<----+   Context   |
    |              |     |             |
    |              |     |             |
    +--------------+     +-------------+
     ^      ^                   ^
     |      |                   |
     |      |                   |
     | +------------+    +------------+
     | |            |    |            |
     | |            |    |            |
     | |   Item     +<---+   Review   |
     | |            |    |            |
     | |            |    |            |
     | +------------+    +------------+
     |                    ^     ^
     |                    |     |
   +------------+         |  +--------------+
   |            |         |  |              |
   |            |         |  |              |
   |   Rating   |         |  |  Attachment  |
   |            |         |  |              |
   |            |         |  |              |
   +-----^------+         |  +--------------+
         |                |
         |                |
         |       +----------+
         |       |          |
         |       |          |
         +-------+   Vote   |
                 |          |
                 |          |
                 +----------+

