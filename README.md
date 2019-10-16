# socialrating
A Django app which allows groups of people to define and rate things (like places, movies, food). 

## Missing Views
The following views are missing functionality or templates


| Model      | List | Create | Detail | Settings | Update | Delete |
| ---------- | ---- | ------ | ------ | -------- | ------ | ------ |
| Team       |   ☑  |    ☑   |    ☑   |     ☑    |    ☑   |    ☑   |
| Membership |   ☑  |    ☐   |    ☐   |     ☐    |    ☐   |    ☐   |
| Category   |   ☑  |    ☑   |    ☑   |     ☑    |    ☑   |    ☑   |
| Context    |   ☑  |    ☑   |    ☑   |     ☑    |    ☑   |    ☑   |
| Fact       |   ☑  |    ☑   |    ☑   |     ☑    |    ☑   |    ☑   |
| Rating     |   ☑  |    ☑   |    ☑   |     ☑    |    ☑   |    ☑   |
| Item       |   ☑  |    ☑   |    ☑   |     ☑    |    ☑   |    ☑   |
| Review     |   ☑  |    ☑   |    ☑   |     ☑    |    ☑   |    ☑   |
| Vote       |   ☑  |    ☑   |    ☑   |     ☑    |    ☑   |    ☑   |
| Attachment |   ☑  |    ☑   |    ☑   |     ☑    |    ☑   |    ☑   |



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

