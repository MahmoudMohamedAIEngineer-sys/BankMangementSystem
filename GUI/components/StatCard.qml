import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: card
    property string title: ""
    property string value: ""
    property string accent: "#2563eb"
    implicitHeight: 116
    radius: 14
    color: "white"
    border.color: "#e2e8f0"

    Column {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 10

        Rectangle {
            width: 34
            height: 5
            radius: 3
            color: card.accent
        }

        Label {
            text: card.title
            color: "#64748b"
            font.pixelSize: 13
        }

        Label {
            text: card.value
            color: "#172b4d"
            font.pixelSize: 24
            font.bold: true
        }
    }
}
