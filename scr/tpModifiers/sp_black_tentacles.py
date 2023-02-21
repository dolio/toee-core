from templeplus.pymod import PythonModifier
from toee import *
import tpdp
from utilities import *
from spell_utils import *

print "registering sp_black_tentacles"
arg_spell_id = 0
arg_duration = 1
arg_part_id = 2
arg_aoe_id = 3

def Begin(spell_obj, args, evt_obj):
	radius_feet = 20.0

	spell_id = args.get_arg(arg_spell_id)
	part_id = args.get_arg(arg_part_id)

	packet = tpdp.SpellPacket(spell_id)
	packet.add_spell_object(spell_obj, part_id)
	packet.update_registry()

	aoe_id = spell_obj.object_event_append(OLC_CRITTERS, radius_feet)
	args.set_arg(arg_aoe_id, aoe_id)
	return 0

def Enter(attachee, args, evt_obj):
	aoe_id = args.get_arg(arg_aoe_id)

	if evt_obj.evt_id != aoe_id:
		return 0

	target = evt_obj.target

	if target == OBJ_HANDLE_NULL or attachee == OBJ_HANDLE_NULL:
		return 0

	spell_id = args.get_arg(arg_spell_id)
	duration = args.get_arg(arg_duration)
	packet = tpdp.SpellPacket(spell_id)

	if packet.add_target(target, 0):
		target.condition_add_with_args(
				'Black Tentacles Target', spell_id, duration, 0, aoe_id, 0)

	return 0

def DismissArea(attachee, args, evt_obj):
	if evt_obj.data1 == args.get_arg(arg_spell_id):
		args.remove_spell()
		args.remove_spell_mod()
	return 0

# 0: spell_id
# 1: spell_duration
# 2: spell_part_id
# 3: spell_aoe_id
# 4: spare
area = PythonModifier('Black Tentacles Area', 5)
area.AddHook(ET_OnConditionAdd, EK_NONE, Begin, ())
area.AddHook(ET_OnObjectEvent,EK_OnEnterAoE,Enter,())
area.AddHook(ET_OnD20Signal, EK_S_Dismiss_Spells, DismissArea, ())
area.AddSpellDispelCheckStandard()
area.AddSpellTeleportPrepareStandard()
area.AddSpellTeleportReconnectStandard()
area.AddSpellCountdownStandardHook()
area.AddAoESpellEndStandardHook()

arg_grapple_state = 2
arg_grapple_part = 4

def Leave(target, args, evt_obj):
	aoe_id = args.get_arg(arg_aoe_id)
	grapple_state = args.get_arg(arg_grapple_state)

	if evt_obj.evt_id != aoe_id:
		return 0

	return Remove(target, args, evt_obj)

# Performs the grapple check with all the relevant black tentacles
# bonuses. 'target' is always the creature within the tentacle area of
# effect. 'defense' indicates whether this is the tentacles initially
# attacking (False) or a break free attempt (True).
def GrappleCheck(caster, cast_level, target, defense=False):
	dice = dice_new('1d20')
	caster_roll = dice.roll()
	target_roll = dice.roll()

	caster_bonus = tpdp.BonusList()
	# BAB equal to caster level
	caster_bonus.add(cast_level, 0, "Base Attack Bonus")
	caster_mod = cast_level
	# +4 for large size
	caster_bonus.add(4, 0, "Size Bonus")
	caster_mod += 4
	# +4 for strength 19
	caster_bonus.add(4, 0, "~Strength~[TAG_STRENGTH] Bonus")
	caster_mod += 4

	target_bonus = tpdp.BonusList()
	# BAB
	t_bab = target.stat_base_get(stat_attack_bonus)
	target_bonus.add(t_bab, 0, "Base Attack Bonus")
	# size bonus
	t_size_mod = target.stat_level_get(stat_size) - STAT_SIZE_MEDIUM
	target_bonus.add(t_size_mod * 4, 0, "Size Bonus")
	# strength modifier
	t_str_mod = target.stat_level_get(stat_str_mod)
	target_bonus.add(t_str_mod, 0, "~Strength~[TAG_STRENGTH] Bonus")

	target_mod = tpdp.dispatch_ability_check(
			caster, target, stat_strength, target_bonus, 1)

	result = 0

	while True:
		caster_tot = caster_roll + caster_mod
		target_tot = target_roll + target_mod

		if caster_tot > target_tot:
			if not defense: result = 1
			break
		elif caster_tot < target_tot:
			if defense: result = 1
			break
		elif caster_mod > target_mod:
			if not defense: result = 1
			break
		elif caster_mod < target_mod:
			if defense: result = 1
			break

		# tied, reroll
		caster_roll = dice.roll()
		target_roll = dice.roll()


	title = 5225
	flags = 1

	hist_id = 0

	if defense:
		hist_id = tpdp.create_history_type6_opposed_check(
				target, caster,
				target_roll, caster_roll,
				target_bonus, caster_bonus,
				title, 144-result, flags)
	else:
		hist_id = tpdp.create_history_type6_opposed_check(
				caster, target,
				caster_roll, target_roll,
				caster_bonus, target_bonus,
				title, 144-result, flags)

	game.create_history_from_id(hist_id)

	return result

def Slowed(target, args, evt_obj):
	grapple_state = args.get_arg(arg_grapple_state)

	evt_obj.factor = 0.5

	return 0

