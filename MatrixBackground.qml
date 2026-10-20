import QtQuick
import Quickshell
import Quickshell.Wayland

Item {
  id: root
  property bool active: true

  Variants {
    model: Quickshell.screens

    PanelWindow {
      id: panel
      required property var modelData
      screen: modelData
      anchors { top: true; bottom: true; left: true; right: true }
      visible: root.active
      color: "black"
      WlrLayershell.namespace: "matrix-rain-wallpaper"
      WlrLayershell.layer: WlrLayer.Bottom
      WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
      exclusionMode: ExclusionMode.Ignore
      mask: Region {}

      MatrixRain {
        anchors.fill: parent
        dpr: panel.modelData.devicePixelRatio
        running: panel.visible
        onRunningChanged: if (running) restart()
      }
    }
  }
}
