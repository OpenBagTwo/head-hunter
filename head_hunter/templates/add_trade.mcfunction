# Desc: Prepends a trade to the wandering trader based on its trade index
#
# Called by: wandering_trades:tick

# Trades

execute if score @s wt_tradeIndex matches IDX run data modify entity @s Offers.Recipes prepend value {rewardExp:XP_BONUSb,maxUses:PURCHASE_LIMIT,buy:{id:COST_ITEM,Count:COST_QTYb},buyB:{id:"minecraft:air",Count:1b},sell:{id:"minecraft:player_head",Count:1b,tag:{HEAD_SPEC}}}

