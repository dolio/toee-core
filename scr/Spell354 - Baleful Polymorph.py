from toee import *

def OnBeginSpellCast(spell):
	game.particles('sp-transmutation-conjure', spell.caster)

protos = [14362, 14364, 14367]

def OnSpellEffect(spell):
	spell.duration = -1

	remove = []

	arg = spell.spell_get_menu_arg(RADIAL_MENU_PARAM_MIN_SETTING)
	arg = max(0, min(2, arg))

	proto_num = protos[arg]

	for item in spell.target_list:
		target = item.obj

		saved = target.saving_throw_spell(
				spell.dc, D20_Save_Fortitude, D20STD_F_NONE, spell.caster, spell.id)
		if saved:
			remove.append(target)
			continue

		game.particles('sp-Polymorph Other', target)
		target.condition_add_with_args(
				'sp-Baleful Polymorph', spell.id, -1, proto_num, arg+1)
