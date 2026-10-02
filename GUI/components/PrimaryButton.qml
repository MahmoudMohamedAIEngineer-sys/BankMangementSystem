import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: control
    implicitHeight: 42
    font.pixelSize: 14
    font.bold: true
    contentItem: Text {
        text: control.text
        color: "white"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
    background: Rectangle {
        radius: 9
        color: control.down ? "#1d4ed8" : (control.hovered ? "#2563eb" : "#173b67")
        opacity: control.enabled ? 1.0 : 0.5
    }
}
