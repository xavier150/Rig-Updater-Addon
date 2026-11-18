# Rig-Updater-Addon

A Blender addon that updates animation actions and mesh skin weights for a new
rig version, helping maintain compatibility with older rigs.
Initially created for [MMVS video game](https://github.com/xavier150/MMVS) rigs.

In the 3D View sidebar, open **Rig Updater > Config**:

Here you will be able to setup Json configuration to define how the addon updates rigs and mesh skin weights.
You can found example json files in the `examples` folder of this repository.

In **Rig Updater > Actions**, you will find buttons to update the meshes skin weights and animation actions for backward compatibility.

You have two buttons:
- The `Update Mesh Skin Weight Backward Compatibility` to update the weights of the meshes of an armature.
<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/skin/update_mesh_skin_weight_result.webp" alt="Update Mesh Skin Weight Result" width="auto" height="200">

- And the `Update Rig Backward Compatibility` to update the animation actions for an armature.

In **Rig Updater > Check**, you will find options to do checks and find potential issues with the current rig and mesh skin weights.

## Configuration Json.

Weight mesh configuration used to update the skinning of mesh objects:
```json
{
  "update_tasks": [
    {
      "description": "Update hand weights.",
      "replace_operations": [
        {"old": ["Hand_L"], "new": "hand_l", "remove_if_already_exists": true},
        {"old": ["Index_00_L"], "new": "index_metacarpal_l", "remove_if_already_exists": true},
        {"old": ["Index_01_L"], "new": "index_01_l", "remove_if_already_exists": true},
        {"old": ["Index_02_L"], "new": "index_02_l", "remove_if_already_exists": true},
        {"old": ["Index_03_L"], "new": "index_03_l", "remove_if_already_exists": true},
        {"old": ["Index_04_L"], "new": "index_claw_l", "remove_if_already_exists": true}
      ],
      "remove_operations": []
    }
  ]
}

```

Rig controller configuration used to update the blender actions:

```json
{
  "update_tasks": [
    {
      "description": "Update hand controllers.",
      "replace_operations": [
        {"old": ["c_Hand_L"], "new": "c_hand_l", "remove_if_already_exists": true},
        {"old": ["c_Index_00_L"], "new": "c_index_metacarpal_l", "remove_if_already_exists": true},
        {"old": ["c_Index_01_L"], "new": "c_index_01_l", "remove_if_already_exists": true},
        {"old": ["c_Index_02_L"], "new": "c_index_02_l", "remove_if_already_exists": true},
        {"old": ["c_Index_03_L"], "new": "c_index_03_l", "remove_if_already_exists": true},
        {"old": ["c_Index_04_L"], "new": "c_index_claw_l", "remove_if_already_exists": true}
      ],
      "remove_operations": []
    }
  ]
}

```



## Additional Notes

You can join my Discord server for more information or if you need help.  

Discord [<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/socials/discord_symbol_blurple.png" alt="Discord Icon" width="auto" height="12">](https://discord.gg/XuYeGCFtxa) ->
[BleuRaven side projects](https://discord.gg/XuYeGCFtxa)  