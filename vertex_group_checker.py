import bpy
import bmesh

bl_info = {
  "name": "Vertex Group Checker",
  "author": "iruca3",
  "version": (0, 9, 1),
  "blender": (2, 80, 0),
  "location": "",
  "description": "Making easy checking used vertex group",
  "warning": "",
  "wiki_url": "https://github.com/iruca3/vertex_group_checker",
  "tracker_url": "https://twitter.com/aqua_h4ck3r5",
  "category": "Rigging"
}


#-------------------------------------------------------------------------------
# UI
#-------------------------------------------------------------------------------

class UI(bpy.types.Panel):
  bl_label = "Vertex Group Checker"
  bl_space_type = "VIEW_3D"
  bl_category = "Item"
  bl_region_type = "UI"

  def is_editing_object(self):
    return hasattr(bpy.context, "active_object") and \
           hasattr(bpy.context.active_object, "mode") and \
           bpy.context.active_object.mode == 'EDIT' and \
           bpy.context.active_object.type == 'MESH'

  def get_weight_names(self):
    if not self.is_editing_object():
      return []

    weight_names = []
    obj = bpy.context.active_object
    obj.update_from_editmode()
    if not hasattr(obj.data, "vertices"):
      return []

    vertex_groups = obj.vertex_groups
    for vert in obj.data.vertices:
      if vert.select:
        for vg in vert.groups:
          weight_names.append(vertex_groups[vg.group].name)

    return sorted(list(set(weight_names)))

  def draw(self, context):
    weight_names = self.get_weight_names()
    for name in weight_names:
      row = self.layout.row(align = False)
      row.alignment = 'LEFT'
      remove_button = row.operator("vgc.remove_weight_button")
      remove_button.target_weight_name = name
      follow_button = row.operator("vgc.follow_button")
      follow_button.target_weight_name = name
      row.label(text = name, icon = "GROUP_VERTEX")
      
    if len(weight_names) == 0:
      self.layout.label(text = "No weight found.")

  @classmethod
  def poll(self, context):
    return self.is_editing_object(self)

class RemoveWeightButton(bpy.types.Operator):
  bl_idname = "vgc.remove_weight_button"
  bl_label = "Remove"
  target_weight_name: bpy.props.StringProperty()

  def execute(self, context):
    obj = bpy.context.active_object
    obj.update_from_editmode()
    bm = bmesh.from_edit_mesh(obj.data)
    vertex_groups = obj.vertex_groups
    dflay = bm.verts.layers.deform.active
    for v in bm.verts:
      if v.select:
        for dvk, dvv in v[dflay].items():
          if obj.vertex_groups[dvk].name == self.target_weight_name:
            del v[dflay][dvk]
    return{'FINISHED'}

class FollowButton(bpy.types.Operator):
  bl_idname = "vgc.follow_button"
  bl_label = "Select"
  target_weight_name: bpy.props.StringProperty()

  def execute(self, context):
    obj = bpy.context.active_object
    obj.update_from_editmode()
    bm = bmesh.from_edit_mesh(obj.data)
    vertex_groups = obj.vertex_groups
    selected_vers = [v for v in bm.verts if v.select]
    bpy.ops.mesh.select_all(action = 'DESELECT')
    for v in selected_vers:
      vert = obj.data.vertices[v.index]
      found = False
      for vg in vert.groups:
        if vertex_groups[vg.group].name == self.target_weight_name:
          found = True
      v.select = found
    bmesh.update_edit_mesh(obj.data, True)
    bpy.context.tool_settings.mesh_select_mode[0] = True
    bpy.context.tool_settings.mesh_select_mode[0] = False

    return{'FINISHED'}

classes = (
  UI,
  RemoveWeightButton,
  FollowButton
)

def register():
  for cls in classes:
    bpy.utils.register_class(cls)

def unregister():
  for cls in classes:
    bpy.utils.unregister_class(cls)

if __name__ == "__main__":
  register()
