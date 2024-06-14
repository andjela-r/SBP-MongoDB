# Upiti pre optimizacije  
Vreme izvršavanja nije moguće odrediti zbog Time Out-a, maksimalno izmereno je 25 minuta.   

1. Select the top 10 most frequent played champion combinations on BOT lane and their win rate, ordered by count descending and by win rate descending  

```
   db.participants.aggregate([
  {
    $match: { role: { $in: ["DUO_CARRY", "DUO_SUPPORT"] }}
  },
  {
    $lookup: {
      from: "playerstats",
      localField: "id",
      foreignField: "id",
      as: "playerstats"}
  },
  {
    $unwind: "$playerstats"
  },
  {
    $match: {role: { $in: ["DUO_CARRY", "DUO_SUPPORT"] }}
  },
  {
    $group: {
      _id: {
        matchid: "$matchid",
        side: {
          $cond: {
            if: { $lte: ["$player", 5] },
            then: "blue",
            else: "red"}}
      },
      champions: {
        $push: {
          role: "$role",
          championid: "$championid",
          win: "$playerstats.win"}}}
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
              cond: { $eq: ["$$champ.role", "DUO_CARRY"] }}},]
      },
      bot_support: {
        $arrayElemAt: [
          {
            $filter: {
              input: "$champions",
              as: "champ",
              cond: { $eq: ["$$champ.role", "DUO_SUPPORT"] }}},0]}}
  },
  {
    $lookup: {
      from: "champs",
      localField: "bot_carry.championid",
      foreignField: "id",
      as: "champion_carry"}
  },
  {
    $lookup: {
      from: "champs",
      localField: "bot_support.championid",
      foreignField: "id",
      as: "champion_support"
    }
  },
  {
    $project: {
      matchid: 1,
      side: 1,
      championid1: { $arrayElemAt: ["$champion_carry.name", 0] },
      championid2: { $arrayElemAt: ["$champion_support.name", 0] },
      win: "$bot_carry.win"}
  },
  {
    $group: {
      _id: {
        championid1: "$championid1",
        championid2: "$championid2"
      },
      count: { $sum: 1 },
      totalWins: { $sum: "$win" },
      winRate: { $avg: "$win" }}
  },
  {
    $project: {
      _id: 0,
      championid1: "$_id.championid1",
      championid2: "$_id.championid2",
      count: 1,
      totalWins: 1,
      winRate: { $multiply: ["$winRate", 100] } }
  },
  { $sort: { count: -1 } },
  { $limit: 10 },
  { $sort: { winRate: -1 } },
]);
```  
2. Select the most commonly used summoner spell per platform and on what key it’s set up per platform.

```
db.participants.aggregate([
  {
    $lookup: {
      from: "matches",
      localField: "matchid",
      foreignField: "id",
      as: "match"}
  },
  { $unwind: "$match" },
  {
    $project: {
      platformid: "$match.platformid",
      ss1: "$ss1",
      ss2: "$ss2"}
  },
  {
    $project: {
      platformid: 1,
      spells: [
        { spell: "$ss1", key: "D" },
        { spell: "$ss2", key: "F" }]}
  },
  { $unwind: "$spells" },
  {
    $match: { "spells.spell": { $exists: true }}
  },
  {
    $group: {
      _id: {
        platformid: "$platformid",
        spell: "$spells.spell",
        key: "$spells.key"},
      count: { $sum: 1 }}
  },
  {
    $sort: {
      "_id.platformid": 1,
      count: -1}
  },
  {
    $group: {
      _id: "$_id.platformid",
      most_used_spell: {
        $first: {
          spell: "$_id.spell",
          key: "$_id.key",
          count: "$count"}}}
  },
  {
    $project: {
      _id: 0,
      platform: "$_id",
      spell: "$most_used_spell.spell",
      key: "$most_used_spell.key",
      count: "$most_used_spell.count"}}
]);
```

3. Select all champions and their “KDA ratio” based on which side they are playing.

