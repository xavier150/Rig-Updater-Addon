# Rig-Updater-Addon

A Blender addon that manages rig backward compatibility by updating scenes, animation actions, and meshes skin weights.
This addon was initially created for [MMVS video game](https://github.com/xavier150/MMVS).

-------------

# How it Works
Create three JSON configuration files for the new rig:

- **Deform**: rules for deform bones and mesh weights.
- **Rig**: rules for animation controllers and channels.
- **Scene**: rules for scene scale and linked libraries.

Choose the files in **3D View > Sidebar > Rig Updater > Config**, then run the
updates from **Rig Updater > Actions**.

# Features

## Animation Update
Update animation channels using the Rig JSON rules.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/animations/update_action_result.webp" alt="Update Action Result" width="auto" height="80%">

- `Update Actions (Active)` updates configured actions for the active armature.
- `Update Actions (All)` updates configured actions for every armature in the scene.

## Weights Update
Update mesh weights using the Deform JSON rules.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/skin/update_mesh_skin_weight_result.webp" alt="Update Mesh Skin Weight Result" width="auto" height="80%">

- `Update Weights (Auto)` updates mesh descendants of the target armature.
- `Update Weight (Select)` updates selected meshes, parented or not, using the active armature's Mesh Weights JSON.

## Libraries Update
Update scene libraries using the Scene JSON rules.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/libraries/update_scene_libraries_result.webp" alt="Update Scene Libraries Result" width="auto" height="80%">

- `Update Scene Libraries` reloads libraries or relinks collections. Relinking can
  preserve animation and local constraints, and uses the new rig's JSON files to update constraint bone names.

## Scene Scale
Set the scene unit scale and optionally rescale related data using the Scene JSON rules.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/scene/update_scene_scale_result.webp" alt="Update Scene Scale Result" width="auto" height="80%">

- `Update Scene Scale` changes the unit scale and applies the enabled rescale options.

**Example:** FBX workflows often use a unit scale of `0.01`, while glTF uses `1.0`.

## Checks Actions
Check action related to an armature and display the results in the system console.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/animations/check_action_result.webp" alt="Check Action Result" width="auto" height="80%">

- `Check Actions (Active)` checks actions for the active armature.
- `Check Actions (All)` checks actions for every armature in the scene.

## Checks Weights
Check meshes weights related to an armature and display the results in the system console.

<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/skin/check_weights_result.webp" alt="Check Weights Result" width="auto" height="80%">

- `Check Meshes Weights (Active)` checks mesh weights for the active armature.
- `Check Meshes Weights (All)` checks mesh weights for every armature in the scene.

## Tools

In **3D View > Sidebar > Rig Updater > Tools > Preview**, use
`Action Search (Active)` for the active armature or `Action Search (All)` for
every armature in the scene. The buttons print the local actions selected by each
`action_search` mode to Blender's system console. They do not change actions and
do not require a JSON configuration.

# Configuration JSON

For linked armatures and inherited overrides, relative paths (`//...`) resolve
from the source library. Locally changed override paths resolve from the current
`.blend` file.

## Scene Rules JSON

The file requires `scene_rescale_rules` and `libraries_update_rules`.

### Scene scale

| Parameter | Values | Description |
|---|---|---|
| `target_unit_scale` | Number in Blender's supported range (required) | Target unit scale. |
| `scale_object_position` | `true` / `false` (required) | Scale location and size of local root objects in the scene. |
| `scale_animation_location_channels` | `true` / `false` (required) | Scale location curves in local actions; linked actions are skipped. |
| `scale_rig` | `true` / `false` (required) | Scale rig data on objects in the scene. |
| `scale_user_view` | `true` / `false` (required) | Scale non-camera view distance and viewport clipping. |
| `scale_constraints` | `true` / `false` (default `true`) | Scale local Child Of constraint offsets. |

Enabled data is multiplied by `old scale / target scale`. Set all options to
`false` to change only the unit scale. Object scaling skips linked objects;
constraint scaling also skips inherited constraints.

### Library updates

Include one or more task arrays in `libraries_update_rules`.

| Parameter | Values | Description |
|---|---|---|
| `reload_tasks` | Array of tasks (optional) | Reload libraries and refresh editable overrides. |
| `collection_relink_tasks` | Array of tasks (optional) | Replace collections and automatically migrate renamed armatures. |
| `proxy_update_to_collection_tasks` | Array of tasks (optional; legacy) | Backward-compatible proxy tasks; prefer `collection_relink_tasks`. |
| `description` | String (required) | Short note for the task. |
| `old` | Array of `.blend` paths (required) | Source libraries to update. |
| `new` | `.blend` path (required) | Destination library. |
| `old_collection`, `new_collection` | Collection names (required for relink/proxy tasks) | Collections to replace and use. |
| `path_type` | `as_before`, `relative`, `absolute` (optional; default `absolute` for reloads and `as_before` for relink/proxy tasks) | How to store the destination path. |
| `object_scale_multipliers` | Object name: positive finite number (relink/proxy only; optional) | Multiply local scale after relinking. |
| `object_location_multipliers` | Object name: positive finite number (relink/proxy only; optional) | Multiply local location after relinking. |
| `scripts_to_run_on_update` | Array of `.py` paths (relink/proxy only; optional) | Run trusted Python scripts on each updated local armature after relinking. Paths are relative to the Scene Rules JSON file or absolute. Each script must define `run(armature)`. |

- Back up first. Relink/proxy tasks require Blender 3.5+; convert instances and legacy proxies to overrides first.
- Update scripts execute Python code in Blender. Only reference scripts you trust; a missing script or a script without `run(armature)` stops the update.
- Relinks preserve animation, including actionless NLA clips, root transforms and local constraints. Old local drivers are discarded; unsupported complex NLA still blocks the relink.
- Relinks remove unused overrides of replaced libraries and their unused linked data; overrides with surviving users or fake users are retained. When an orphan occupied its linked object's name, a matching numbered override can recover that name. Other orphaned data is not purged.
- When a local armature's linked name is absent from the destination, the updater maps it to the single unmatched destination armature. Ambiguous mappings stop the update. The replacement uses the destination rig's drivers and bone constraints.
- Relative paths require a saved file and the same drive. Update nested libraries in their parent file.
- `Update Actions` migrates bone/channel names; relinks only restore action/NLA assignments. Do not target the same collection twice; all replacements are preflighted.

Example:

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
        "description": "Reload a library",
        "old": ["OldLib.blend"],
        "new": "NewLib.blend",
        "path_type": "relative"
      }
    ],
    "collection_relink_tasks": [
      {
        "description": "Relink a collection",
        "old": ["OldRigCollection.blend"],
        "new": "NewRigCollection.blend",
        "path_type": "as_before",
        "old_collection": "OldRigCollection",
        "new_collection": "NewRigCollection",
        "object_scale_multipliers": {
          "NewRig": 100.0
        }
      },
      {
        "description": "Replace a legacy proxy",
        "old": ["OldRigProxy.blend"],
        "new": "NewRigCollection.blend",
        "path_type": "as_before",
        "old_collection": "OldRigProxyCollection",
        "new_collection": "NewRigCollection"
      }
    ]
  }
}
```

## Mesh Weights JSON

The file requires an `update_tasks` array. Each task needs a `description` and
at least one operations list.

| Parameter | Values | Description |
|---|---|---|
| `description` | String (required) | Short note for the task. |
| `replace_operations` | Array (optional) of `{old: [names], new: name, conflit_resolution: value}` | Rename or combine vertex groups. |
| `remove_operations` | Array (optional) of `{old: [names]}` | Remove named groups. |
| `remove_starting_operations` | Array (optional) of `{starts_with: [prefixes]}` | Remove groups by name prefix. |

`conflit_resolution` values:

| Value | Description |
|---|---|
| `keep_both` | Keep both groups. |
| `remove_old` | Keep the destination group and remove the old group. |
| `remove_new` | Replace the destination group with the old group's weights. |
| `merge` | Add weights per vertex (up to `1.0`) and remove the old group. |

Example:

```json
{
  "update_tasks": [
    {
      "description": "Remove position bone that should not be included in meshes weights",
      "remove_starting_operations": [
        {"starts_with": ["pos_", "Pos_"]}
      ]
    },
    {
      "description": "Update left-hand weights.",
      "replace_operations": [
        {"old": ["Hand_L"], "new": "hand_l", "conflit_resolution": "merge"},
        {"old": ["Index_00_L"], "new": "index_metacarpal_l", "conflit_resolution": "merge"},
        {"old": ["Index_01_L"], "new": "index_01_l", "conflit_resolution": "merge"},
        {"old": ["Index_02_L"], "new": "index_02_l", "conflit_resolution": "merge"},
        {"old": ["Index_03_L"], "new": "index_03_l", "conflit_resolution": "merge"},
        {"old": ["Index_04_L"], "new": "index_claw_l", "conflit_resolution": "merge"}
      ],
      "remove_operations": [
        {"old": ["old_bone"]}
      ]
    }
  ]
}
```

If the destination group does not exist, it is created from the old group.
Tasks run in order: replacements, exact removals, then prefix removals. Prefix
matching is case-sensitive.

## Rig Controllers JSON

The file requires an `update_tasks` array. Each task needs a `description` and
an `action_search` value.

| Parameter | Values | Description |
|---|---|---|
| `description` | String (required) | Short note for the task. |
| `action_search` | `all_actions`, `used_actions`, `revelant_actions`, `revelant_and_used_actions` (required) | Select actions to update or check. `all_action` is also accepted. |
| `replace_channel_operations` | Array (optional) of `{old: [paths], new: path, conflit_resolution: value}` | Replace full animation data paths. |
| `remove_channel_operations` | Array (optional) of `{old: [paths]}` | Remove full animation data paths. |
| `replace_bone_operations` | Array (optional) of `{old: [names], new: name, conflit_resolution: value}` | Rename bones and their animation channels. |
| `remove_bone_operations` | Array (optional) of `{old: [names]}` | Remove channels for named bones. |
| `remove_starting_channel_operations` | Array (optional) of `{starts_with: [prefixes]}` | Remove channels by data-path prefix. |
| `remove_deform_bones` | `true` / `false` (optional; default `false`) | Remove channels for deform bones on the target armature. |

`action_search` options:

| Value | Description |
|---|---|
| `all_actions` | All local actions in the file. |
| `used_actions` | The armature's active action and NLA actions. |
| `revelant_actions` | Local actions with matching armature bones and slots. |
| `revelant_and_used_actions` | Union of relevant and used local actions, without duplicates. |

Updates apply each task to its selected local actions; checks inspect their
union.
For action conflicts, `conflit_resolution` accepts:

| Value | Description |
|---|---|
| `keep_both` | Keep both channels. |
| `remove_old` | Keep the destination channel and remove the old one. |
| `remove_new` | Replace the destination channel with the old channel's values. |

Example:

```json
{
  "update_tasks": [
    {
      "description": "Remove animation channels for internal bones.",
      "action_search": "revelant_actions",
      "remove_starting_channel_operations": [
        {"starts_with": ["pose.bones[\"rp_"]},
        {"starts_with": ["pose.bones[\"rlp_"]}
      ]
    },
    {
      "description": "Remove all deform bones that should not be animated. (Switch to true if your seperate deform bones from control bones)",
      "action_search": "revelant_actions",
      "remove_deform_bones": false
    },
    {
      "description": "Update left-hand controllers.",
      "action_search": "revelant_actions",
      "replace_channel_operations": [
        {"old": ["pose.bones[\"Ik_Hand_L\"][\"IkBlend\"]"], "new": "pose.bones[\"ik_hand_l\"][\"ik_blend\"]", "conflit_resolution": "remove_old"}
      ],
      "remove_channel_operations": [
        {"old": ["pose.bones[\"Ik_Hand_L\"][\"old_property\"]"]}
      ],
      "replace_bone_operations": [
        {"old": ["Ik_Hand_L"], "new": "ik_hand_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Hand_L"], "new": "c_hand_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Index_00_L"], "new": "c_index_metacarpal_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Index_01_L"], "new": "c_index_01_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Index_02_L"], "new": "c_index_02_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Index_03_L"], "new": "c_index_03_l", "conflit_resolution": "remove_old"},
        {"old": ["c_Index_04_L"], "new": "c_index_claw_l", "conflit_resolution": "remove_old"}
      ],
      "remove_bone_operations": [
        {"old": ["c_old_bone"]}
      ]
    }
  ]
}
```

Sections run in JSON order. Put channel replacements before bone replacements
when paths use old bone names. Checks do not modify actions; slots for other
data types are reported as skipped.


## Additional Notes

You can join my Discord server for more information or if you need help.  

Discord [<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/socials/discord_symbol_blurple.png" alt="Discord Icon" width="auto" height="12">](https://discord.gg/XuYeGCFtxa) ->
[BleuRaven side projects](https://discord.gg/XuYeGCFtxa)  