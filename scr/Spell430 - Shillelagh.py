from toee import *

def OnBeginSpellCast( spell ):
	game.particles( "sp-transmutation-conjure", spell.caster )

def	OnSpellEffect( spell ):
	spell.duration = 10 * spell.caster_level

	remove = []
	for item in spell.target_list:
		target = item.obj

		fizzle = False

		wt = target.get_weapon_type()
		if wt != wt_club and wt != wt_quarterstaff:
			fizzle = True
		if target.item_condition_has('Weapon Enhancement Bonus'):
			fizzle = True

		if fizzle:
			game.sound(17122,1)
			target.float_mesfile_line('mes\\spell.mes', 30000)
			game.particles('Fizzle', target)
			remove.append(target)
			continue
		else:
			target.d20_status_init()
			game.particles('sp-Shillelagh', target)
			target.condition_add_with_args(
					'sp-Shillelagh', spell.id, spell.duration)

	spell.target_list.remove_list(remove)
	spell.spell_end(spell.id)

def OnBeginRound( spell ):
	print "Shillelagh OnBeginRound"

def OnEndSpellCast( spell ):
	print "Shillelagh OnEndSpellCast"
