# Rig-Updater-Addon

A Blender addon that updates animation actions and mesh skin weights for a new
rig version, helping maintain compatibility with older rigs.

> **Note:** The migration rules are currently hardcoded for rigs developed for
> the [MMVS video game](https://github.com/xavier150/MMVS). They are not yet
> configurable for other rigs.

In the 3D View sidebar, open **Rig Updater > Config**:

Here you will be able to setup Json configuration to define how the addon updates rigs and mesh skin weights.
You can found example json files in the `examples` folder of this repository.

In **Rig Updater > Actions**, you will find buttons to update the meshes skin weights and animation actions for backward compatibility.

In **Rig Updater > Check**, you will find options to do checks and find potential issues with the current rig and mesh skin weights.

## Configuration Json.

Weight mesh configuration used to update the skinning of mesh objects:
```json
{
  "update_tasks": [
    {
      "replace_operations": [
        {"description": "Rename Hand_L", "old_data_path_substrings": ["Hand_L"], "new_data_path_substring": "hand_l", "remove_if_already_exists": true},
        {"description": "Rename Index_00_L", "old_data_path_substrings": ["Index_00_L"], "new_data_path_substring": "index_metacarpal_l", "remove_if_already_exists": true},
        {"description": "Rename Index_01_L", "old_data_path_substrings": ["Index_01_L"], "new_data_path_substring": "index_01_l", "remove_if_already_exists": true},
        {"description": "Rename Index_02_L", "old_data_path_substrings": ["Index_02_L"], "new_data_path_substring": "index_02_l", "remove_if_already_exists": true},
        {"description": "Rename Index_03_L", "old_data_path_substrings": ["Index_03_L"], "new_data_path_substring": "index_03_l", "remove_if_already_exists": true},
        {"description": "Rename Index_04_L", "old_data_path_substrings": ["Index_04_L"], "new_data_path_substring": "index_claw_l", "remove_if_already_exists": true},
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
      "replace_operations": [
        {"description": "Rename c_Hand_L", "old_data_path_substrings": ["pose.bones[\"c_Hand_L\"]"], "new_data_path_substring": "pose.bones[\"c_hand_l\"]", "remove_if_already_exists": true},
        {"description": "Rename c_Index_00_L", "old_data_path_substrings": ["pose.bones[\"c_Index_00_L\"]"], "new_data_path_substring": "pose.bones[\"c_index_metacarpal_l\"]", "remove_if_already_exists": true},
        {"description": "Rename c_Index_01_L", "old_data_path_substrings": ["pose.bones[\"c_Index_01_L\"]"], "new_data_path_substring": "pose.bones[\"c_index_01_l\"]", "remove_if_already_exists": true},
        {"description": "Rename c_Index_02_L", "old_data_path_substrings": ["pose.bones[\"c_Index_02_L\"]"], "new_data_path_substring": "pose.bones[\"c_index_02_l\"]", "remove_if_already_exists": true},
        {"description": "Rename c_Index_03_L", "old_data_path_substrings": ["pose.bones[\"c_Index_03_L\"]"], "new_data_path_substring": "pose.bones[\"c_index_03_l\"]", "remove_if_already_exists": true},
        {"description": "Rename c_Index_04_L", "old_data_path_substrings": ["pose.bones[\"c_Index_04_L\"]"], "new_data_path_substring": "pose.bones[\"c_index_claw_l\"]", "remove_if_already_exists": true},
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