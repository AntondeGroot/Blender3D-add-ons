bl_info = {
    "name": "Construction Beam",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import mathutils
from math import radians, tan
def make_single_user():
    """ When you copy an object they will have the same material, you've already seen it happen for materials and 
    if you change the material of 1 object it changes all materials unless you unlink them by clicking on the number
    The same can happen if you copy a mesh. This will prevent you from being able to apply modifiers
    """#object/relations/make single user/object n data
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)
    

def deselect_all(scene):
    #allobjects = scene.objects
    bpy.context.view_layer.objects.active = None    
    #for ob in allobjects:
    #    make_single_user()
    #    bpy.data.objects[ob.name].select_set(False)

def select_obj(ob):
    bpy.context.view_layer.objects.active = ob

def all_single_users(scene):
    allobjects = scene.objects
    for ob in allobjects:
        select_obj(ob)
        make_single_user()

    
def select_only_obj(object = None,scene = None):
    if object and scene:
        deselect_all(scene)
        bpy.data.objects[object.name].select_set(True)
def create_empty(name = 'empty object',size = 1,type = 'ARROWS',location =  mathutils.Vector((0,0,0))):
    Empty = bpy.data.objects.new( name, None ) 
    bpy.context.scene.collection.objects.link( Empty )
    Empty.empty_display_size = size
    Empty.empty_display_type = type  
    Empty.location = location
    return Empty

           
