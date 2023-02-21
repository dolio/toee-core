from toee import *

def OnBeginSpellCast(spell):
	game.particles('sp-transmutation-conjure', spell.caster)

def OnSpellEffect(spell):

	remove = []

	for item in spell.target_list:
		target = item.obj
		remove.append(target)

		avail = []

		# num_cast = target.obj_get_spell_size(obj_f_critter_spells_cast_idx)
		num_cast = 1000

		for i in range(0, num_cast): 
			spell = target.obj_get_spell(obj_f_critter_spells_cast_idx, i)
			if spell.spell_enum == 0:
				break
			if spell.spell_level > 5 or spell.is_naturally_cast():
				continue

			avail.append(spell)
			i += 1

		if len(avail) > 0:
			spell = avail[0]
			enum = spell.spell_enum
			cls = spell.spell_class & 0x7f
			lvl = spell.spell_level
			target.spell_memorized_add(enum, cls, lvl)
		else:
			game.particles('Fizzle', target)
			game.sound(17122,1)
			target.float_mesfile_line('mes\\spell.mes', 30000)
			spell.target_list.remove_target(target)

	spell.target_list.remove_list(remove)
	spell.spell_end(spell.id)

