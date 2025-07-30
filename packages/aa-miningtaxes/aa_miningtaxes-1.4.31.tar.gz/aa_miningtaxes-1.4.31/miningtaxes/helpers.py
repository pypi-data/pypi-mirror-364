# from eveuniverse.models import EveGroup, EveType


class PriceGroups:
    moon_ore_groups = (
        1923,  # R64 Moon ores
        1922,  # R32 Moon ores
        1921,  # R16 Moon ores
        1920,  # R8 Moon ores
        1884,  # R4 Moon ores
    )

    groups = (
        711,  # Gasses
        1923,  # R64 Moon ores
        1922,  # R32 Moon ores
        1921,  # R16 Moon ores
        1920,  # R8 Moon ores
        1884,  # R4 Moon ores
        427,  # Moon materials
        465,  # Ice
        423,  # Ice materials
        18,  # Ore materials
        468,  # Mercoxit
        450,  # Arkonor
        4031,  # Bezdnacine
        451,  # Bistot
        452,  # Crokite
        453,  # Dark Ochre
        467,  # Gneiss
        454,  # Hedbergite
        455,  # Hemorphite
        456,  # Jaspet
        457,  # Kernite
        469,  # Omber
        458,  # Plagioclase
        459,  # Pyroxeres
        4030,  # Rakovene
        460,  # Scordite
        461,  # Spodumain
        4029,  # Talassonite
        462,  # Veldspar
        4513,  # Mordunium
        4514,  # Ytirium
        4515,  # Eifyrium
        4516,  # Ducinium
        4568,  # Mutanite
        4755,  # Kylixium
        4756,  # Nocxite
        4757,  # Ueganite
        4758,  # Hezorime
        4759,  # Griemeer
    )

    taxgroups = {
        711: "Gasses",
        1923: "R64",
        1922: "R32",
        1921: "R16",
        1920: "R8",
        1884: "R4",
        465: "Ice",
        468: "Mercoxit",
        450: "Ores",
        4031: "Ores",
        451: "Ores",
        452: "Ores",
        453: "Ores",
        467: "Ores",
        454: "Ores",
        455: "Ores",
        # 529: "Ores",
        457: "Ores",
        # 526: "Ores",
        # 516: "Ores",
        458: "Ores",
        459: "Ores",
        4030: "Ores",
        460: "Ores",
        461: "Ores",
        469: "Ores",
        4029: "Ores",
        462: "Ores",
        4513: "Ores",
        4514: "Ores",
        4515: "Ores",
        4516: "Ores",
        456: "Ores",  # Jaspet
        4568: "Ores",  # Mutanite
        4755: "Ores",  # Kylixium
        4756: "Ores",  # Nocxite
        4757: "Ores",  # Ueganite
        4758: "Ores",  # Hezorime
        4759: "Ores",  # Griemeer
    }


#    def __init__(self):
#        self.items = []
#        added = set()
#        for grp in self.groups:
#            EveGroup.objects.get_or_create_esi(
#                id=grp,
#                include_children=True,
#                wait_for_children=True,
#            )
#            g = EveType.objects.filter(eve_group_id=grp)
#            for it in g:
#                if it.id in added:
#                    continue
#                added.add(it.id)
#                self.items.append(it)
#        self.taxable_groups = set()
#        for k in self.taxgroups.keys():
#            self.taxable_groups.add(self.taxgroups[k])
