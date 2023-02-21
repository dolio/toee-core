from templeplus.pymod import PythonModifier
from toee import *
import tpdp
from spell_utils import *

hulk = [23,13,19,0,0,0]
chicken = [5,15,10,2,8,6]
rooster = [6,15,10,2,8,6]
toad = [6,12,10,2,6,4]

stats = [hulk,chicken,rooster,toad]

def ResetAnim(char, args, evt_obj):
	char.obj_set_int(obj_f_animation_handle, 0)
	return 0

def Proto(char, args, evt_obj):
	evt_obj.return_val = args.get_arg(2)
	return 0

def Ability(char, args, evt_obj):
	stat = args.get_param(0)
	ix = args.get_arg(3)
	new = stats[ix][stat]
	old = char.stat_base_get(stat)
	evt_obj.bonus_list.modify(new - old, 1, 0x66)
	return 0

def Atks(char, args, evt_obj):
	evt_obj.return_val = args.get_param(0)
	return 0

def CheckRemove(char, args, evt_obj):
	if evt_obj.data1 == args.get_arg(0):
		game.particles('sp-Polymorph Self', char)
		args.remove_spell_mod()
		args.remove_spell()
		char.obj_set_int(obj_f_animation_handle, 0)
	return 0

poly = PythonModifier('sp-Polymorph', 5, 0)
poly.AddHook(ET_OnConditionAdd, EK_NONE, ResetAnim, ())
poly.AddHook(ET_OnD20Query, EK_Q_Polymorphed, Proto, ())
poly.AddHook(ET_OnD20Signal, EK_S_Dismiss_Spells, CheckRemove, ())
poly.AddHook(ET_OnAbilityScoreLevel, EK_STAT_STRENGTH, Ability,
		(stat_strength,))
poly.AddHook(ET_OnAbilityScoreLevel, EK_STAT_DEXTERITY, Ability,
		(stat_dexterity,))
poly.AddHook(ET_OnAbilityScoreLevel, EK_STAT_CONSTITUTION, Ability,
		(stat_constitution,))
poly.AddHook(ET_OnGetCritterNaturalAttacksNum, EK_NONE, Atks, (3,))
poly.AddSpellDispelCheckStandard()
poly.AddSpellCountdownStandardHook()
poly.AddSpellTeleportPrepareStandard()
poly.AddSpellTeleportReconnectStandard()

nul = PythonModifier('Null Condition', 5, 0)

bale = PythonModifier('sp-Baleful Polymorph', 5, 0)
bale.AddHook(ET_OnConditionAdd, EK_NONE, ResetAnim, ())
bale.AddHook(ET_OnD20Query, EK_Q_Polymorphed, Proto, ())
bale.AddHook(ET_OnAbilityScoreLevel, EK_STAT_STRENGTH, Ability,
		(stat_strength,))
bale.AddHook(ET_OnAbilityScoreLevel, EK_STAT_DEXTERITY, Ability,
		(stat_dexterity,))
bale.AddHook(ET_OnAbilityScoreLevel, EK_STAT_CONSTITUTION, Ability,
		(stat_constitution,))
bale.AddHook(ET_OnAbilityScoreLevel, EK_STAT_INTELLIGENCE, Ability,
		(stat_intelligence,))
bale.AddHook(ET_OnAbilityScoreLevel, EK_STAT_WISDOM, Ability,
		(stat_wisdom,))
bale.AddHook(ET_OnAbilityScoreLevel, EK_STAT_CHARISMA, Ability,
		(stat_charisma,))
bale.AddHook(ET_OnGetCritterNaturalAttacksNum, EK_NONE, Atks, (1,))
poly.AddSpellDispelCheckStandard()
