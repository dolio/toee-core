from toee import *

def OnBeginSpellCast(spell):
	game.particles('sp-transmutation-conjure', spell.caster)

def OnSpellEffect(spell):
	spell.duration = 10 * spell.caster_level

	spell.caster.condition_add_with_args('Dismiss', spell.id)

	for item in spell.target_list:
		target = item.obj

		armor = target.item_worn_at(5)
		game.particles('sp-Polymorph Self', target)
		target.condition_add_with_args(
				'sp-Polymorph', spell.id, spell.duration, 14260)
		armor.item_condition_add_with_args('Null Condition', 0, 0, 0, 0, spell.id)

def OnBeginRound(spell):
	return

def OnEndSpellCast(spell):
	print "Polymorph End"
