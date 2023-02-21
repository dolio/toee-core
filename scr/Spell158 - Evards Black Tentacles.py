from toee import *
import tpdp

def OnBeginSpellCast(spell):
	game.particles('sp-conjuration-conjure', spell.caster)

def OnSpellEffect(spell):
	spell.duration = spell.caster_level
	loc = spell.target_loc
	loc_off_x = spell.target_loc_off_x
	loc_off_y = spell.target_loc_off_y

	obj = game.obj_create(OBJECT_SPELL_GENERIC, loc, loc_off_x, loc_off_y)

	caster_init_value = spell.caster.get_initiative()
	obj.d20_status_init()
	obj.set_initiative(caster_init_value)

	partsys_id = game.particles('sp-Black Tentacles Area', obj)
	obj.condition_add_with_args(
			'Black Tentacles Area', spell.id, spell.duration, partsys_id, 0, 0)

	spell.caster.condition_add_with_args('Dismiss', spell.id)

	return 0

def OnEndSpellCast(spell):
	print "ending black tentacles"
	spell.caster.d20_send_signal(S_Spell_End, spell.id)
