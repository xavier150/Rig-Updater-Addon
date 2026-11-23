# Rig-Updater-Addon

A Blender addon that manages rig backward compatibility by updating scenes, animation actions, and meshes skin weights.
This addon was initially created for [MMVS video game](https://github.com/xavier150/MMVS).

-------------

# How it Works
Once you create a new rig version with many changes, this addon helps you update related data to the new rig version for backward compatibility.
Create three JSON configuration files:

- **Deform**: rules for deform bones and mesh weights.
- **Rig**: rules for animation controllers and channels.
- **Scene**: rules for scene scale and linked libraries.

Use **Rig Updater > Actions** to apply the rules.

# Features

## Animation Update
You can update animations by updating the channels according to the rules defined in your Rig JSON configuration.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/animations/update_action_result.webp" alt="Update Action Result" width="auto" height="80%">

- `Update Actions (Active)` updates all action related to the active armature.
- `Update Actions (All)` updates all actions related to all armatures in the scene.

## Weights Update
You can update the weights data of meshes using the rules defined in your Deform JSON configuration.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/skin/update_mesh_skin_weight_result.webp" alt="Update Mesh Skin Weight Result" width="auto" height="80%">

- `Update Weights (Auto)` updates mesh descendants of the target armature.
- `Update Weight (Select)` updates selected meshes, parented or not, using the active armature's Mesh Weights JSON.

## Libraries Update
You can update scene libraries using the rules defined in your Scene JSON configuration.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/libraries/update_scene_libraries_result.webp" alt="Update Scene Libraries Result" width="auto" height="80%">

- `Update Scene Libraries` updates all scene libraries according to the scene rules config.
You can specify the collection to use and action specific to the relinking like object rescale or transforms adjustments.
It also keep the animation data including NLA tracks and keep all the constraints with the updated bones. 
For the constraints it uses the Rig JSON configuration from the new armature from the updated library.

## Scene rescale
You can update the scene scale according to the rules defined in your Scene JSON configuration.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/scene/update_scene_scale_result.webp" alt="Update Scene Scale Result" width="auto" height="80%">

- `Update Scene Scale` updates the scene unit scale and optionally rescales object positions, animation location channels, rig data, constraints, and viewport settings according to the scene rescale rules.

This is mainly useful with Unreal Engine pipeline when you switch from FBX to glTF file formats to export assets:
- FBX with Blender requires to use unit scale at 0.01.
- glTF fix that requirement and uses unit scale at 1.0.

You can now set the target unit scale to 1.0 and update the scene accordingly to match the glTF export requirements.

## Checks Actions
Check action related to an armature and display the results in the system console.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/animations/check_action_result.webp" alt="Check Action Result" width="auto" height="80%">

## Checks Weights
Check meshes weights related to an armature and display the results in the system console.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/skin/check_weights_result.webp" alt="Check Weights Result" width="auto" height="80%">

# Configuration JSON

Choose the files in **3D View > Sidebar > Rig Updater > Config**. Examples are in
the `examples` folder. Relative paths (`//...`) on linked armatures and inherited
overrides resolve from the source library; locally changed override paths resolve
from the current `.blend` file.

Set **Scene Rules JSON** in Config to use the scene rules example in `examples`.

```json
{
  "scene_rescale_rules": {
    "target_unit_scale": 1.0,
    "scale_object_position": true,
    "scale_animation_location_channels": true,
    "scale_rig": false,
    "scale_user_view": true,
    "scale_constraints": true
  },
  "libraries_update_rules": {
    "reload_tasks": [
      {
        "description": "Update scenes from v3 and v4 to v5.",
        "old": ["//scene_v3.blend", "//scene_v4.blend"],
        "new": "//scene_v5.blend"
      }
    ],
    "collection_relink_tasks": [
      {
        "description": "Update rig library from v3 and v4 to v5.",
        "old": ["//rig_v3.blend", "//rig_v4.blend"],
        "new": "//rig_v5.blend",
        "path_type": "as_before",
        "old_collection": "my_rig_collection",
        "new_collection": "my_rig_collection"
      }
    ]
  }
}
```

The four original rescale options are required booleans. `scale_constraints` is
an optional boolean, defaulting to `true` when omitted; set all options to `false` to change only
the unit scale. Enabled data is multiplied by the old unit scale divided by the
target unit scale. `scale_object_position` scales position and object scale only
on local root objects (objects without a parent) in the current scene, including
library overrides and ordinary objects such as a Cube. Children follow their
parent without changing their local transforms; directly linked objects are not rescaled.
Rig data is limited to the current scene; animation location channels are updated
in all actions in the file.
`scale_constraints` rescales the inverse matrix translation of local Child Of
constraints on objects and pose bones in the scene, including constraints added
locally to library overrides. Linked objects and inherited override constraints
are not changed. This option is independent of `scale_rig`.
`scale_user_view` rescales the pivot and viewing distance outside camera view,
plus the clipping start/end distances, in all saved 3D viewports, including quad views.
It does not move camera objects.

`reload_tasks` relocates libraries and refreshes existing editable object overrides.
`collection_relink_tasks` replaces collection overrides, restores root override world transforms, animation
and local constraints, and uses the new rig's Rig Controllers and Mesh Weights JSON
to rename constraint owner and target bones, including targets on the same rig.
Objects or bones missing from the new collection are
skipped. Either task list may be omitted. Back up the `.blend` before relinking.
Collection relinking requires Blender 3.5 or newer. Convert collection instances
to library overrides before relinking. Local drivers,
NLA strips other than action clips, and clips with modifiers cannot currently be transferred.
Libraries referenced by another linked library must be updated in their parent file.

After collection relinking, unused linked data from the replaced libraries and
their dependencies is removed immediately. Shared dependencies still used by
another collection or library are retained; unrelated orphan data is not purged.

Optional `path_type` in each `collection_relink_tasks` entry controls the direct
destination library's stored path: `"as_before"` (the default) keeps the replaced
library's relative or absolute path type, `"relative"` stores a path relative to
the current `.blend`, and `"absolute"` stores an absolute path. Relative paths
require saving the current `.blend` first and a destination on the same drive.
Paths inside nested libraries remain
defined by those libraries.

Optional `object_scale_multipliers` and `object_location_multipliers` objects in a
relink task multiply local scale and location after relinking, for example
`"object_scale_multipliers": {"Cobble_Character": 100.0}` and
`"object_location_multipliers": {"Sub_StuckZoneProxyFloor": 0.01}`.
Names match objects in the scene containing the updated collection, inside or
outside that collection, with or without a parent or override. Each adjustment
is applied once per object per task, only if the task relinks a collection.
Missing objects are skipped; directly linked read-only objects are skipped with a warning.
Without an explicit multiplier, children retain the new library's local transforms.
Factors must be finite positive numbers. Animation keys and armature data are
unchanged; children also inherit their parent's transforms. These adjustments are
independent of `Update Scene Scale`. Animated or
constrained transforms remain controlled by their animation, drivers and constraints.

Weight mesh configuration used to update the skinning of mesh objects:
```json
{
  "update_tasks": [
    {
      "description": "Remove position bone weights.",
      "remove_starting_operations": [
        {"starts_with": ["pos_", "Pos_"]}
      ]
    },
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

`remove_starting_operations` removes vertex groups whose names start with any
prefix in the non-empty `starts_with` list. Matching is case-sensitive. Tasks
run in order; within each task, replacements run first, followed by exact
removals and then prefix removals.

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
      ],
      "remove_deform_bones": true
    }
  ]
}

```

Operations are applied in the order their sections appear in the JSON. It is
recommended to place `replace_channel_operations` before `replace_bone_operations`
so channel paths still match the old bone names. Channel operations match full
data paths, while bone operations apply to all channels of the named bone.
When a bone replacement is applied, channel groups named after the old bone are
renamed to the new bone name as well.
`remove_starting_channel_operations` removes channels whose full data path starts
with any prefix in the non-empty `starts_with` list; the match is case-sensitive.
`remove_deform_bones: true` removes action channels for every bone on the target
armature whose `use_deform` property is enabled. It requires the target armature,
just like action searches other than `all_actions`.

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