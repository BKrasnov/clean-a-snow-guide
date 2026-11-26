"""Run the standard checker with a lower exposure so white snow is not clipped."""
from pathlib import Path
import sys
import bpy
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'.agents/skills/game-model-workflow/scripts'))
import model_check
original=model_check.studio_scene.render_views
def snow_views(*args,**kwargs):
    bpy.context.scene.view_settings.exposure=-1.25
    return original(*args,**kwargs)
model_check.studio_scene.render_views=snow_views
model_check.main(sys.argv)
