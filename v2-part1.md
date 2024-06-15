# Upiti posle optimizajie

1. Select the top 10 most frequent played champion combinations on BOT lane and their win rate, ordered by count descending and by win rate descending  

```
   use league_of_legends
db.op_playerstats.aggregate([
  {
    $match: {
      role: { $in: ["DUO_CARRY", "DUO_SUPPORT"] }
    }
  },
  {
    $group: {
      _id: {
        matchid: "$matchid",
        side: {
          $cond: {
            if: { $lte: ["$player", 5] },
            then: "blue",
            else: "red"
          }
        }
      },
      champions: {
        $push: {
          role: "$role",
          champion: "$champion",
          win: "$win"
        }
      }
    }
  },
  {
    $project: {
      _id: 0,
      matchid: "$_id.matchid",
      side: "$_id.side",
      bot_carry: {
        $arrayElemAt: [
          {
            $filter: {
              input: "$champions",
              as: "champ",
              cond: { $eq: ["$$champ.role", "DUO_CARRY"] }
            }
          },
          0
        ]
      },
      bot_support: {
        $arrayElemAt: [
          {
            $filter: {
              input: "$champions",
              as: "champ",
              cond: { $eq: ["$$champ.role", "DUO_SUPPORT"] }
            }
          },
          0
        ]
      }
    }
  },
  {
    $project: {
      matchid: 1,
      side: 1,
      champion1: "$bot_carry.champion",
      champion2: "$bot_support.champion",
      win: "$bot_carry.win"
    }
  },
  {
    $group: {
      _id: {
        champion1: "$champion1",
        champion2: "$champion2"
      },
      count: { $sum: 1 },
      totalWins: { $sum: "$win" },
      winRate: { $avg: "$win" }
    }
  },
  {
    $project: {
      _id: 0,
      champion1: "$_id.champion1",
      champion2: "$_id.champion2",
      count: 1,
      totalWins: 1,
      winRate: { $multiply: ["$winRate", 100] }
    }
  },
  { $sort: { count: -1 } },
  { $limit: 10 },
  { $sort: { winRate: -1 } }
]);
//Vreme izvrsavanja oko 6s

```  

2. Select the most commonly used summoner spell per platform and on what key it’s set up per platform.

```
db.op_participants.aggregate([
  {
    $project: {
      platformid: 1,
      spells: [
        { spell: "$ss1", key: "D" },
        { spell: "$ss2", key: "F" },
      ],
    },
  },
  {
    $unwind: "$spells",
  },
  {
    $match: {
      "spells.spell": { $exists: true },
    },
  },
  {
    $group: {
      _id: {
        platformid: "$platformid",
        spell: "$spells.spell",
        key: "$spells.key",
      },
      count: { $sum: 1 },
    },
  },
  {
    $sort: {
      "_id.platformid": 1,
      count: -1,
    },
  },
  {
    $group: {
      _id: "$_id.platformid",
      most_used_spell: {
        $first: {
          spell: "$_id.spell",
          key: "$_id.key",
          count: "$count",
        },
      },
    },
  },
  {
    $project: {
      _id: 0,
      platform: "$_id",
      spell: "$most_used_spell.spell",
      key: "$most_used_spell.key",
      count: "$most_used_spell.count",
    },
  },
]);

//Vreme izvrsavanja oko 6s
```

3. Select all champions and their “KDA ratio” based on which side they are playing.

```
use league_of_legends
db.opp_playerstats.aggregate([
  {
    $set: {
      side: {
        $cond: { 
          if: { $lte: ["$player", 5] },
          then: "blue",
          else: "red"
        }
      }
    }
  },
  {
    $project: {
      champion: "$champion",
      side: 1,
      kdaRatio: {
        $cond: {
          if: { $eq: ["$deaths", 0] },
          then: { $sum: ["$kills", "$assists"] },
          else: { $divide: [{ $sum: ["$kills", "$assists"] }, "$deaths"] }
        }
      },
    }
  },
  {
    $group: {
      _id: {
        champion: "$champion",
        side: "$side"
      },
      avgKdaRatio: { $avg: "$kdaRatio" },
    }
  },
  {
    $project: {
      _id: 0,
      champion: "$_id.champion",
      side: "$_id.side",
      avgKdaRatio: { $round: ["$avgKdaRatio", 2] }
    }
  },
  {
    $sort: { champion: 1, avgKdaRatio: -1 }
  }
]);


```

