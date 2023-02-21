from templeplus.pymod import PythonModifier
from toee import *
import tpdp
from utilities import *
from spell_utils import *

def PermETool(char, args, evt_obj):
	spell_enum = args.get_param(0)
	name = spellName(args.get_arg(0)) # game.get_spell_mesline(spell_enum)
	key_name = "PERMANENT_{}".format(name.upper().replace(" ", "_"))

	evt_obj.append(tpdp.hash(key_name), -2, "(Permanent)")
	return 0

def PermActive(char, args, evt_obj):
	spell_enum = args.get_param(0)
	if evt_obj.data1 == spell_enum:
		evt_obj.return_val = 1
	return 0

def PermDispel(char, args, evt_obj):
	mask = args.get_param(1)

	if not (evt_obj.flags & mask): return 0

	dpacket = tpdp.SpellPacket(evt_obj.spell_id)
	spacket = tpdp.SpellPacket(args.get_arg(0))

	# This special dispel handler is for cases where a minimum
	# level is required to dispel.
	if dpacket.caster_level <= spacket.caster_level: return 0

	cap = 0
	if evt_obj.flags & 0x40: # break enchantment
		cap = 15
	elif dpacket.spell_enum == 133: # dispel magic
		cap = 10
	elif dpacket.spell_enum == 202: # greater dispel magic
		cap = 20

	dispel_bonus = min(dpacket.caster_level, cap)
	boni = tpdp.BonusList()
	boni.add(dispel_bonus, 0, 203)
	die = dice_new('1d20')
	roll = die.roll()
	check = die.roll() + dispel_bonus
	dc = 11 + spacket.caster_level
	link = '~Dispel Magic~[TAG_SPELLS_DISPEL_MAGIC]'

	hist = tpdp.create_history_dc_roll(
			dpacket.caster, dc, die, roll, link, boni)

	if check >= dc: # success
		game.create_history_from_id(hist)
		spell_name = game.get_spell_mesline(args.get_param(0))
		floater = "Dispel attempt successful. [{}]".format(spell_name)
		spacket.caster.float_text_line(floater, tf_white)

		args.remove_spell()
		args.remove_spell_mod()

	return 0

def Yes(char, args, evt_obj):
	evt_obj.return_val = 1
	return 0

sips = (spell_see_invisibility, 0x81)

sinv = PythonModifier('sp-Permanent See Invisibility', 3, 0)
sinv.AddHook(ET_OnDispelCheck, EK_NONE, PermDispel, sips)
sinv.AddHook(ET_OnGetEffectTooltip, EK_NONE, PermETool, sips)
sinv.AddHook(ET_OnD20Query, EK_Q_Critter_Can_See_Invisible, Yes, ())
sinv.AddHook(ET_OnD20Query, EK_Q_Critter_Has_Spell_Active, PermActive, sips)

def HitBonus(char, args, evt_obj):
	packet = evt_obj.attack_packet
	weapon = packet.get_weapon_used()

	if weapon == OBJ_HANDLE_NULL:
		evt_obj.bonus_list.add(args.get_arg(1), 12, 0xd1)

	return 0

def DmgBonus(char, args, evt_obj):
	apacket = evt_obj.attack_packet
	dpacket = evt_obj.damage_packet
	weapon = apacket.get_weapon_used()

	if weapon == OBJ_HANDLE_NULL:
		dpacket.add_damage_bonus(args.get_arg(1), 12, 0xd1)
		dpacket.attack_power |= D20DAP_MAGIC

	return 0

mfps = (spell_magic_fang,)

mfng = PythonModifier('sp-Permanent Magic Fang', 4, 0)
mfng.AddHook(ET_OnGetEffectTooltip, EK_NONE, PermETool, mfps)
mfng.AddHook(ET_OnD20Query, EK_Q_Critter_Has_Spell_Active, PermActive, mfps)
mfng.AddHook(ET_OnToHitBonus2, EK_NONE, HitBonus, ())
mfng.AddHook(ET_OnDealingDamage, EK_NONE, DmgBonus, ())
mfng.AddSpellDispelCheckStandard()

def SaveBonus(char, args, evt_obj):
	evt_obj.bonus_list.add(1, 13, 0xc7)
	return 0

rsps = (spell_resistance,)

rsng = PythonModifier('sp-Permanent Resistance', 4, 0)
rsng.AddHook(ET_OnGetEffectTooltip, EK_NONE, PermETool, rsps)
rsng.AddHook(ET_OnD20Query, EK_Q_Critter_Has_Spell_Active, PermActive, rsps)
rsng.AddHook(ET_OnSaveThrowLevel, EK_NONE, SaveBonus, ())
rsng.AddSpellDispelCheckStandard()
