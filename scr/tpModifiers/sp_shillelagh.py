from templeplus.pymod import PythonModifier
from toee import *
import tpdp
from spell_utils import verifyItem

def PackDice(num, size):
	return (num & 0x7f) | (size & 0x7f)<<7

def UnpackDice(packed):
	return (packed & 0x7f, packed>>7 & 0x7f)

# damage increases
damages = {
		PackDice(1,1): PackDice(1,3),
		PackDice(1,2): PackDice(1,4),
		PackDice(1,3): PackDice(1,6),
		PackDice(1,4): PackDice(1,8),
		PackDice(1,6): PackDice(2,6),
		PackDice(1,8): PackDice(3,6),
		PackDice(2,6): PackDice(4,6),
		PackDice(3,6): PackDice(6,6), # borrowed from bigger progressions
		PackDice(4,6): PackDice(8,6)  # borrowed from bigger progressions
		}

def Verify(char, args, weapon):
	caster = tpdp.SpellPacket(args.get_arg(4)).caster

	return verifyItem(weapon, args) and char == caster

def Atk(char, args, evt_obj):
	if Verify(char, args, evt_obj.attack_packet.get_weapon_used()):
		evt_obj.bonus_list.add(1, 12, 147)

	return 0

def Dmg(char, args, evt_obj):
	if Verify(char, args, evt_obj.attack_packet.get_weapon_used()):
		evt_obj.damage_packet.add_damage_bonus(1, 12, 147)
		evt_obj.damage_packet.attack_power |= D20DAP_MAGIC

	return 0

def Dice(char, args, evt_obj):
	if Verify(char, args, evt_obj.weapon):
		dice = evt_obj.dice_packed
		# no change if it's not in our dictionary
		evt_obj.dice_packed = damages.get(dice, dice)

	return 0

def Glow(char, args, evt_obj):
	if Verify(char, args, evt_obj.get_obj_from_args()):
		if evt_obj.return_val < 1:
			evt_obj.return_val = 1
	return 0

shl = PythonModifier('Shillelagh', 5, 0)
shl.AddHook(ET_OnToHitBonus2, EK_NONE, Atk, ())
shl.AddHook(ET_OnDealingDamage, EK_NONE, Dmg, ())
shl.AddHook(ET_OnGetAttackDice, EK_NONE, Dice, ())
shl.AddHook(ET_OnWeaponGlowType, EK_NONE, Glow, ())

def Add(wpn, args, evt_obj):
	spell_id = args.get_arg(0)
	wpn.item_condition_add_with_args('Shillelagh', 0, 0, 0, 0, spell_id)
	return 0

def Rmv(wpn, args, evt_obj):
	spell_id = args.get_arg(0)
	wpn.item_condition_remove('Shillelagh', spell_id)
	return 0

spl = PythonModifier('sp-Shillelagh', 3, 0)
spl.AddHook(ET_OnConditionAdd, EK_NONE, Add, ())
spl.AddHook(ET_OnConditionRemove, EK_NONE, Rmv, ())
