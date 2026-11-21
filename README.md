# Rig-Updater-Addon

A Blender addon that updates animation actions and mesh skin weights for a new
rig version, helping maintain compatibility with older rigs.
Initially created for [MMVS video game](https://github.com/xavier150/MMVS) rigs.

In the 3D View sidebar, open **Rig Updater > Config**:

Here you will be able to setup Json configuration to define how the addon updates rigs and mesh skin weights.
You can found example json files in the `examples` folder of this repository.

Relative JSON paths (`//...`) on linked armatures or inherited by library overrides
are resolved from the source library's `.blend` file. Paths changed locally on an
override are resolved from the current `.blend` file.

In **Rig Updater > Actions**, you will find buttons to update scene libraries,
scene unit scale, mesh skin weights and animation actions for backward compatibility.

- The `Update Scene Libraries` button relocates linked `.blend` libraries using the scene rules.
- The `Update Scene Scale` button updates the scene unit scale and optionally rescales object positions, animation location channels, rig data and viewport settings.
- The `Update Mesh Weights` button updates the weights of an armature's meshes.
<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/skin/update_mesh_skin_weight_result.webp" alt="Update Mesh Skin Weight Result" width="auto" height="80%">

- The `Update Actions` button updates animation actions for an armature.

In **Rig Updater > Check**, you can check mesh weights and action channels.
**Check Meshes Weights (Active)** and **Check Action (Active)** check the active
armature. **Check Meshes Weights (All)** and **Check Actions (All)** check every
armature in the scene. Results are listed in the system console.

## Configuration Json.

Set **Scene Rules JSON** in Config to use the scene rules example in `examples`.

```json
{
  "scene_rescale_rules": {
    "target_unit_scale": 1.0,
    "scale_object_position": true,
    "scale_animation_location_channels": true,
    "scale_rig": false,
    "scale_user_view": true
  },
  "libraries_update_rules": {
    "update_tasks": [
      {
        "description": "Update rig library from v3 and v4 to v5.",
        "old": ["//rig_v3.blend", "//rig_v4.blend"],
        "new": "//rig_v5.blend"
      }
    ]
  }
}
```

The four rescale options are required booleans; set them to `false` to change only
the unit scale. Enabled data is multiplied by the old unit scale divided by the
target unit scale. Object positions and rig data are limited to the current scene;
animation location channels are updated in all actions in the file. Object scale
is unchanged.
`scale_user_view` rescales the pivot and viewing distance outside camera view,
plus the clipping start/end distances, in all saved 3D viewports, including quad views.
It does not move camera objects.

Library paths identify `.blend` files. Blender handles data-blocks missing from
the destination during relocation; potential missing data is reported in the
system console. Library updates affect the whole Blender file.
After each relocation, Make Library Override is run again on objects that were
already editable overrides of that library. System overrides are not explicitly targeted.
If Blender does not allow refreshing an override, the library remains relocated
and a warning is reported.
Libraries referenced by another linked library must be updated in their parent file.

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
      "action_search": "revelant_actions",
      "remove_starting_channel_operations": [
        {"starts_with": ["pose.bones[\"rp_", "pose.bones[\"rlp_"]}
      ],
      "replace_channel_operations": [
        {"old": ["pose.bones[\"Ik_Hand_L\"][\"IkBlend\"]"], "new": "pose.bones[\"ik_hand_l\"][\"ik_blend\"]", "conflit_resolution": "remove_old"}
      ],
      "remove_channel_operations": [
        {"old": ["pose.bones[\"Ik_Hand_L\"][\"old_property\"]"]}
      ],
      "replace_bone_operations": [
        {"old": ["c_Hand_L"], "new": "c_hand_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Index_00_L"], "new": "c_index_metacarpal_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Index_01_L"], "new": "c_index_01_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Index_02_L"], "new": "c_index_02_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Index_03_L"], "new": "c_index_03_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Index_04_L"], "new": "c_index_claw_l", "conflit_resolution": "remove_old"}
      ],
      "remove_bone_operations": [
        {"old": ["c_Layer_Body"]}
      ]
    }
  ]
}

```

Operations are applied in the order their sections appear in the JSON. It is
recommended to place `replace_channel_operations` before `replace_bone_operations`
so channel paths still match the old bone names. Channel operations match full
data paths, while bone operations apply to all channels of the named bone.
`remove_starting_channel_operations` removes channels whose full data path starts
with any prefix in the non-empty `starts_with` list; the match is case-sensitive.

Each rig update task must select its actions with `action_search`:

- `all_actions`: all actions in the file (`all_action` is also accepted).
- `used_actions`: the armature's active action and actions in its NLA strips.
- `revelant_actions`: local actions with matching bones and action slots.

Updates apply each task only to its selected local actions; checks inspect the
union of selected local actions.

Checks resolve channels against the target armature or its armature data without
changing the actions. Slots targeting other data types are reported as skipped.

For action updates, `conflit_resolution` controls what happens when the new
channel already exists for the same array index and slot:

- `keep_both`: leave both channels unchanged.
- `remove_old`: remove the old channel and keep the new channel.
- `remove_new`: remove the new channel and replace it with the old channel's values.


## Additional Notes

You can join my Discord server for more information or if you need help.  

Discord [<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/socials/discord_symbol_blurple.png" alt="Discord Icon" width="auto" height="12">](https://discord.gg/XuYeGCFtxa) ->
[BleuRaven side projects](https://discord.gg/XuYeGCFtxa)  