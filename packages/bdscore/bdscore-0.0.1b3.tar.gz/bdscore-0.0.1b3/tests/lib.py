from bdscore import BDSCore

bds = BDSCore(api_key="efee0a2f25cc49e38284139f169d4bfe")

fx = bds.datapack.getFX(":all", "2023-10-01", "2023-10-31")
equities = bds.datapack.getEquitiesB3(":all", "2023-10-01", "2023-10-31")

print(equities)