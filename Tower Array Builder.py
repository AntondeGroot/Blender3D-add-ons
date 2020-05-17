bl_info = {
    "name": "Construction Beam",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import mathutils
from math import radians, atan, sqrt, pi, sin, cos

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
def unlinkedcopy(object1):
    object2 = object1.copy()
    object2.data = object1.data.copy() #omit if you want a linked copy where they both point to the same mesh object
    return object2
    
    
    
def select_obj(ob):
    bpy.context.view_layer.objects.active = ob
    bpy.data.objects[ob.name].select_set(True)
def all_single_users(scene):
    allobjects = scene.objects
    for ob in allobjects:
        select_obj(ob)
        make_single_user()

    
def select_only_obj(object = None,scene = None):
    if object and scene:
        deselect_all(scene)
        bpy.data.objects[object.name].select_set(True)
def create_empty(name = 'empty object',size = 1,type = 'ARROWS',location =  mathutils.Vector((0,0,0)),colname = ''):
    Empty = None
    if colname:
        Empty = bpy.data.objects.new( name, None ) 
        bpy.data.collections[colname.name].objects.link(Empty)   
        #bpy.context.scene.collection.objects.link( Empty )
        Empty.empty_display_size = size
        Empty.empty_display_type = type  
        Empty.location = location
    return Empty

def movecollection(object,new_col):
    try:
        select_obj(object)
        obj = bpy.context.object
        old_col = obj.users_collection[0]
        print(f"object was in collection {obj.users_collection}")
        bpy.data.collections[new_col.name].objects.link(object)
        bpy.data.collections[old_col.name].objects.unlink(object)  
    except:
        pass        
           
class ObjectCursorArray(bpy.types.Operator):
    """Create a Transmission Tower"""
    bl_idname = "object.tower_array"
    bl_label = "Tower Array"
    bl_options = {'REGISTER', 'UNDO'}
    print("new script is run")

      
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
    diagonalxy: bpy.props.FloatProperty(name="Diagonal size", 
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
    z_array: bpy.props.IntProperty(name="Z array", 
        default=1,
        description = 'Z',
        min = 1)  
    N_sides: bpy.props.IntProperty(name="Nr of sides", 
        default=4,
        description = 'Z',
        min = 3,
        soft_max = 32)  
    # delete all empty collections first
    collection2delete = []
    for collection in bpy.context.scene.collection.children:
        nr_objects = len(list(collection.all_objects))
        if nr_objects == 0:
            collection2delete.append(collection)
    
    for collection in collection2delete:
        bpy.context.scene.collection.children.unlink(collection)

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor.location
        cursor_org = cursor
        object_beam = context.active_object
        
        TowerCol = bpy.data.collections.new('TransmissionTower')
        print(f"towcol {TowerCol}")
        bpy.context.scene.collection.children.link(TowerCol)
        
        
        all_single_users(scene)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True) 
        
        bpy.ops.mesh.primitive_cube_add()
        # newly created cube will be automatically selected
        boxcube = bpy.context.selected_objects[0]  
        
        boxcube.location = cursor
        movecollection(boxcube,TowerCol)
        select_obj(boxcube)
        bpy.ops.object.modifier_add(type='WIREFRAME') 
        bpy.data.objects[boxcube.name].modifiers["Wireframe"].thickness = 0.06
        w = self.boxwidth/boxcube.dimensions[0]
        h = self.boxheight/boxcube.dimensions[2]
        boxcube.scale = (2*w,2*w,2*h)
        

        
        #copy object mesh (unlinked)
        obj_topbar = unlinkedcopy(object_beam)
        obj_topbar.name = 'Topbar'
        
        
        
        
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
        else:
            f = beamsize
        print(f"newsize is {obj_topbar.dimensions}") 
                       
        all_single_users(scene)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True) 

        deselect_all(scene)
        # Determine how much the diagonal beam need to be slanted
        angle = atan(self.boxheight/self.boxwidth) 
        diagonallength = sqrt(self.boxheight**2+self.boxwidth**2)/2*self.diagonalpercent
        # Determine the center of the scene
        EmptyCenter = create_empty(name = 'EmptyCenter',size = max(self.boxwidth,self.boxheight)*1.5,location =  cursor,colname = TowerCol)
        xm,ym,zm = cursor #middle of box
        # point vectors to where the beams should be placed
        Vector = mathutils.Vector
        
        
        
        vec_centertop = Vector((self.boxwidth/2, 0, self.boxheight/2)) + cursor
        vec_corner = Vector((self.boxwidth/2, self.boxwidth/2, self.boxheight/2)) + cursor
        vec_side = Vector((self.boxwidth/2, self.boxwidth/2, 0)) + cursor
        # Create extra Empties
        EmptyCorner   = create_empty(name = 'EmptyCorner',size = max(self.boxwidth,self.boxheight)/4,location =  vec_corner,colname = TowerCol)        
        EmptyFront    = create_empty(name = 'EmptyFront',size = max(self.boxwidth,self.boxheight)/4,location =  cursor + Vector((self.boxwidth/2,0,0)),colname = TowerCol)                
        EmptyDiagonal = create_empty(name = 'EmptyDiagonal',size = max(self.boxwidth,self.boxheight)/4,location =  cursor + Vector((self.boxwidth/2,0,0)),colname = TowerCol)                        
        # to avoid having to rotate the beam at the eind points: it's easier to use an extra empty and scale/rotate the object around the center
        p = self.diagonalpercent
        EmptyDiagonal.location = (EmptyFront.location*p + EmptyCorner.location*(2-p))/2
        

        #obj_topbar = bpy.data.objects.new('Topbar',beam_ob.data)        
        #scene.collection.objects.link(obj_topbar)     
        bpy.data.collections[TowerCol.name].objects.link(obj_topbar)   
        all_single_users(scene)
        obj_topbar.location = vec_centertop
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)   
        select_obj(obj_topbar)
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.data.objects[obj_topbar.name].modifiers["Mirror"].use_axis = (False, False, True)
        bpy.data.objects[obj_topbar.name].modifiers["Mirror"].mirror_object = EmptyCenter
        
        
         
        #copy object mesh (unlinked)
        #select_obj(obj_topbar)
        #obj_sidebar = bpy.ops.object.duplicate()
        obj_sidebar = unlinkedcopy(obj_topbar)
        obj_sidebar.name = 'Sidebar' 
        all_single_users(scene)
        #scene.collection.objects.link(obj_sidebar) 
        bpy.data.collections[TowerCol.name].objects.link(obj_sidebar)          
        all_single_users(scene)  
        select_obj(obj_sidebar)    
        obj_sidebar.rotation_euler = (radians(90),0,0)
        obj_sidebar.location = vec_side
        select_obj(obj_sidebar)  
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        print(f" scale = {obj_sidebar.scale}")

        x,y,z = obj_sidebar.dimensions
        obj_sidebar.scale = (1,1,self.boxheight/z+2*f/z) 

        

        all_single_users(scene)
        select_obj(obj_sidebar)
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.data.objects[obj_sidebar.name].modifiers["Mirror"].use_axis = (False, True, False)
        bpy.data.objects[obj_sidebar.name].modifiers["Mirror"].mirror_object = EmptyCenter

        obj_diagonalbar = unlinkedcopy(obj_topbar)
        fr = diagonallength/obj_diagonalbar.dimensions[1]
        obj_diagonalbar.scale = (self.diagonalxy,fr,self.diagonalxy)
        obj_diagonalbar.rotation_euler = (angle,0,0)
        obj_diagonalbar.name = 'Diagonalbar' 
        all_single_users(scene)
        #scene.collection.objects.link(obj_diagonalbar)
        bpy.data.collections[TowerCol.name].objects.link(obj_diagonalbar)   
        obj_diagonalbar.location =   EmptyDiagonal.location   
        
                
        select_obj(obj_diagonalbar)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.data.objects[obj_diagonalbar.name].modifiers["Mirror"].use_axis = (False, True, True)
        bpy.data.objects[obj_diagonalbar.name].modifiers["Mirror"].mirror_object = EmptyCenter
        #scene.collection.objects.link(obj_diagonal1)
        
        #obj_diagonal1.rotation_euler = (angle,0,0)
        
       
        #add instancing plane

        instanceplane = bpy.ops.mesh.primitive_plane_add()
        # newly created cube will be automatically selected
        instanceplane = bpy.context.selected_objects[0]  
        instanceplane.scale = (0.25,1,1)
        instanceplane.name = 'InstancePlane'
        #scene.collection.objects.link(instanceplane) 
        instanceplane.location = Vector((self.boxwidth/2,0,-self.boxheight/2-f)) + cursor 
        movecollection(instanceplane, TowerCol)
        #bpy.data.collections[TowerCol.name].objects.link(instanceplane)   
        bpy.data.objects[instanceplane.name].hide_render = True
       # deselect_all(scene)   
        #bpy.ops.object.modifier_add(type='MIRROR')
        #print(obj_new.name)
        #bpy.data.objects[obj.name].modifiers['Mirror'].use_axis = (False,True,False)
        #bpy.data.objects[obj_new.name].select_set(False)
        bpy.data.objects[instanceplane.name].instance_type = 'FACES'
        
        # Create extra Empties
        EmptyTop   = create_empty(name = 'EmptyTop',size = max(self.boxwidth,self.boxheight)/4,colname = TowerCol)
        EmptyTop.location = Vector((self.boxwidth/2,0,self.boxheight/2+f))  + cursor      
