import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: badge
    property string status: ""
    implicitWidth: statusLabel.implicitWidth + 20
    implicitHeight: 28
    radius: 14
    color: {
        if (status === "ACTIVE") return "#dcfce7"
        if (status === "FROZEN") return "#fef3c7"
        if (status === "CLOSED") return "#fee2e2"
        return "#e2e8f0"
    }

    Label {
        id: statusLabel
        anchors.centerIn: parent
        text: badge.status
        color: {
            if (badge.status === "ACTIVE") return "#166534"
            if (badge.status === "FROZEN") return "#92400e"
            if (badge.status === "CLOSED") return "#991b1b"
            return "#475569"
        }
        font.pixelSize: 11
        font.bold: true
    }
}
