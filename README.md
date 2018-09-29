* Do you like Ryanair? Nobody does, but their flights are cheap and that's something. Are you too lazy to look for good weekend flights that won't require taking days off from work? Me too! So Power up the `python weekend.py` after populating your database with whatever flights you want, e.g. `python main.py 2018-10-01 2019-05-01 BCN SXF` and go!

For example if you're living in Barcelona...
```
Malaga 2018-11-30 19:45:00  ---  [21.98]
Malaga 2019-01-18 19:45:00  ---  [21.98]
Brussels 2019-01-18 20:00:00  ---  [29.98]
Milan (Bergamo) 2019-01-18 19:40:00  ---  [29.98]
Mallorca 2019-02-01 16:20:00  ---  [33.54, 33.54]
Mallorca 2019-02-01 21:35:00  ---  [33.54, 33.54]
Brussels 2019-02-01 20:00:00  ---  [33.98]
Porto 2019-01-18 22:05:00  ---  [35.22, 40.58]
Mallorca 2018-12-14 21:35:00  ---  [39.55, 47.35]
Mallorca 2018-12-14 16:20:00  ---  [39.55, 47.35]
Dublin T1 2019-01-18 21:15:00  ---  [39.98]
Dublin T1 2019-01-18 16:35:00  ---  [39.98]
Brussels 2019-02-22 20:00:00  ---  [43.75]
London (Stansted) 2019-01-25 18:05:00  ---  [45.879999999999995]
Vienna International Airport 2019-01-18 20:40:00  ---  [45.88]
Vienna International Airport 2019-02-22 20:40:00  ---  [45.88]
Mallorca 2018-12-28 21:35:00  ---  [47.35, 39.55]
Mallorca 2018-11-30 21:35:00  ---  [47.35, 66.93]
Mallorca 2018-11-30 16:20:00  ---  [47.35, 66.93]
Dublin T1 2018-11-30 21:15:00  ---  [47.519999999999996]
Dublin T1 2018-11-30 16:35:00  ---  [47.519999999999996]
Rome (Fiumicino) T3 2019-01-11 16:30:00  ---  [48.93000000000001]
Dublin T1 2019-02-01 21:15:00  ---  [49.519999999999996]
Malaga 2019-02-01 19:45:00  ---  [49.93]
...
```
Those prices (in the square brackets) look good for a FRI-SUN evening flights, don't they?

* Remember to run redis for this to work, e.g.
`docker run -p 6379:6379 -v /home/grining/ryanair_crawler/redis:/data -d redis`
