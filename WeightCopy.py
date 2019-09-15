bl_info = {
    'name': 'Vertices Weights Tool',
    'category': 'All'
}

import bpy
import os
import bmesh

shouldLog = True
copyData = []

class VertexData:
    def __init__(self):
        self.bonesWeight = {}

class MeshUtils:

    @staticmethod
    def getSelectedHistory():
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)
        selectedHistory = []
        for elem in bm.select_history:
            selectedHistory.append(elem.index)
        return selectedHistory

class ListUtils:

    @staticmethod
    def safeGet(index, list):
        if index < 0:
            return None
        if index >= len(list):
            return None
        return list[index]

class Logger:

    @staticmethod
    def log(str):
        if not shouldLog:
            return
        print(str)

class CopyVerticesWeights(bpy.types.Operator):
    bl_idname = 'mesh.copy_vertices_weights'
    bl_label = 'Copy Selected Vertices Weights'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        Logger.log("Copying ----------------------")

        activeObj = bpy.context.active_object

        selectedHistory = MeshUtils.getSelectedHistory()

        copyData.clear()

        for vertIndex in selectedHistory:
            mv = activeObj.data.vertices[vertIndex]
            vData = VertexData()
            for g in mv.groups:
                boneName = activeObj.vertex_groups[g.group].name
                vData.bonesWeight[boneName] = g.weight
            copyData.append(vData)

        for data in copyData:
            Logger.log(data.bonesWeight)

        Logger.log("Copy done ----------------------")
        
        return { "FINISHED" }

class PasteVerticesWeights(bpy.types.Operator):
    bl_idname = 'mesh.paste_vertices_weights'
    bl_label = 'Paste Selected Vertices Weights'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        Logger.log("Pasting ----------------------")

        activeObj = bpy.context.active_object
        obj = bpy.ops.object
        mode = bpy.context.object.mode
        selectedHistory = MeshUtils.getSelectedHistory()

        obj.mode_set(mode='OBJECT')

        for i, vertIndex in enumerate(selectedHistory):
            copyVertexData = ListUtils.safeGet(i, copyData)
            if copyVertexData is None:
                continue
            for boneName, boneWeight in copyVertexData.bonesWeight.items():
                vg = activeObj.vertex_groups.get(boneName)
                if vg is None:
                    continue
                vg.add([vertIndex], float(boneWeight), "REPLACE")
                Logger.log('Replaced bone(%s) vertex(%d) with weight(%6.6f)'%(boneName, vertIndex, boneWeight))

        obj.mode_set(mode=mode)
        Logger.log("Paste done ----------------------")
        return { "FINISHED" }

class PanelUI(bpy.types.Panel):
    bl_idname = "panel"
    bl_label = "Vertices Weights Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "edit_mesh"

    @classmethod
    def poll(cls, context):
        return context.mode in {'EDIT_MESH'}
 
    def draw(self, context):
        row = self.layout.row(align = True)
        row.operator("mesh.copy_vertices_weights", text = "Copy")
        row.operator("mesh.paste_vertices_weights", text = "Paste")

def register() :
    bpy.utils.register_class(CopyVerticesWeights)
    bpy.utils.register_class(PasteVerticesWeights)
    bpy.utils.register_class(PanelUI)
 
def unregister() :
    bpy.utils.unregister_class(CopyVerticesWeights)
    bpy.utils.unregister_class(PasteVerticesWeights)
    bpy.utils.unregister_class(PanelUI)
 
if __name__ == "__main__" :
    register()