def StartGrapple(target, args):
	spell_id = args.get_arg(arg_spell_id)

	target.condition_add_with_args('Grappled', spell_id, 1, 0)
	part_id = game.particles('sp-Black Tentacles Grapple', target)
	args.set_arg(arg_grapple_part, part_id)
	args.set_arg(arg_grapple_state, 1)

def EndGrapple(target, args):
	grapple_state = args.get_arg(arg_grapple_state)
	if not grapple_state: return

	spell_id = args.get_arg(arg_spell_id)
	part_id = args.get_arg(arg_grapple_part)

	if part_id != 0:
		game.particles_end(part_id)

	target.d20_send_signal(S_Spell_Grapple_Removed, spell_id)

def Targeted(target, args, evt_obj):
	spell_id = args.get_arg(arg_spell_id)

	packet = tpdp.SpellPacket(spell_id)

	grappled = GrappleCheck(packet.caster, packet.caster_level, target)

	if grappled:
		target.anim_goal_push_hit_by_weapon(target)
	else:
		target.anim_goal_push_dodge(target)

	if grappled:
		StartGrapple(target, args)

	return 0

def IsGrappled(target, args, evt_obj):
	evt_obj.return_val = args.get_arg(arg_grapple_state)

	return 0

def BreakFree(target, args, evt_obj):
	spell_id = args.get_arg(arg_spell_id)
	packet = tpdp.SpellPacket(spell_id)

	check = GrappleCheck(packet.caster, packet.caster_level, target, True)

	if check:
		target.float_mesfile_line(21003)
		target.d20_send_signal(S_Spell_Grapple_Removed, spell_id)
		part_id = args.get_arg(arg_grapple_part)
		if part_id != 0:
			game.particles_end(part_id)
		args.set_arg(arg_grapple_state, 0) # not grappled
		args.set_arg(arg_grapple_part, 0) # clear particle id

	return 0

def OnRound(target, args, evt_obj):
	spell_id = args.get_arg(arg_spell_id)
	packet = tpdp.SpellPacket(spell_id)
	caster = packet.caster
	grapple_state = args.get_arg(arg_grapple_state)

	check = GrappleCheck(packet.caster, packet.caster_level, target)

	if check:
		if grapple_state:
			dice = dice_new('1d6+4')
			target.spell_damage(
					caster, D20DT_BLUDGEONING, dice, D20DAP_UNSPECIFIED,
					D20A_CAST_SPELL, spell_id)
		else:
			StartGrapple(target, args)

	return 0

def Remove(target, args, evt_obj):
	# in case somehow still grappled
	EndGrapple(target, args)

	packet = tpdp.SpellPacket(args.get_arg(arg_spell_id))
	packet.remove_target(target)

	args.condition_remove()

	return 0

def DenyDex(target, args, evt_obj):
	evt_obj.bonus_list.add_cap(3, 0, 232)
	evt_obj.bonus_list.add_cap(8, 0, 232)
	return 0

disabled = [
	  tpdp.D20ActionType.StandardAttack
	, tpdp.D20ActionType.StandardRangedAttack
	, tpdp.D20ActionType.FullAttack
	, tpdp.D20ActionType(D20A_TRIP)
	, tpdp.D20ActionType(D20A_DISARM)
	, tpdp.D20ActionType(D20A_WHIRLWIND_ATTACK)
	]

def Disabled(attachee, args, evt_obj):
	act = evt_obj.get_d20_action()

	for ty in disabled:
		if act.action_type == ty:
			evt_obj.return_val = 1

	return 0

def DismissTarget(attachee, args, evt_obj):
	if evt_obj.data1 == args.get_arg(arg_spell_id):
		EndGrapple(attachee, args)
		args.remove_spell()
		args.remove_spell_mod()
	return 0

def EndTarget(attachee, args, evt_obj):
	print evt_obj.data1
	print evt_obj.data2
	if evt_obj.data1 == args.get_arg(arg_spell_id):
		EndGrapple(attachee, args)
		args.condition_remove()
	return 0

# 0: spell_id
# 1: spell_duration
# 2: grapple_state
# 3: spell_aoe_id
# 4: grappe_particle_id
tgt = PythonModifier('Black Tentacles Target', 5)
tgt.AddHook(ET_OnConditionAdd, EK_NONE, Targeted, ())
tgt.AddHook(ET_OnObjectEvent, EK_OnLeaveAoE, Leave, ())
tgt.AddHook(ET_OnGetMoveSpeed, EK_NONE, Slowed, ())
tgt.AddHook(ET_OnD20Query, EK_Q_IsActionInvalid_CheckAction, Disabled, ())
tgt.AddHook(ET_OnD20Query, EK_Q_Is_BreakFree_Possible, IsGrappled, ())
tgt.AddHook(ET_OnD20Signal, EK_S_BreakFree, BreakFree, ())
tgt.AddHook(ET_OnD20Signal, EK_S_Killed, spellKilled, ())
tgt.AddHook(ET_OnD20Signal, EK_S_Dismiss_Spells, EndTarget, ())
tgt.AddHook(ET_OnD20Signal, EK_S_Spell_End, EndTarget, ())
tgt.AddHook(ET_OnBeginRound, EK_NONE, OnRound, ())
tgt.AddHook(ET_OnGetAC, EK_NONE, DenyDex, ())
tgt.AddSpellTeleportPrepareStandard()
tgt.AddSpellTeleportReconnectStandard()
tgt.AddSpellCountdownStandardHook()
