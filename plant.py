from ursina import *
from panda3d.core import TransparencyAttrib
from pbr_material import PBRMaterialLoader
    
class PlantActor(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='../texture/marijuana/pot/bush_obj.obj',
            texture='../texture/marijuana/pot/Users/Dima/Desktop/marijuana_leaf.jpg', 
            color=color.white,
            collider='box', # Hitbox-ul initial
            double_sided=True, 
            **kwargs
        )
        self.set_transparency(TransparencyAttrib.MAlpha)
        
        # Facem hitbox-ul sa fie doar la baza (ghiveciul)
        # Reducem scale-ul collider-ului pe Y si pe X/Z
        self.collider = BoxCollider(self, size=(0.5, 0.5, 0.5)) 

        self.scale = (0.2, 0.2, 0.2) 
        self.growth = 0.0          
        self.health = 100.0
        self.ph_level = 7.0       
        self.water_level = 30.0    
        self.light_cycle_on = True
        self.smell_radius = 0.0     

    def custom_update(self):
        if self.health <= 0:
            return
        dt = time.dt

        ph_eff = 1.0
        if self.ph_level < 6.0 or self.ph_level > 6.8:
            ph_eff = max(0.1, 1.0 - abs(self.ph_level - 6.4) * 0.4)

        water_eff = 1.0
        if self.water_level < 40:
            water_eff = 0.5; self.health -= 2.0 * dt
        elif self.water_level > 80:
            water_eff = 0.2; self.health -= 5.0 * dt

        if self.light_cycle_on and self.health > 0:
            growth_rate = 0.0011 * ph_eff * water_eff
            self.growth += growth_rate * dt
            self.smell_radius = self.growth * 10.0 

        if self.water_level > 0: self.water_level -= 0.13 * dt

        # Scalare mult mai mica si controlata conforme cererii
        s = 0.05 + (self.growth * 1.5)
        self.scale = (s, s, s)
        
        if self.health <= 0: self.color = color.gray
        else: self.color = color.white
