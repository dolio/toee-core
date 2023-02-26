from templeplus.pymod import PythonModifier
from toee import *
import tpdp

# Notes that the caster has antagonized targets that enter the area
# of effect, so that experience can be rewarded properly. Enemies
# that die of ability drain will not otherwise award experience.
def SetHit(spell_obj, args, evt_obj):
	target = evt_obj.target
	spell_id = args.get_arg(0)
	packet = tpdp.SpellPacket(spell_id)

	if target.type == obj_t_npc:
		target.obj_set_obj(obj_f_last_hit_by, packet.caster)

	return 0

cloudkill = PythonModifier()
cloudkill.ExtendExisting('sp-Cloudkill')
cloudkill.AddHook(ET_OnObjectEvent, EK_OnEnterAoE, SetHit, ())
