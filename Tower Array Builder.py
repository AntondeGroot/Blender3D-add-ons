bl_info = {
    "name": "Construction Beam",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import mathutils
from math import radians, atan, sqrt, pi, sin, cos, tan

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )


class MySettings(PropertyGroup):#https://blender.stackexchange.com/questions/35007/how-can-i-add-a-checkbox-in-the-tools-ui
    my_bool : BoolProperty(
        name="Enable or Disable",
        description="A bool property",
        default = False
        )

    my_int : IntProperty(
        name = "Set a value",
        description="A integer property",
        default = 23,
        min = 10,
        max = 100
        )

    my_float : FloatProperty(
        name = "Base height",
        description = "A float property",
        default = 3,
        min = 1
        )
    boxheight: FloatProperty(
        name="Base height", 
        default=3,
        description = 'Base height',
        min = 1)
        
    ###
    boxheight: FloatProperty(
        name="Base height", 
        default=3,
        description = 'Base height',
        min = 1)
    boxwidth: bpy.props.FloatProperty(name="Base width", 
        default=2,    
        description = 'Base width',
        min = 1)
    diagonalpercent: bpy.props.FloatProperty(name="Diagonal length", 
        default=0.75,    
        description = 'How wide the diagonal beam goes to the center',
        min = 0,
        max = 1)
    diagonalxy: bpy.props.FloatProperty(name="Diagonal width", 
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
    z_array: bpy.props.IntProperty(name="Height array", 
        default=3,
        description = 'Z',
        min = 1)  
    N_sides: bpy.props.IntProperty(name="N polygon shape", 
        default=4,
        description = 'Z',
        min = 3,
        soft_max = 32)  
    N_sides_used: bpy.props.IntProperty(name="N polygon used", 
        default=4,
        description = 'Z',
        min = 1,
        soft_max = 32)  
    platethickness: bpy.props.FloatProperty(name="Plate Thickness", 
        default=0.2,
        description = '',
        min = 0,
        soft_max = 1.2)  
    platesize: bpy.props.FloatProperty(name="Plate Size%", 
        default=1.1,
        description = '',
        soft_min = 0.1,
        soft_max = 2)  
        
class PanelMain(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Tower Array"
    bl_idname = "PT_panelmain"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = 'Tower Array'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text='sample text')

class PanelBase(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Base"
    bl_idname = "PT_panelbase"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = 'Tower Array'
    bl_parent_id = 'PT_panelmain'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        mytool = scene.my_tool
        
        row = layout.row()
        row.label(text='Box')
        
        # display the properties
        layout.prop(mytool, "boxheight", text="height")
        layout.prop(mytool, "boxwidth", text="width")
        row = layout.row()
        row.label(text='Polygon Base Shape')
        layout.prop(mytool, "N_sides", text="N polygon")
        layout.prop(mytool, "N_sides_used", text="nr of sides shown")
        
        


class PanelSpire(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Tower Spire"
    bl_idname = "PT_panelspire"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = 'Tower Array'
    bl_parent_id = 'PT_panelmain'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        mytool = scene.my_tool
        
        row = layout.row()
        row.label(text='sample text')
        
        # display the properties
        layout.prop(mytool, "my_bool", text="Put a spire on top")
        layout.prop(mytool, "my_int", text="Integer Property")
        layout.prop(mytool, "my_float", text="Float Property")


def assignmaterial(object,RGBA_color):
    mat = bpy.data.materials.new(name="MaterialName") #set new material to  variable
    object.data.materials.append(mat) #add the material to the object
    bpy.context.object.active_material.diffuse_color = RGBA_color #change color

    
    """# Get material
    bpy.ops.material.new("material ")
    
    mat = bpy.data.materials.get("Material")
    if mat is None:
        # create material
        mat = bpy.data.materials.new(name="Material")

    # Assign it to object
    if object.data.materials:
        # assign to 1st material slot
        ob.data.materials[0] = mat
    else:
        # no slots
        object.data.materials.append(mat)
    """    


def make_single_user():
    """ When you copy an object they will have the same material, you've already seen it happen for materials and 
    if you change the material of 1 object it changes all materials unless you unlink them by clicking on the number
    The same can happen if you copy a mesh. This will prevent you from being able to apply modifiers
    """#object/relations/make single user/object n data
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)

def cylinderarray(object,offset, N):
    array1 = bpy.data.objects[object.name].modifiers.new(name='array1',type='ARRAY')
    array1.use_relative_offset = False
    array1.use_object_offset = True
    array1.offset_object = offset
    array1.count = N
    
def heightarray(object,offset, N ):
    array2 = bpy.data.objects[object.name].modifiers.new(name='array2',type='ARRAY')
    array2.use_relative_offset = False
    array2.use_object_offset = True
    array2.offset_object = offset
    array2.count = N

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

      

    
    # delete all empty collections first
    collection2delete = []
    for collection in bpy.context.scene.collection.children:
        nr_objects = len(list(collection.all_objects))
        if nr_objects == 0:
            collection2delete.append(collection)

    for collection in collection2delete:
        bpy.context.scene.collection.children.unlink(collection)

    def execute(self, context):
        if self.N_sides_used > self.N_sides:
            self.N_sides_used = self.N_sides
        scene = context.scene
        cursor = scene.cursor.location
        cursor_org = cursor
        object_beam = context.active_object
        bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY')
        
        TowerCol = bpy.data.collections.new('TransmissionTower')
        print(f"towcol {TowerCol}")
        bpy.context.scene.collection.children.link(TowerCol)
        
        ## rgba colors for the materials
        matcolor1 = (1,0,0,1)
        matcolor2 = (0,1,0,1)
        matcolor3 = (0,0,1,1)
        

        
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
            barscale = f
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True) 
        else:
            f = beamsize
        print(f"newsize is {obj_topbar.dimensions}") 
#                       
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
        select_obj(obj_topbar)
        obj_sidebar = unlinkedcopy(obj_topbar)
        #select_obj(obj_sidebar)
        obj_sidebar.name = 'Sidebar' 
        assignmaterial(obj_topbar, matcolor1)
        assignmaterial(obj_sidebar, matcolor2)
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
        assignmaterial(obj_diagonalbar,matcolor3)
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
        
        #make a plate
        if True:
            bpy.ops.mesh.primitive_cube_add()
            frontplate = bpy.context.selected_objects[0]  
            frontplate.location = EmptyFront.location
            frontplate.name = 'Frontplate'
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            
            #xc,yc,zc = frontplatecorner - EmptyFront.location
            
            #width = 2*abs(EmptyFront.location[1]-(EmptyCorner.location[1]-2*EmptyDiagonal.location[1]))
            width = (EmptyDiagonal.location-EmptyFront.location)[1]/2*self.platesize
            #height = 2*abs(EmptyFront.location[2]-(EmptyCorner.location[2]-2*EmptyDiagonal.location[2]))
            height = (EmptyDiagonal.location-EmptyFront.location)[2]/2*self.platesize

            xf,yf,zf = frontplate.dimensions
            xd = obj_diagonalbar.dimensions[0]
            sx = xd*self.platethickness/xf
            sy = width*self.platesize/yf
            sz = height/zf
            print(f"height = {height},\n width = {width},\n sz = {sz},\n zf = {zf},\n sz = {sz}")
            frontplate.scale = (sx,width,height)
            movecollection(frontplate,TowerCol)
            
            
            

        
       
        #add instancing plane
        EmptyBottom   = create_empty(name = 'EmptyBottom',size = 1,colname = TowerCol)
        EmptyBottom.location = Vector((self.boxwidth/2,0,-self.boxheight/2-f)) + cursor 

        
        
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
        x2,y2,z2 = EmptyBottom.location
        xx = length*sin(pi-Ngon_angle)
        yy = length*cos(pi-Ngon_angle)
        emptypos = (x1-xx,y1+yy,z2)
        EmptyPolygon   = create_empty(name = 'EmptyPolygon',size = 1,location =  emptypos,colname = TowerCol)        
        EmptyPolygon.rotation_euler = (0,0,3*pi-Ngon_angle)

        select_obj(EmptyBottom)
        bpy.ops.view3d.snap_cursor_to_active()
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        
        
        ASSIGN_MODS = True
        APPLY_MODS  = False
        DELETE_EMPTIES = False
        DRAW_SPIRE = True
        if DRAW_SPIRE:
            #distance from center of topbar to center of the polygon
            pos_x = EmptyTop.location[0] - (self.boxwidth/2) * tan(Ngon_angle/2) 
            pos_y = EmptyTop.location[1]
            pos_z = EmptyTop.location[2] + (self.boxheight) * (self.z_array)
            
            EmptySpire   = create_empty(name = 'EmptySpire',size = 1,colname = TowerCol)
            EmptySpire.location = Vector((pos_x,pos_y,pos_z))  
            x0,y0,z0 = EmptySpire.location
            x1,y1,_ = EmptyCorner.location
            z1 = EmptyPolygon.location[2] + (EmptyTop.location[2]-EmptyPolygon.location[2])*self.z_array #exactly the highest point, accounts for width of beams
            
            EmptySpireHalf   = create_empty(name = 'EmptySpireHalf',size = 5,colname = TowerCol)
            EmptySpireHalf.location = Vector(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))  
            
            obj_spire = unlinkedcopy(object_beam)
            obj_spire.name = 'SpireBar'
            obj_spire.location = EmptySpireHalf.location
            scene.collection.objects.link(obj_spire)     

            O = (pos_z-z1)
            A = sqrt((EmptySpire.location[0]-EmptyCorner.location[0])**2 + (EmptySpire.location[1]-EmptyCorner.location[1])**2)
            S = sqrt(O**2+A**2)
            z_angle = atan(O/A)
            yscale = S/obj_spire.dimensions[1]
            obj_spire.scale = (barscale,yscale,barscale)
            obj_spire.rotation_euler = (-z_angle,0,-Ngon_angle/2)
            movecollection(obj_spire,TowerCol)
            
        if ASSIGN_MODS:
            for object in TowerCol.objects:
                if object.type != 'EMPTY' and boxcube.name != object.name:
                    select_obj(object)
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    bpy.ops.object.origin_set(type = 'ORIGIN_CURSOR')
                    cylinderarray(object, EmptyPolygon, self.N_sides_used )
                    if object != obj_spire:
                        heightarray(object, EmptyTop, self.z_array)
                    
                    print(f'modifiers = {object.modifiers}')                    
                    if APPLY_MODS:
                        #apply all modifiers of an object:
                        for mod in object.modifiers:
                            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
            #PARENT TO CUBE
            for object in TowerCol.objects:
                if object.type == 'EMPTY' or object.type == 'MESH' and object != boxcube:
                    select_obj(object)
                    object.parent = boxcube
                    object.matrix_parent_inverse = boxcube.matrix_world.inverted()
        #restore 3D cursor
        select_obj(EmptyCenter)
        bpy.ops.view3d.snap_cursor_to_active()   
        if DELETE_EMPTIES:#remove all empties
            for object in TowerCol.objects:
                if object.type == 'EMPTY':
                    bpy.data.collections[TowerCol.name].objects.unlink(object)   
        
                     
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ObjectCursorArray.bl_idname)

# store keymaps here to access after registration
addon_keymaps = []

classes = (
    MySettings,
    PanelMain,
    PanelBase)
    
def register():
    bpy.utils.register_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    """
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        kmi = km.keymap_items.new(ObjectCursorArray.bl_idname, 'T', 'PRESS', ctrl=True, shift=True)
        kmi.properties.boxheight = 3
        addon_keymaps.append((km, kmi))
    """
    for cls in classes:
        bpy.utils.register_class(cls)        
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)

    bpy.utils.register_class(PanelSpire)

def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    bpy.utils.unregister_class(PanelMain)
    bpy.utils.unregister_class(PanelSpire)
    # handle the keymap
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()