```
db.participants.aggregate([
  {
    $lookup: {
      from: "playerstats",
      localField: "id",
      foreignField: "id",
      as: "playerstats"
    }
  },
  { $unwind: "$playerstats" },
  {
    $set: {
      side: {
        $cond: { 
          if: { $lte: ["$player", 5] },
          then: "blue",
          else: "red"}}}
  },
  {
    $project: {
      championid: 1,
      side: 1,
      kdaRatio: {
        $cond: {
          if: { $eq: ["$playerstats.deaths", 0] },
          then: { $sum: ["$playerstats.kills", "$playerstats.assists"] },
          else: { $divide: [{ $sum: ["$playerstats.kills", "$playerstats.assists"] }, "$playerstats.deaths"] }}},}
  },
  {
    $group: {
      _id: {
        championid: "$championid",
        side: "$side"
      },
      avgKdaRatio: { $avg: "$kdaRatio" },
    }
  },
  {
    $lookup: {
      from: "champs",
      localField: "_id.championid",
      foreignField: "id",
      as: "champion" }
  },
  {
    $project: {
      _id: 0,
      championid: { $arrayElemAt: ["$champion.name", 0] },
      side: "$_id.side",
      avgKdaRatio: { $round: ["$avgKdaRatio",2]}
    }
  },
  { $sort: { championid: 1, avgKdaRatio: -1 } }
]);

```

4. Select all champions, their main damage type where the player position is "MID" on blue side and the rate at which both sides on MID lane have the same damage type champions.

```
db.participants.aggregate([
  {
    $match: {
      position: "MID",
      player: { $lte: 5 }
    }
  },
  {
    $lookup: {
      from: "playerstats",
      localField: "id",
      foreignField: "id",
      as: "playerstats"
    }
  },
  { $unwind: "$playerstats" },
  {
    $set: {
      mainDamageType: {
        $cond: {
          if: { $gt: ["$playerstats.magicdmgdealt", { $max: ["$playerstats.physicaldmgdealt", "$playerstats.truedmgdealt"] }] },
          then: "magic",
          else: {
            $cond: {
              if: { $gt: ["$playerstats.physicaldmgdealt", "$playerstats.truedmgdealt"] },
              then: "physical",
              else: "true"}}}}}
  },
  {
    $project: {
      matchid: 1,
      player: 1,
      championid: 1,
      mainDamageType: 1
    }
  },
  {
    $lookup: {
      from: "participants",
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
          $lookup: {
            from: "playerstats",
            localField: "id",
            foreignField: "id",
            as: "playerstats"
          }
        },
        { $unwind: "$playerstats" },
        {
          $set: {
            mainDamageType: {
              $cond: {
                if: { $gt: ["$playerstats.magicdmgdealt", { $max: ["$playerstats.physicaldmgdealt", "$playerstats.truedmgdealt"] }] },
                then: "magic",
                else: {
                  $cond: {
                    if: { $gt: ["$playerstats.physicaldmgdealt", "$playerstats.truedmgdealt"] },
                    then: "physical",
                    else: "true"}}}}}
        },
        {
          $project: {
            championid: 1,
            mainDamageType: 1 }}],
      as: "redSideDetails"}
  },
  {
    $unwind: "$redSideDetails"
  },
  {
    $project: {
      matchid: 1,
      blueChampion: "$championid",
      blueDamageType: "$mainDamageType",
      redChampion: "$redSideDetails.championid",
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
      championid: "$_id",
      damageType: 1,
      sameDamageTypeCount: 1,
      totalCount: 1,
      sameDamageTypeFrequency: { $divide: ["$sameDamageTypeCount", "$totalCount"] }
    }
  },
  {
    $lookup: {
      from: "champs",
      localField: "championid",
      foreignField: "id",
      as: "championDetails"
    }
  },
  {
    $unwind: "$championDetails"
  },
  {
    $project: {
      championName: "$championDetails.name",
      damageType: 1,
      sameDamageTypeCount: 1,
      totalCount: 1,
      sameDamageTypeFrequency: 1}
  },
  { $sort: { sameDamageTypeFrequency: -1 }}
]);
```

5. Select the top 10 most banned champions and their average win rate.

```
db.teambans.aggregate([
  {
    $group: {
      _id: "$championid",
      banCount: { $sum: 1 }}
  },
  { $sort: { banCount: -1 }},
  { $limit: 10},
  {
    $lookup: {
      from: "participants",
      localField: "_id",
      foreignField: "championid",
      as: "participants"}
  },
  {
    $unwind: "$participants"
  },
  {
    $lookup: {
      from: "playerstats",
      localField: "participants.id",
      foreignField: "id",
      as: "playerstats"
    }
  },
  {
    $unwind: "$playerstats"
  },
  {
    $group: {
      _id: "$_id",
      banCount: { $first: "$banCount" },
      totalWins: { $sum: "$playerstats.win" },
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
    $lookup: {
      from: "champs",
      localField: "_id",
      foreignField: "id",
      as: "champion"
    }
  },
  { $unwind: "$champion" },
  {
    $project: {
      championName: "$champion.name",
      winRate: 1,
      banCount: 1,
      totalWins: 1,
      totalMatches: 1
    }
  },
  { $sort: { banCount: -1 }}
]);

```

