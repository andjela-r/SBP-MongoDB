# Upiti pre optimizacije

## Upit 1: Kakav je uticaj prvih ciljeva na ishod meča?
```
db.clean_teamstats.aggregate([
   {
       $lookup: {
           from: "clean_player_stats",
           localField: "matchid",
           foreignField: "matchid",
           as: "player_stats"
       }
   },
   {
       $unwind: "$player_stats"
   },
   {
       $group: {
           _id: {
               firstblood: "$firstblood",
               firsttower: "$firsttower",
               firstinhib: "$firstinhib",
               firstbaron: "$firstbaron",
               firstdragon: "$firstdragon"
           },
           totalMatches: { $sum: 1 },
           wins: {
               $sum: {
                   $cond: { if: { $eq: ["$player_stats.win", 1] }, then: 1, else: 0 }
               }
           }
       }
   },
   {
       $project: {
           _id: 0,
           firstblood: "$_id.firstblood",
           firsttower: "$_id.firsttower",
           firstinhib: "$_id.firstinhib",
           firstbaron: "$_id.firstbaron",
           firstdragon: "$_id.firstdragon",
           totalMatches: 1,
           wins: 1,
           winRate: {
               $divide: ["$wins", "$totalMatches"]
           }
       }
   }
]);
```
Vreme izvršavanja nije moguće odrediti zbog Time Out-a. Rezultat se dobija dodavanjem sledećih indeksa:
```
db.clean_teamstats.createIndex({ matchid: 1 });
db.clean_player_stats.createIndex({ matchid: 1 });
```
Vreme izvršavanja: 01:00.741s
Broj dokumenata: 32

Upit 2: Koji su 10 najčešće korišćenih item-a u pobedničkim mečevima i njihov uticaj na performanse? 
```
db.clean_player_stats.aggregate([
 { $match: { win: 1 } },
 { $project: {
     items: ["$item1", "$item2", "$item3", "$item4", "$item5", "$item6"],
     kills: "$kills",
     deaths: "$deaths",
     assists: "$assists"
   }
 },
 { $unwind: "$items" },
 { $group: {
     _id: "$items",
     avg_kills: { $avg: "$kills" },
     avg_deaths: { $avg: "$deaths" },
     avg_assists: { $avg: "$assists" },
     count: { $sum: 1 }
   }
 },
 { $project: {
     _id: 1,
     avg_kills: { $round: ["$avg_kills", 2] },
     avg_deaths: { $round: ["$avg_deaths", 2] },
     avg_assists: { $round: ["$avg_assists", 2] },
     count: 1
   }
 },
 { $sort: { count: -1 } },
 { $limit: 10 }
]);

Vreme izvršavanja: 00:08.213s
Broj dokumenata: 10

Upit 3: Koji su 10 najčešće korišćenih item-a i njihov uticaj na prosečnu štetu?
