# Rig-Updater-Addon

A Blender addon that updates animation actions and mesh skin weights for a new
rig version, helping maintain compatibility with older rigs.

> **Note:** The migration rules are currently hardcoded for rigs developed for
> the [MMVS video game](https://github.com/xavier150/MMVS). They are not yet
> configurable for other rigs.

In the 3D View sidebar, open **Rig Updater > Actions**:

- **Update Rig Backward Compatibility** updates local animation actions using the
  original rig's controller and property mappings; linked actions are skipped.
- **Update Mesh Skin Weight Backward Compatibility** updates vertex groups on
  selected mesh objects.

The `neck_rotation` and `jaw_rotation` settings in `auto_rig_updater/config.py`
are reserved and empty for now. No rotation curves are inverted.

## Additional Notes

You can join my Discord server for more information or if you need help.  

Discord [<img src="https://github.com/xavier150/Rig-Updater-Addon/wiki/images/socials/discord_symbol_blurple.png" alt="Discord Icon" width="auto" height="12">](https://discord.gg/XuYeGCFtxa) ->
[BleuRaven side projects](https://discord.gg/XuYeGCFtxa)  