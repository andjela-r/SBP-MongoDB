# Upiti pre optimizacije

Upit 1: Kakav je uticaj prvih ciljeva na ishod meča?
```
db.clean_teamstats.aggregate([
   {
       $lookup: {
           from: "clean_matches",
           localField: "matchid",
           foreignField: "id",
           as: "match"
       }
   },
   {
       $unwind: "$match"
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
           match_count: { $sum: 1 },
           win_count: {
               $sum: {
                   $cond: { if: { $eq: ["$win", 1] }, then: 1, else: 0 }
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
           match_count: 1,
           win_count: 1,
           win_rate: { $divide: ["$win_count", "$match_count"] }
       }
   },
   {
       $sort: { win_rate: -1 }
   }
]);
```
Vreme izvršavanja nije moguće odrediti zbog Time Out-a. Rezultat se dobija dodavanjem sledećih indeksa:
```
db.clean_teamstats.createIndex({ matchid: 1 });
db.clean_matches.createIndex({ id: 1 });
```
Vreme izvršavanja: 36.148s
Broj dokumenata: 32