#        scene.collection.objects.link(EmptyTop) 
        
        #determine polygon's next center of the edge.
        """If you place an empty at the next edge center of a polygon , then an array with N numbers will finish the polygon"""
        n = self.N_sides
        Ngon_angle = (n - 2)*pi/n
        length = self.boxwidth/2
        x1,y1,z1 = EmptyCorner.location
        x2,y2,z2 = instanceplane.location
        xx = length*sin(pi-Ngon_angle)
        yy = length*cos(pi-Ngon_angle)
        emptypos = (x1-xx,y1+yy,z2)
        EmptyPolygon   = create_empty(name = 'EmptyPolygon',size = 1,location =  emptypos,colname = TowerCol)        
        EmptyPolygon.rotation_euler = (0,0,3*pi-Ngon_angle)

        select_obj(instanceplane)
        bpy.ops.view3d.snap_cursor_to_active()
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        array1 = bpy.data.objects[instanceplane.name].modifiers.new(name='array1',type='ARRAY')
        obname = instanceplane.name
        array1.use_relative_offset = False
        array1.use_object_offset = True
        array1.offset_object = EmptyPolygon
        array1.count = self.N_sides
        
        
        array2 = bpy.data.objects[instanceplane.name].modifiers.new(name='array2',type='ARRAY')
        array2.use_relative_offset = False
        array2.use_object_offset = True
        array2.offset_object = EmptyTop
        array2.count = self.z_array
        """
        bpy.ops.object.modifier_add(type='ARRAY')
        obname2 = obname.copy()
        bpy.data.objects[obname2].modifiers["Array"].use_relative_offset = False
        bpy.data.objects[obname2].modifiers["Array"].use_object_offset = True
        bpy.data.objects[obname2].modifiers["Array"].offset_object = EmptyTop
        bpy.data.objects[obname2].modifiers["Array"].count = self.z_array
        """
        
        #parent all objects in the TransmissionTower collection to the instanceplane except for the instance plane
        
        for object in TowerCol.objects:
            if instanceplane.name != object.name and 'empty' not in object.name.lower() and boxcube.name != object.name:
                select_obj(object)
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                object.parent = instanceplane
                object.matrix_parent_inverse = instanceplane.matrix_world.inverted()
        for object in TowerCol.objects:
            if instanceplane.name == object.name or 'empty' in object.name.lower():
                
                select_obj(object)
                if 'empty' not in object.name.lower():
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                object.parent = boxcube
                object.matrix_parent_inverse = boxcube.matrix_world.inverted()
                
        select_obj(EmptyCenter)
        bpy.ops.view3d.snap_cursor_to_active()                
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
