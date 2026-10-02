import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: control
    implicitHeight: 38
    font.pixelSize: 13
    contentItem: Text {
        text: control.text
        color: "#173b67"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
    background: Rectangle {
        radius: 8
        color: control.down ? "#dbeafe" : (control.hovered ? "#eff6ff" : "white")
        border.color: "#bfd3ec"
        opacity: control.enabled ? 1.0 : 0.5
    }
}
