# lfdata_ui

The lfdata_ui tool is a UI to load, save, and edit config files,
and to invoke the lfdata tool. lfdata_ui is platform independent.

# UI

The screen is divided into three parts:

*   Top left: Screen layout arrangement. This is a canvas where the user can drag and drop
    the UI elements. UI elements are shown as rectangles with their name in the center.
    The user can drag and drop them to move them, or drag and drop the bottom right corner
    to resize them.
*   Top right: UI element properties. These are edit fields that allow changing the values
    of the selected UI element. These include:
    *   Anchor point coordinates
    *   Size
    *   Alignment
    *   Enabled (on/off)
    *   Font
    *   Font size
    *   Visible - start time in ms
    *   Visible - end time in ms
    *   Fade in time in ms
    *   Fade out time in ms
    *   Formatted text
*   Bottom left: The rendered image. This view has a slider to navigate through the game time,
    and a dropdown selector to pick the name for the player on the video (or none).
    Underneath that is the actual rendered image. It is created by invoking the `lfdata`
    executable.
*   Bottom right: Global settings:
    *   A button to load a TDF file. This will pick a file open dialog to pick a TDF file.
    *   Video FPS
    *   Video width and height
    *   A list of all available UI elements. Clicking on one will select it and highlight it in
        the screen layout view, and show its values in the UI element properties view.
    *   A button to generate the video. This will open a file save dialog that picks the target
        file name and allows picking a selected extension (.webm, .mov, .mp4).

There is also a menu on the top. It has a "File" menu which has an "Open Configuration File"
and "Save Configuration File" option.

