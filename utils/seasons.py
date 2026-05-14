def assign_season(row):
    m = row["month"]
    if m in [12,1,2]:
        return "Kleine regentijd"
    if m in [3,4]:
        return "Kleine droge tijd"
    if m in [5,6,7,8]:
        return "Grote regentijd"
    if m in [9,10,11]:
        return "Grote droge tijd"

