# Rig-Updater-Addon

A Blender addon that updates animation actions and mesh skin weights for a new
rig version, helping maintain compatibility with older rigs.
Initially created for [MMVS video game](https://github.com/xavier150/MMVS) rigs.

In the 3D View sidebar, open **Rig Updater > Config**:

Here you will be able to setup Json configuration to define how the addon updates rigs and mesh skin weights.
You can found example json files in the `examples` folder of this repository.

In **Rig Updater > Actions**, you will find buttons to update the meshes skin weights and animation actions for backward compatibility.

You have two buttons:
- The `Update Mesh Weights` button updates the weights of an armature's meshes.
<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/skin/update_mesh_skin_weight_result.webp" alt="Update Mesh Skin Weight Result" width="auto" height="80%">

- The `Update Actions` button updates animation actions for an armature.

In **Rig Updater > Check**, you can check mesh weights and action channels.
**Check Meshes Weights (Active)** and **Check Action (Active)** check the active
armature. **Check Meshes Weights (All)** and **Check Actions (All)** check every
armature in the scene. Results are listed in the system console.

## Configuration Json.

Weight mesh configuration used to update the skinning of mesh objects:
```json
{
  "update_tasks": [
    {
      "description": "Update hand weights.",
      "replace_operations": [
        {"old": ["Hand_L"], "new": "hand_l", "conflit_resolution": "merge"},
        {"old": ["Index_00_L"], "new": "index_metacarpal_l", "conflit_resolution": "merge"},
        {"old": ["Index_01_L"], "new": "index_01_l", "conflit_resolution": "merge"},
        {"old": ["Index_02_L"], "new": "index_02_l", "conflit_resolution": "merge"},
        {"old": ["Index_03_L"], "new": "index_03_l", "conflit_resolution": "merge"},
        {"old": ["Index_04_L"], "new": "index_claw_l", "conflit_resolution": "merge"}
      ],
      "remove_operations": [
        {"old": ["ObsoleteGroup"]}
      ]
    }
  ]
}

```

For skin weights, `conflit_resolution` controls what happens when the new
vertex group already exists:

- `keep_both`: leave both groups unchanged.
- `remove_old`: remove the old group and keep the new group.
- `remove_new`: remove the new group and replace it with the old group's weights.
- `merge`: add both groups' weights per vertex, capped at 1.0,
  and remove the old group.

If the new group does not exist, the old group is transferred to it. Multiple
names in `old` are processed in order.

Rig controller configuration used to update the blender actions:

```json
{
  "update_tasks": [
    {
      "description": "Update hand controllers.",
      "action_search": "all_actions",
      "replace_operations": [
        {"old": ["c_Hand_L"], "new": "c_hand_l", "remove_if_already_exists": true},
        {"old": ["c_Index_00_L"], "new": "c_index_metacarpal_l", "remove_if_already_exists": true},
        {"old": ["c_Index_01_L"], "new": "c_index_01_l", "remove_if_already_exists": true},
        {"old": ["c_Index_02_L"], "new": "c_index_02_l", "remove_if_already_exists": true},
        {"old": ["c_Index_03_L"], "new": "c_index_03_l", "remove_if_already_exists": true},
        {"old": ["c_Index_04_L"], "new": "c_index_claw_l", "remove_if_already_exists": true}
      ],
      "remove_operations": [
        {"old": ["c_Layer_Body"]}
      ]
    }
  ]
}

```

Each rig update task can select its actions with `action_search`:

- `all_actions`: all actions in the file (`all_action` is also accepted).
- `used_actions`: the armature's active action and actions in its NLA strips.
- `revelant_actions`: local actions with matching bones and action slots.

If omitted, `all_actions` preserves the previous behavior. Updates apply each
task only to its selected local actions, checks inspect the union of selected
actions, including linked actions.

Checks resolve channels against the target armature or its armature data without
changing the actions. Slots targeting other data types are reported as skipped.



## Additional Notes

You can join my Discord server for more information or if you need help.  

Discord [<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/socials/discord_symbol_blurple.png" alt="Discord Icon" width="auto" height="12">](https://discord.gg/XuYeGCFtxa) ->
[BleuRaven side projects](https://discord.gg/XuYeGCFtxa)  