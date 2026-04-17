from panda3d.core import Material, Texture, TextureStage, SamplerState
from ursina import application

class PBRMaterialLoader:
    """Încarcă un set complet de texturi PBR și le aplică unui model."""
    
    def __init__(self, base_path: str, model_node):
        """
        base_path: calea către fișiere fără extensie
        ex: "assets/textures/plant/og_kush"
        """
        self.model = model_node
        self.base_path = base_path
        # Legăm instanța loader-ului din fundalul Ursina (Panda3D base)
        self.loader = application.base.loader
        
    def load_and_apply(self):
        # 1. Creează Materialul de bază
        mat = Material()
        mat.setShininess(0.0)  # PBR nu folosește shininess vechi
        mat.setMetallic(1.0)    # Va fi controlat de textura metallic
        mat.setRoughness(1.0)   # Va fi controlat de textura roughness
        
        self.model.setMaterial(mat)
        
        # 2. Încarcă fiecare textură în slotul corect
        self._load_texture("albedo", TextureStage.getDefault(), mod="modulate")
        self._load_texture("normal", self._get_normal_stage(), mod="normal")
        self._load_texture("roughness", self._get_roughness_stage(), mod="modulate")
        self._load_texture("metallic", self._get_metallic_stage(), mod="modulate")
        self._load_texture("ao", self._get_ao_stage(), mod="modulate")
        
    def _load_texture(self, suffix: str, stage, mod: str):
        tex_path = f"{self.base_path}_{suffix}.jpg"
        try:
            tex = self.loader.loadTexture(tex_path)
            if tex:
                # Setări pentru calitate maximă
                tex.setMinfilter(SamplerState.FT_linear_mipmap_linear)
                tex.setMagfilter(SamplerState.FT_linear)
                tex.setAnisotropicDegree(16)  # Claritate la unghiuri oblice
                tex.setWrapU(SamplerState.WM_repeat)
                tex.setWrapV(SamplerState.WM_repeat)
                
                self.model.setTexture(stage, tex)
                print(f"[+] Textura PBR {suffix.upper()} ancorată cu succes: {tex_path}")
        except:
            print(f"[-] Avertisment: Textura {suffix} lipsește din calea: {tex_path}")
            
    def _get_normal_stage(self):
        stage = TextureStage('normal')
        stage.setMode(TextureStage.M_normal)
        return stage
        
    def _get_roughness_stage(self):
        stage = TextureStage('roughness')
        stage.setMode(TextureStage.M_modulate)
        return stage
        
    def _get_metallic_stage(self):
        stage = TextureStage('metallic')
        stage.setMode(TextureStage.M_modulate)
        return stage
        
    def _get_ao_stage(self):
        stage = TextureStage('ao')
        stage.setMode(TextureStage.M_modulate)
        return stage
