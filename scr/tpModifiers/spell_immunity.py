from templeplus.pymod import PythonModifier
from toee import *
import tpdp
from utilities import *
print "Registering spell_immunity"

by_level = 0
by_school = 1
by_subschool = 2
by_descriptor = 3
by_spell = 4

def Ordinal(n):
	if n == 1:
		return "1st"
	elif n == 2:
		return "2nd"
	elif n == 3:
		return "3rd"
	else:
		return "{}th".format(n)

def Description(category, item):
	if category == by_level:
		return "Immunity to {} level spells".format(Ordinal(item))
	elif category == by_spell:
		return "Immunity to {}".format(game.get_spell_mesline(item))

	return ""

def Tooltip(attachee, args, evt_obj):
	duration = args.get_arg(1)
	category = args.get_arg(2)
	item = args.get_arg(3)

	desc = Description(category,item)
	evt_obj.append("{}	({} rounds)".format(desc, duration))

	return 0


# args
#  0: spell_id
#  1: duration
#  2: category
#  3: item
#  4: spare
#  5: spare

immune = PythonModifier('Spell Immunity', 6)
immune.AddHook(ET_OnGetTooltip,EK_NONE,Tooltip,())
#immune.AddHook(ET_OnGetEffectTooltip,EK_NONE,EffectTooltip,())
