from toee import *
import tpdp

def OnBeginSpellCast(spell):
	print "Permanency Begin"

def OnSpellEffect(spell):

	target_item = spell.target_list[0]
	target = target_item.obj
	caster = spell.caster

	avail = []
	conds = target.conditions_get()
	if conds == None: conds = []

	for cond in conds:
		args = cond[1]
		if cond[0] == 'sp-Darkvision':
			if target == caster and spell.caster_level >= 10:
				new_cond = ('sp-Permanent Darkvision', spell.id, 0, 0)
				avail.append(('Darkvision', args[0], 97, new_cond))
		elif cond[0] == 'sp-Detect Magic':
			if target == caster and spell.caster_level >= 9:
				new_cond = ('sp-Permanent Detect Magic', spell.id, 0, 0)
				avail.append(('Detect Magic', args[0], 114, new_cond))
		elif cond[0] == 'sp-Read Magic':
			if target == caster and spell.caster_level >= 9:
				new_cond = ('sp-Permanent Read Magic', spell.id, 0, 0)
				avail.append(('Read Magic', args[0], 385, new_cond))
		elif cond[0] == 'sp-See Invisibility':
			if target == caster and spell.caster_level >= 10:
				new_cond = ('sp-Permanent See Invisibility', spell.id, 0, 0)
				avail.append(('See Invisibility', args[0], 414, new_cond))
		elif cond[0] == 'sp-Enlarge':
			if spell.caster_level >= 9:
				new_cond = ('sp-Permanent Enlarge Person', spell.id, 0, 0)
				avail.append(('Enlarge Person', args[0], 152, new_cond))
		elif cond[0] == 'sp-Greater Magic Fang':
			if spell.caster_level >= 11:
				new_cond = ('sp-Permanent Magic Fang', spell.id, args[2], 0)
				avail.append(('Greater Magic Fang', args[0], 204, new_cond))
		elif cond[0] == 'sp-Magic Fang':
			if spell.caster_level >= 9:
				new_cond = ('sp-Permanent Magic Fang', spell.id, 1, 0)
				avail.append(('Magic Fang', args[0], 286, new_cond))
		elif cond[0] == 'sp-Reduce':
			if spell.caster_level >= 9:
				new_cond = ('sp-Permanent Reduce Person', spell.id, 0, 0)
				avail.append(('Reduce Person', args[0], 386, new_cond))
		elif cond[0] == 'sp-Resistance':
			if spell.caster_level >= 9:
				new_cond = ('sp-Permanent Resistance', spell.id, 0, 0)
				avail.append(('Resistance', args[0], 399, new_cond))

	if len(avail) < 1:
		game.particles('Fizzle', target)
		game.sound(17122,1)
		target.float_mesfile_line('mes\\spell.mes', 30000)
		spell.target_list.remove_target(target)
	else:
		name, old, enum, new = avail[0]

		opacket = tpdp.SpellPacket(old)
		target.d20_send_signal(S_Dismiss_Spells, old)

		target.condition_add_with_args(*new)

		packet = tpdp.SpellPacket(spell.id)
		packet.caster = opacket.caster
		packet.spell_enum = opacket.spell_enum
		packet.spell_known_slot_level = opacket.spell_known_slot_level
		packet.spell_class = opacket.spell_class
		packet.caster_level = opacket.caster_level
		packet.update_registry()

	spell.spell_end(spell.id)

def OnBeginRound(spell):
	print "Permanency Begin Round"