4. Select all champions, their main damage type where the player position is "MID" on blue side and the rate at which both sides on MID lane have the same damage type champions.

```
db.opp_playerstats.createIndex({ "matchid": 1, "player": 1 })
db.opp_playerstats.createIndex({ "id": 1, "win": 1 })

db.opp_playerstats.aggregate([
  // Step 1: Filter for MID lane on the blue side
  {
    $match: {
      position: "MID",
      player: { $lte: 5 }
    }
  },
  {
    $set: {
      mainDamageType: {
        $cond: {
          if: { $gt: ["$magicdmgdealt", { $max: ["$physicaldmgdealt", "$truedmgdealt"] }] },
          then: "magic",
          else: {
            $cond: {
              if: { $gt: ["$physicaldmgdealt", "$truedmgdealt"] },
              then: "physical",
              else: "true"
            }
          }
        }
      }
    }
  },
  {
    $project: {
      matchid: 1,
      player: 1,
      champion: 1,
      mainDamageType: 1
    }
  },
{
    $lookup: {
      from: "opp_playerstats",
      let: { matchid: "$matchid" },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$position", "MID"] },
                { $gt: ["$player", 5] },
                { $eq: ["$matchid", "$$matchid"] }
              ]
            }
          }
        },
        {
          $set: {
            mainDamageType: {
              $cond: {
                if: { $gt: ["$magicdmgdealt", { $max: ["$physicaldmgdealt", "$truedmgdealt"] }] },
                then: "magic",
                else: {
                  $cond: {
                    if: { $gt: ["$physicaldmgdealt", "$truedmgdealt"] },
                    then: "physical",
                    else: "true"
                  }
                }
              }
            }
          }
        },
        {
          $project: {
            champion: 1,
            mainDamageType: 1
          }
        }
      ],
      as: "redSideDetails"
    }
  },
  {
    $unwind: "$redSideDetails"
  },
  {
    $project: {
      matchid: 1,
      blueChampion: "$champion",
      blueDamageType: "$mainDamageType",
      redChampion: "$redSideDetails.champion",
      redDamageType: "$redSideDetails.mainDamageType",
      sameDamageType: { $eq: ["$mainDamageType", "$redSideDetails.mainDamageType"] }
    }
  },
  {
    $group: {
      _id: "$blueChampion",
      damageType: { $first: "$blueDamageType" },
      sameDamageTypeCount: { $sum: { $cond: ["$sameDamageType", 1, 0] } },
      totalCount: { $sum: 1 }
    }
  },
  {
    $project: {
      _id: 0,
      champion: "$_id",
      damageType: 1,
      sameDamageTypeCount: 1,
      totalCount: 1,
      sameDamageTypeFrequency: { $divide: ["$sameDamageTypeCount", "$totalCount"] }
    }
  },
  {
    $sort: { sameDamageTypeFrequency: -1 }
  }
]);

//Vreme izvrsavanja oko 1min
```

5. Select the top 10 most banned champions and their average win rate.

```
db.op_teambans.aggregate([
  {
    $group: {
      _id: "$champion",
      banCount: { $sum: 1 }}
  },
  { $sort: { banCount: -1 }},
  { $limit: 10},
  {
    $lookup: {
      from: "opp_playerstats",
      localField: "_id",
      foreignField: "champion",
      as: "player_stats"}
  },
  {
    $unwind: "$player_stats"
  },
 
  {
    $group: {
      _id: "$_id",
      banCount: { $first: "$banCount" },
      totalWins: { $sum: "$player_stats.win" },
      totalMatches: { $sum: 1 }
    }
  },
  {
    $project: {
      _id: 1,
      winRate: { $divide: ["$totalWins", "$totalMatches"] },
      banCount: 1,
      totalWins: 1,
      totalMatches: 1
    }
  },
  {
    $project: {
      champion: "$champion",
      winRate: 1,
      banCount: 1,
      totalWins: 1,
      totalMatches: 1
    }
  },
  { $sort: { banCount: -1 }}
]);
//Vreme izvrsavanja 1s

```
