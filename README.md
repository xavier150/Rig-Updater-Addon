# Rig-Updater-Addon
A Blender addon to update animations and scene with a new rig version. Initialy created for MMVS game dev.

In the 3D View sidebar, open **Rig Updater > Actions**:

- **Update Rig Backward Compatibility** updates local animation actions using the
  original rig's controller and property mappings; linked actions are skipped.
- **Update Mesh Skin Weight Backward Compatibility** updates vertex groups on
  selected mesh objects.

The `neck_rotation` and `jaw_rotation` settings in `auto_rig_updater/config.py`
are reserved and empty for now. No rotation curves are inverted.
