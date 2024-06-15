# Upiti pre optimizacije

### Upit 1: Kakav je uticaj prvih ciljeva na ishod meča?
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
Vreme izvršavanja: 01:00.741
Broj dokumenata: 32

### Upit 2: Koji su 10 najčešće korišćenih item-a u pobedničkim mečevima i njihov uticaj na performanse? 
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
```

Vreme izvršavanja: 00:08.213
Broj dokumenata: 10

### Upit 3: Koji su 100 najčešće korišćenih item-a i njihov uticaj na prosečnu štetu?
db.clean_player_stats.aggregate([
   {
       $project: {
           items: ["$item1", "$item2", "$item3", "$item4", "$item5", "$item6"],
           totdmgdealt: 1
       }
   },
   {
       $unwind: "$items"
   },
   {
       $group: {
           _id: "$items",
           avgDamage: { $avg: "$totdmgdealt" },
           count: { $sum: 1 }
       }
   },
   {
       $sort: { avgDamage: -1 }
   },
   {
       $limit: 100
   },
   {
       $project: {
           _id: 0,
           item: "$_id",
           avgDamage: 1,
           count: 1
       }
   }
]);
```
Vreme izvršavanja: 00:10.829
Broj dokumenata: 100

### Upit 4: Koji je uticaj upravljanja resursima džungle na ishod meča?
```
db.clean_player_stats.aggregate([
   { $match: { win: { $exists: true } } },
  
   {
       $group: {
           _id: "$win",
           avgTotalVisionScore: { $avg: { $round: ["$visionscore", 2] } },
           avgTotalHeal: { $avg: { $round: ["$totdmgtochamp", 2] } },
           avgTotalDamageDealt: { $avg: { $round: ["$totdmgdealt", 2] } },
           avgTotalDamageToChamps: { $avg: { $round: ["$totdmgtochamp", 2] } },
           avgTotalTurretKills: { $avg: { $round: ["$totminionskilled", 2] } },
           avgTotalCS: { $avg: { $round: ["$totminionskilled", 2] } },  // Creep Score (Farm)
           avgTotalWardsPlaced: { $avg: { $round: ["$neutralminionskilled", 2] } },
           avgTotalWardsKilled: { $avg: { $round: ["$neutralminionskilled", 2] } },
           avgOwnJungleCS: { $avg: { $round: ["$ownjunglekills", 2] } },
           avgEnemyJungleCS: { $avg: { $round: ["$enemyjunglekills", 2] } },
           count: { $sum: 1 }
       }
   },
  
   {
       $project: {
           _id: 0,
           win: "$_id",
           avgTotalVisionScore: { $round: ["$avgTotalVisionScore", 2] },
           avgTotalHeal: { $round: ["$avgTotalHeal", 2] },
           avgTotalDamageDealt: { $round: ["$avgTotalDamageDealt", 2] },
           avgTotalDamageToChamps: { $round: ["$avgTotalDamageToChamps", 2] },
           avgTotalTurretKills: { $round: ["$avgTotalTurretKills", 2] },
           avgTotalCS: { $round: ["$avgTotalCS", 2] },
           avgTotalWardsPlaced: { $round: ["$avgTotalWardsPlaced", 2] },
           avgTotalWardsKilled: { $round: ["$avgTotalWardsKilled", 2] },
           avgOwnJungleCS: { $round: ["$avgOwnJungleCS", 2] },
           avgEnemyJungleCS: { $round: ["$avgEnemyJungleCS", 2] },
           count: 1
       }
   },
  
   {
       $sort: { win: 1 }
   }
]);
```
Vreme izvršavanja: 00:12.882
Broj dokumenata: 2

### Upit 5: Koje su najefikasnije uloge na osnovu ekonomije?
```
db.clean_player_stats.aggregate([
   {
       $lookup: {
           from: "clean_participants",
           localField: "id",
           foreignField: "id",
           as: "participant"
       }
   },
   {
       $unwind: "$participant"
   },
   {
       $group: {
           _id: "$participant.role",
           avgGoldEarned: { $avg: "$goldearned" },
           avgGoldSpent: { $avg: "$goldspent" },
           avgTotalMinionsKilled: { $avg: "$totminionskilled" },
           avgNeutralMinionsKilled: { $avg: "$neutralminionskilled" }
       }
   },
   {
       $project: {
           _id: 0,
           role: "$_id",
           avgGoldEarned: 1,
           avgGoldSpent: 1,
           avgTotalMinionsKilled: 1,
           avgNeutralMinionsKilled: 1
       }
   },
   {
       $sort: { avgGoldEarned: -1 }  // Sortiraj uloge prema prosečnoj zaradi zlata
   }
]);
```
Vreme izvršavanja: 02:55.026