class ObjectCursorArray(bpy.types.Operator):
    """Create a Transmission Tower"""
    bl_idname = "object.tower_array"
    bl_label = "Tower Array"
    bl_options = {'REGISTER', 'UNDO'}
    print(f"testing\n"*10)

      
    boxheight: bpy.props.FloatProperty(name="Height", 
        default=3,
        description = 'Height of the box',
        min = 1)
    boxwidth: bpy.props.FloatProperty(name="Width", 
        default=2,    
        description = 'Width of the box',
        min = 1)
    diagonalpercent: bpy.props.FloatProperty(name="Diagonal%", 
        default=0.75,    
        description = 'How wide the diagonal beam goes to the center',
        min = 0,
        max = 1)
    beampercent: bpy.props.FloatProperty(name="Thickness", 
        default=0.1,
        description = 'thickness of the beam w.r.t. the box',
        min = 0,
        soft_min = 0.1,
        max = 1)  
    #make a collection
    #TowerCollection = bpy.data.collections.new('TransmissionTower')
    #bpy.context.scene.collection.children.link(TowerCollection)
    
    
   

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor.location
        object_beam = context.active_object
        all_single_users(scene)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True) 
        
        bpy.ops.mesh.primitive_cube_add()
        # newly created cube will be automatically selected
        boxcube = bpy.context.selected_objects[0]  
        boxcube.location = cursor
        select_obj(boxcube)
        bpy.ops.object.modifier_add(type='WIREFRAME') 
        bpy.data.objects[boxcube.name].modifiers["Wireframe"].thickness = 0.06
        w = self.boxwidth/boxcube.dimensions[0]
        h = self.boxheight/boxcube.dimensions[2]
        boxcube.scale = (w,w,h)
        
        #copy object mesh (unlinked)
        obj_topbar= bpy.data.objects.new('Topbar',object_beam.data)        
        
        
        
        
        #resize the beam if it is too large:
        x,y,z = obj_topbar.dimensions
        print(f"size is {x,y,z}") 
        beamsize = min(self.boxwidth,self.boxheight)*self.beampercent
        if x > y: #rotate the original beam correctly
            obj_topbar.rotation_euler = (0,0,radians(90))
        all_single_users(scene)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)        
        if x > beamsize:
            
            f = beamsize/max(x,y)
            print(f"is too large {f,max(x,y),beamsize}")
            obj_topbar.scale = (f,self.boxwidth/y-f,f) 
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True) 
        print(f"newsize is {obj_topbar.dimensions}") 
                       
        all_single_users(scene)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True) 

        deselect_all(scene)
        # Determine how much the diagonal beam need to be slanted
        angle = radians(90) - tan(self.boxwidth/self.boxheight) 
        
        # Determine the center of the scene
        EmptyCenter = create_empty(name = 'EmptyCenter',size = max(self.boxwidth,self.boxheight)*1.5,location =  cursor)

        # point vectors to where the beams should be placed
        Vector = mathutils.Vector
        
        vec_centertop = Vector((self.boxwidth/2, 0, self.boxheight/2))
        vec_corner = Vector((self.boxwidth/2, self.boxwidth/2, self.boxheight/2))
        vec_side = Vector((self.boxwidth/2, self.boxwidth/2, 0))
        # Create extra Empties
        EmptyCorner   = create_empty(name = 'EmptyCorner',size = max(self.boxwidth,self.boxheight)/4,location =  vec_corner)        
        EmptyFront    = create_empty(name = 'EmptyFront',size = max(self.boxwidth,self.boxheight)/4,location =  cursor + Vector((self.boxwidth/2,0,0)))                
        EmptyDiagonal = create_empty(name = 'EmptyDiagonal',size = max(self.boxwidth,self.boxheight)/4,location =  cursor + Vector((self.boxwidth/2,0,0)))                        
        # to avoid having to rotate the beam at the eind points: it's easier to use an extra empty and scale/rotate the object around the center
        p = self.diagonalpercent
        EmptyDiagonal.location = (EmptyFront.location*p + EmptyCorner.location*(2-p))/2
        

        #obj_topbar = bpy.data.objects.new('Topbar',beam_ob.data)        
        scene.collection.objects.link(obj_topbar)        
        all_single_users(scene)
        obj_topbar.location = cursor + vec_centertop
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)   
        select_obj(obj_topbar)
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.data.objects[obj_topbar.name].modifiers["Mirror"].use_axis = (False, False, True)
        bpy.data.objects[obj_topbar.name].modifiers["Mirror"].mirror_object = EmptyCenter
        
        
         
        #copy object mesh (unlinked)
        #select_obj(obj_topbar)
        #obj_sidebar = bpy.ops.object.duplicate()
        obj_sidebar = obj_topbar.copy() 
        all_single_users(scene)
        scene.collection.objects.link(obj_sidebar)        
        all_single_users(scene)  
        select_obj(obj_sidebar)    
        obj_sidebar.rotation_euler = (radians(90),0,0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj_sidebar.location = vec_side
        select_obj(obj_sidebar)  
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        z = obj_sidebar.dimensions[2]
        print(f" scale = {obj_sidebar.scale}")
        sx,sy,sz = obj_sidebar.scale
        obj_sidebar.scale = (sx,sy,sz*2)
        scene.update()
        """
        x,y,z = obj_sidebar.dimensions
        print(f'dim = {x,y,z,}')
        zh = (self.boxheight + obj_topbar.dimensions.z)/max(x,y,z)
        print(f"zh = {zh}")
        obj_sidebar.scale = (1,1,zh)
        all_single_users(scene)
        select_obj(obj_topbar)
        print(f"type is {obj_sidebar.type}") 
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.data.objects[obj_topbar.name].modifiers["Mirror"].use_axis = (False, False, True)
        bpy.data.objects[obj_topbar.name].modifiers["Mirror"].mirror_object = EmptyCenter
        
        select_obj(obj_sidebar)
        all_single_users(scene)
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.data.objects[obj_sidebar.name].modifiers["Mirror"].use_axis = (False, True, False)
        bpy.data.objects[obj_sidebar.name].modifiers["Mirror"].mirror_object = EmptyCenter
        #bpy.data.objects[obj_topbar.name].modifiers["Mirror"].mirror_object
        #obj_diagonal1 = obj_topbar.copy()
        
        
        
        #scene.collection.objects.link(obj_diagonal1)
        
        #obj_diagonal1.rotation_euler = (angle,0,0)
        
       
            
        
       # deselect_all(scene)   
        #bpy.ops.object.modifier_add(type='MIRROR')
        #print(obj_new.name)
        #bpy.data.objects[obj.name].modifiers['Mirror'].use_axis = (False,True,False)
        #bpy.data.objects[obj_new.name].select_set(False)
        """
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ObjectCursorArray.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []


def register():
    bpy.utils.register_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(ObjectCursorArray.bl_idname, 'T', 'PRESS', ctrl=True, shift=True)
        kmi.properties.boxheight = 3
        addon_keymaps.append((km, kmi))

def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
